/*
 * NOTE: All of this was copy/pasted from jupyterlab/jupyterlab-latex from src/index.ts and then edited 
 */

import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  IWidgetTracker,
  WidgetTracker,
  showErrorMessage
} from '@jupyterlab/apputils';

import { CodeEditor } from '@jupyterlab/codeeditor';

import {
  IStateDB,
  PathExt,
  ISettingRegistry,
  URLExt
} from '@jupyterlab/coreutils';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { DocumentRegistry, IDocumentWidget } from '@jupyterlab/docregistry';

import { FileEditor, IEditorTracker } from '@jupyterlab/fileeditor';

import { ServerConnection } from '@jupyterlab/services';

import { ReadonlyJSONObject, Token } from '@phosphor/coreutils';

import { DisposableSet } from '@phosphor/disposable';

import { ErrorPanel } from './error';

import { PDFJSDocumentWidget, PDFJSViewer, PDFJSViewerFactory } from './pdf';

import '../style/index.css';


/**
 * A class that tracks editor widgets.
 */
export interface IPDFJSTracker
  extends IWidgetTracker<IDocumentWidget<PDFJSViewer>> {}

/* tslint:disable */
/**
 * The editor tracker token.
 */
export const IPDFJSTracker = new Token<IPDFJSTracker>(
  '@jupyterlab/zenodo:IPDFJSTracker'
);
/* tslint:enable */

const zenodoPluginId = '@jupyterlab/zenodo:plugin';

namespace CommandIDs {
  /**
   * Open a live preview for a `.tex` document.
   */
  export const uploadToZenodo = 'zenodo:upload-directory';

  /**
   * Reveal in the editor a position from the pdf using SyncTeX.
   */
  //export const synctexEdit = 'latex:synctex-edit';

  /**
   * Reveal in the pdf a position from the editor using SyncTeX.
   */
  //export const synctexView = 'latex:synctex-view';
}


/**
 * The options for a SyncTeX view command,
 * mapping the editor position the PDF.
 */
// MKQ: do i need this?
type ISynctexViewOptions = CodeEditor.IPosition;

/**
 * The options for a SyncTeX edit command,
 * mapping the pdf position to an editor position.
 */
// MKQ: do i need this?
type ISynctexEditOptions = PDFJSViewer.IPosition;

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  requires: [
    IDocumentManager,
    IEditorTracker,
    ILabShell,
    ILayoutRestorer,
    IPDFJSTracker,
    ISettingRegistry,
    IStateDB
  ],
  activate: activateZenodoPlugin,
  autoStart: true
};


/**
 * Make a request to the notebook server Zenodo endpoint.
 *
 * @param filename - the file name
 *
 * @param settings - the settings for the current notebook server.
 *
 * @returns a Promise resolved with the text response.
 */
function zenodoUploadRequest(
    //used to be: latexBuildRequest
    path: string,
    // synctex: boolean,
    settings: ServerConnection.ISettings
): Promise<any> {
    let fullUrl = URLExt.join(settings.baseUrl, 'zenodo', 'build', filename);
    // fullUrl += `?synctex=${synctex ? 1 : 0}`;

    return ServerConnection.makeRequest(fullUrl, {}, settings).then(response => {
        if (response.status !== 200) {
            return response.text().then(data => {
                throw new ServerConnection.ResponseError(response, data);
            });
        }
        return response.text();
    });
}

function activateZenodoPlugin(
    app: JupyterFrontEnd,
    manager: IDocumentManager,
    editorTracker: IEditorTracker,
    shell: ILabShell,
    restorer: ILayoutRestorer,
    pdfTracker: IPDFJSTracker,
    settingRegistry: ISettingRegistry,
    state: IStateDB
  ): void {
    const { commands } = app;
    const id = 'jupyterlab-zenodo';
  
      //Lots of stuff in between
   commands.addCommand(CommandIDs.uploadToZenodo, {
        execute: () => {
            // Get the current widget that had its contextMenu activated.
            let widget = editorTracker.currentWidget;
            if (widget) {
                openPreview(widget);
            }
        },
        isEnabled: hasWidget,
        isVisible: () => {
            let widget = editorTracker.currentWidget;
            return (
                true //MKQ: Probably change this
//                (widget && PathExt.extname(widget.context.path) === '.tex') || false
            );
        },
        label: 'Upload to Zenodo'
    }); 
 
    app.contextMenu.addItem({
        command: CommandIDs.uploadToZenodo,
        selector: '.jp-FileEditor' //MKQ: change this
    });
 
  
 
/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [zenodoPlugin];
export default plugins;

/**
 * A namespace for private module data.
 */
  namespace Private {
    /**
     * A counter for unique IDs.
     */
    let id = 0;
  
    /**
     * A cache for the currently active LaTeX previews.
     */
    export const previews = new Set<string>();
  
    /**
     * Create an error panel widget.
     */
    export function createErrorPanel(): ErrorPanel {
        const errorPanel = new ErrorPanel();
        errorPanel.id = `zenodo-error-${++id}`;
        errorPanel.title.label = 'Zenodo Error';
        errorPanel.title.closable = true;
        return errorPanel;
    }
} 
