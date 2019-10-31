import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';

import { ISettingRegistry } from '@jupyterlab/coreutils';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { Menu } from '@phosphor/widgets';

import { fileBrowserFactory } from './filebrowser';

import { IZenodoRegistry } from './tokens';

import { ZenodoRegistry } from './registry';

import { ZenodoWidget } from './widget';

const zenodoPluginId = '@chameleoncloud/jupyterlab_zenodo:plugin';

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  requires: [
    ICommandPalette,
    IFileBrowserFactory,
    IMainMenu,
    ISettingRegistry,
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

  /*
   * Open Zenodo publish form with pre-filled (hidden) directory field
   */
  export const publishDirectory = 'zenodo:publish-directory';
}

/*
const onSettingsUpdated = async (settings: ISettingRegistry.ISettings) => {
    const baseUrl = settings.get('baseUrl').composite as
        | string
        | null
        | undefined;
    const accessToken = settings.get('accessToken').composite as
        | string
        | null
        | undefined;
    drive.baseUrl = baseUrl || DEFAULT_GITHUB_BASE_URL;
    if (accessToken) {
        let proceed = true;
        if (shouldWarn) {
            proceed = await Private.showWarning();
        }
        if (!proceed) {
            settings.remove('accessToken');
        } else {
            drive.accessToken = accessToken;
        }
    } else {
      drive.accessToken = null;
    }
};
*/


/**
 * Activate the Zenodo front-end plugin
 *
 * NOTE: arguments must be in the same order as in the zenodoPlugin declaration
 */
function activateZenodoPlugin(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  factory: IFileBrowserFactory,
  mainMenu: IMainMenu,
  settingRegistry: ISettingRegistry,
  zenodoRegistry: IZenodoRegistry
): void {
  // Retrive settings
  Promise.all([
    settingRegistry.load(zenodoPluginId),
    app.restored,
    zenodoRegistry.getDepositions()
  ])
    .then(([settings]) => {
      const uploadLabel = settings.get('uploadTitle').composite as string;
      const baseUrl = settings.get('baseUrl').composite as string;
      const zenodoConfig = {
        baseUrl
      };

      const widget = new MainAreaWidget({
        content: new ZenodoWidget(zenodoRegistry, zenodoConfig)
      });
      widget.id = 'zenodo';
      widget.title.label = uploadLabel;
      widget.title.closable = true;

      // Add commands to the extension, including the 'upload' command
      addZenodoCommands(
        app,
        palette,
        factory,
        mainMenu,
        widget,
        zenodoRegistry,
        uploadLabel
      );
    })
    .catch((reason: Error) => {
      // If something went wrong, log the error
      console.error(reason.message);
    });

  return;
}

function openWidget(
  app: JupyterFrontEnd,
  widget: MainAreaWidget
) {
  if (!widget.isAttached) {
    app.shell.add(widget, 'main');
  }
  app.shell.activateById(widget.id);
}

/*
 * Using arguments from 'activate' and the newly created widget,
 *   create commands for each action and add them to appropriate menus
 */
function addZenodoCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  factory: IFileBrowserFactory,
  mainMenu: IMainMenu,
  widget: MainAreaWidget,
  zenodoRegistry: IZenodoRegistry,
  uploadLabel: string
) {
  const { tracker } = factory;

  // Command to publish from a directory
  app.commands.addCommand(CommandIDs.publishDirectory, {
    label: uploadLabel,
    execute: () => {
      if (!tracker.currentWidget) {
        return;
      }

      const item = tracker.currentWidget.selectedItems().next();
      if (!item) {
        return;
      }

      zenodoRegistry.updateDeposition(item.path);
      // TODO: when done, broadcast event to show UI
    },
    iconClass: 'jp-MaterialIcon jp-FileUploadIcon'
  });

  // Command to upload any set of files
  app.commands.addCommand(CommandIDs.upload, {
    label: uploadLabel,
    iconClass: 'icon-class',
    execute: () => {
      openWidget(app, widget);
    }
  });

  app.commands.addCommand(CommandIDs.update, {
    label: 'Update Zenodo Deposition',
    iconClass: 'icon-class',
    execute: () => {
      openWidget(app, widget);
      // Just update the first one we find
      // TODO: this should either be smarter, or perhaps not exist
      // as functionality? Need to deal with multiple depositions.
      zenodoRegistry.getDepositions().then(([record]) => {
        if (record) {
          zenodoRegistry.updateDeposition(record.path);
        }
      });
    }
  });

  // Create sharing menu with 'upload' and 'update' commands
  const menu = new Menu({ commands: app.commands });
  menu.addItem({ command: CommandIDs.upload });
  menu.addItem({ command: CommandIDs.update });
  menu.title.label = 'Share';
  mainMenu.addMenu(menu, { rank: 20 });

  // Add commands to Command Palette
  palette.addItem({ command: CommandIDs.upload, category: 'Sharing' });
  palette.addItem({ command: CommandIDs.update, category: 'Sharing' });

  // Add context menu for directories with 'publish directory' command
  app.contextMenu.addItem({
    command: CommandIDs.publishDirectory,
    selector: '.jp-DirListing-item[data-isdir=true]',
    rank: 4
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
