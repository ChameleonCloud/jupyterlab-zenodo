import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import {
  ICommandPalette,
  MainAreaWidget,
  WidgetTracker
} from '@jupyterlab/apputils';

import { ISettingRegistry } from '@jupyterlab/coreutils';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { Menu } from '@phosphor/widgets';

import { fileBrowserFactory } from './filebrowser';

import { IZenodoRegistry, ZenodoFormFields } from './tokens';

import { ZenodoRegistry } from './registry';

import { ZenodoWidget } from './widget';

import { IFileBrowserFactory, FileBrowser } from '@jupyterlab/filebrowser';
import { Contents } from '@jupyterlab/services';

const zenodoPluginId = '@chameleoncloud/jupyterlab_zenodo:plugin';

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  requires: [
    ISettingRegistry,
    ICommandPalette,
    ILayoutRestorer,
    IMainMenu,
    IFileBrowserFactory,
    IZenodoRegistry
  ],
  activate: activateZenodoPlugin,
  autoStart: true
};

const zenodoRegistryPlugin: JupyterFrontEndPlugin<IZenodoRegistry> = {
  id: '@chameleoncloud/jupyterlab_zenodo:registry',
  provides: IZenodoRegistry,
  requires: [],
  activate(app: JupyterFrontEnd) {
    return new ZenodoRegistry();
  }
};

namespace CommandIDs {
  /*
   * Open a form that users can submit to publish to Zenodo
   */
  export const upload = 'zenodo:upload';

  /*
   * Update existing Zenodo deposition with new archive
   */
  export const update = 'zenodo:update';
}

/**
 * Activate the Zenodo front-end plugin
 *
 * NOTE: arguments must be in the same order as in the zenodoPlugin declaration
 */
function activateZenodoPlugin(
  app: JupyterFrontEnd,
  settingRegistry: ISettingRegistry,
  palette: ICommandPalette,
  restorer: ILayoutRestorer,
  mainMenu: IMainMenu,
  fileBrowserFactory: IFileBrowserFactory,
  zenodoRegistry: IZenodoRegistry
): void {
  // Retrive settings
  Promise.all([
    settingRegistry.load(zenodoPluginId),
    app.restored,
    zenodoRegistry.getDepositions()
  ])
    .then(([settings]) => {
      const browser = fileBrowserFactory.defaultBrowser;
      // Add commands to the extension, including the 'upload' command
      addZenodoCommands(app, settings, restorer, browser, zenodoRegistry);

      // Create sharing menu with 'upload' and 'update' commands
      const menu = new Menu({ commands: app.commands });
      menu.addItem({ command: CommandIDs.upload });
      menu.addItem({ command: CommandIDs.update });
      menu.title.label = 'Share';
      mainMenu.addMenu(menu, { rank: 20 });

      // Add commands to Command Palette
      palette.addItem({ command: CommandIDs.upload, category: 'Sharing' });
      palette.addItem({ command: CommandIDs.update, category: 'Sharing' });

      // Add context menu for directories
      app.contextMenu.addItem({
        command: CommandIDs.update,
        selector: '.jp-DirListing-item[data-isdir=true][data-doi]',
        rank: 4
      });
      app.contextMenu.addItem({
        command: CommandIDs.upload,
        selector: '.jp-DirListing-item[data-isdir=true]:not([data-doi])',
        rank: 4
      });
    })
    .catch((reason: Error) => {
      // If something went wrong, log the error
      console.error(reason.message);
    });
}

/*
 * Using arguments from 'activate' and the newly created widget,
 *   create commands for each action and add them to appropriate menus
 */
function addZenodoCommands(
  app: JupyterFrontEnd,
  settings: ISettingRegistry.ISettings,
  restorer: ILayoutRestorer,
  browser: FileBrowser,
  zenodoRegistry: IZenodoRegistry
) {
  const createLabel = settings.get('createLabel').composite as string;
  const editLabel = settings.get('editLabel').composite as string;
  const baseUrl = settings.get('baseUrl').composite as string;
  const externalEditUrl = settings.get('externalEditUrl').composite as string;
  const zenodoConfig = {
    baseUrl,
    externalEditUrl
  };

  let widget: MainAreaWidget<ZenodoWidget>;

  const tracker = new WidgetTracker<MainAreaWidget<ZenodoWidget>>({
    namespace: 'zenodo'
  });

  function openWidget(formDefaults: ZenodoFormFields) {
    if (!widget || widget.isDisposed) {
      const content = new ZenodoWidget(
        zenodoRegistry,
        zenodoConfig,
        formDefaults
      );
      content.title.label = createLabel;
      widget = new MainAreaWidget({ content });
      widget.id = 'zenodo';
    }

    if (!widget.isAttached) {
      app.shell.add(widget, 'main');
    }

    if (!tracker.has(widget)) {
      tracker.add(widget);
    }

    widget.update();
    app.shell.activateById(widget.id);
  }

  function unsupportedItem(item?: Contents.IModel) {
    return item && item.type !== 'directory';
  }

  function hasDeposition(item?: Contents.IModel) {
    // No item = check the root path (empty)
    return zenodoRegistry.hasDepositionSync((item && item.path) || '');
  }

  // Command to upload any set of files
  app.commands.addCommand(CommandIDs.upload, {
    label: createLabel,
    iconClass: 'jp-MaterialIcon jp-FileUploadIcon',
    isEnabled: () => {
      const item = browser.selectedItems().next();
      if (unsupportedItem(item)) {
        return false;
      }
      return !hasDeposition(item);
    },
    execute: () => {
      let formDefaults: ZenodoFormFields;

      const item = browser.selectedItems().next();
      if (item && item.type === 'directory') {
        formDefaults = { directory: item.path };
      }

      openWidget(formDefaults || {});
    }
  });

  app.commands.addCommand(CommandIDs.update, {
    label: editLabel,
    iconClass: 'jp-MaterialIcon jp-EditIcon',
    isEnabled: () => {
      const item = browser.selectedItems().next();
      if (unsupportedItem(item)) {
        return false;
      }
      return hasDeposition(item);
    },
    execute: () => {
      const item = browser.selectedItems().next();
      const path = (item && item.path) || '';
      zenodoRegistry.getDeposition(path).then(record => {
        if (!record) {
          throw Error(`No deposition exists at path "${path}"`);
        }

        const { externalEditUrl } = zenodoConfig;
        if (externalEditUrl) {
          window.open(externalEditUrl.replace('{doi}', record.doi));
        } else {
          // TODO: open edit UI
          throw Error('Not implemented yet');
        }
      });
    }
  });

  restorer.restore(tracker, {
    command: CommandIDs.upload,
    name: () => 'zenodo'
  });
}

/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [
  fileBrowserFactory,
  zenodoRegistryPlugin,
  zenodoPlugin
];

export default plugins;
