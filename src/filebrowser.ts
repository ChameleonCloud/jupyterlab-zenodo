import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ToolbarButton, WidgetTracker } from '@jupyterlab/apputils';

import { IStateDB } from '@jupyterlab/coreutils';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { DocumentRegistry } from '@jupyterlab/docregistry';

import {
  FileBrowserModel,
  FileBrowser,
  IFileBrowserFactory,
  DirListing
} from '@jupyterlab/filebrowser';

import { Contents } from '@jupyterlab/services';

import { IIconRegistry } from '@jupyterlab/ui-components';

export interface IZenodoRegistry {
  getDOIForPath(path: string): string | null;
}

class ZenodoRegistry implements IZenodoRegistry {
  getDOIForPath(path: string) {
    // TODO
    return (new Date()).getMilliseconds().toString();
  }
}

class ZenodoFileBrowserModel extends FileBrowserModel {}

class ZenodoDirListingRenderer extends DirListing.Renderer {
  constructor(icoReg: IIconRegistry, zenodoReg: IZenodoRegistry) {
    super(icoReg);
    this._zenodoReg = zenodoReg;
  }

  updateItemNode(
    node: HTMLElement,
    model: Contents.IModel,
    fileType?: DocumentRegistry.IFileType
  ): void {
    super.updateItemNode(node, model, fileType);

    const doi = this._zenodoReg.getDOIForPath(model.path);
    if (doi) {
      node.setAttribute('data-doi', doi);
    } else {
      delete node.dataset.doi;
    }
  }

  private _zenodoReg: IZenodoRegistry;
}

function activateFactory(
  app: JupyterFrontEnd,
  icoReg: IIconRegistry,
  docManager: IDocumentManager,
  state: IStateDB
): IFileBrowserFactory {
  const { commands } = app;
  const tracker = new WidgetTracker<FileBrowser>({ namespace: 'filebrowser' });
  const createFileBrowser = (
    id: string,
    options: IFileBrowserFactory.IOptions = {}
  ) => {
    const model = new ZenodoFileBrowserModel({
      iconRegistry: icoReg,
      manager: docManager,
      driveName: options.driveName || '',
      refreshInterval: options.refreshInterval,
      state: options.state === null ? null : options.state || state
    });
    const zenodoReg = new ZenodoRegistry();
    const renderer = new ZenodoDirListingRenderer(icoReg, zenodoReg);
    const widget = new FileBrowser({
      id,
      model,
      renderer
    });

    // Add a launcher toolbar item.
    let launcher = new ToolbarButton({
      iconClassName: 'jp-AddIcon',
      onClick: () => commands.execute('filebrowser:create-main-launcher'),
      tooltip: 'New Launcher'
    });
    widget.toolbar.insertItem(0, 'launch', launcher);

    // Track the newly created file browser.
    void tracker.add(widget);

    return widget;
  };
  // Use the same name
  const defaultBrowser = createFileBrowser('filebrowser');

  return { createFileBrowser, defaultBrowser, tracker };
}

/**
 * The default file browser factory provider.
 */
export const fileBrowserFactory: JupyterFrontEndPlugin<IFileBrowserFactory> = {
  activate: activateFactory,
  id: '@chameleoncloud/jupyterlab_zenodo:file-browser-factory',
  provides: IFileBrowserFactory,
  requires: [IIconRegistry, IDocumentManager, IStateDB]
};
