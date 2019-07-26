/*
 * NOTE: All of this was copy/pasted from jupyterlab/jupyterlab-latex from src/index.ts and then edited 
 */

console.log("TESTING")

import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette,
    //MainAreaWidget
  //IWidgetTracker
} from '@jupyterlab/apputils';

/*
import { CodeEditor } from '@jupyterlab/codeeditor';

*/

import {
  IStateDB,
  ISettingRegistry,
  URLExt,
} from '@jupyterlab/coreutils';

import { IDocumentManager } from '@jupyterlab/docmanager';

//import { IDocumentWidget } from '@jupyterlab/docregistry';

import { IEditorTracker } from '@jupyterlab/fileeditor';

import { ServerConnection } from '@jupyterlab/services';

// import { Token } from '@phosphor/coreutils';

//import '../style/index.css';


/**
 * A class that tracks editor widgets.
 */

/* tslint:disable */
/**
 * The editor tracker token.
export const IPDFJSTracker = new Token<IPDFJSTracker>(
  '@jupyterlab/zenodo:IPDFJSTracker'
);
 */
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

/**
 * The options for a SyncTeX edit command,
 * mapping the pdf position to an editor position.
 */

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  requires: [
    IDocumentManager,
    IEditorTracker,
    ILabShell,
    ICommandPalette,
    ILayoutRestorer,
    //IPDFJSTracker,
    ISettingRegistry,
    IStateDB
  ],
  activate: activateZenodoPlugin,
  autoStart: true
};

//const palette = ICommandPalette;


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
    console.log("upload req");
    let fullUrl = URLExt.join(settings.baseUrl, 'zenodo', 'upload', "hi");
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
    settingRegistry: ISettingRegistry,
    palette: ICommandPalette,
    /*
    manager: IDocumentManager,
    editorTracker: IEditorTracker,
    shell: ILabShell,
    restorer: ILayoutRestorer,
    pdfTracker: IPDFJSTracker,
    state: IStateDB
    */
  ): void {
    const serverSettings = ServerConnection.makeSettings();
    console.log("here i am");
    // const { commands } = app;
    // const id = 'jupyterlab-zenodo';
    // widget.id = 'zenodo-jupyterlab'
    // widget.title.label = 'Zenodo Upload';
    // widget.title.closable = true;


      //Lots of stuff in between
    //const command: string = 'zenodo:upload'
    app.commands.addCommand(CommandIDs.uploadToZenodo, {
        label: 'Upload to Zenodo',
        //isEnabled: true,//hasWidget,
        //isVisible: true,
        //toggled: false,
        isToggled: () => false, //toggled,
        iconClass: 'icon-class',
        execute: () => {
            zenodoUploadRequest("hi", serverSettings);
            console.log('Executed ${commandIDs.uploadToZenodo}');
            /*
            if (!widget.isAttached){
               app.shell.add(widget, 'main'); 
            }
            app.shell.activateById(widget.id);
            */
            //toggled = !toggled;
            //isToggled = !isToggled
            // Get the current widget that had its contextMenu activated.
            /*
            let widget = editorTracker.currentWidget;
            if (widget) {
                openPreview(widget);
            }
            */
        },
    
        /*
        isVisible: () => {
            let widget = editorTracker.currentWidget;
            return (
                true //MKQ: Probably change this
//                (widget && PathExt.extname(widget.context.path) === '.tex') || false
            );
        },
        */
    }); 
 
    app.contextMenu.addItem({
        command: CommandIDs.uploadToZenodo,
        selector: '.jp-FileEditor' //MKQ: change this
    });
 
    //palette.addItem({command, category: 'Zenodo'})

} 
 
/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [zenodoPlugin];
export default plugins;

/**
 * A namespace for private module data.
 */
/*
  namespace Private {
    /**
     * A counter for unique IDs.
    let id = 0;
     */
  
    /**
     * A cache for the currently active LaTeX previews.
    export const previews = new Set<string>();
     */
  
    /**
     * Create an error panel widget.
    export function createErrorPanel(): ErrorPanel {
        const errorPanel = new ErrorPanel();
        errorPanel.id = `zenodo-error-${++id}`;
        errorPanel.title.label = 'Zenodo Error';
        errorPanel.title.closable = true;
        return errorPanel;
    }
     */
//} 

/*
palette.addItem({
  command: CommandIDs.uploadToZenodo,
  category: 'Zenodo',
  args: {}
});

const menu = new Menu({ commands: app.commands });
menu.add Item({
    command: CommandIDs.uploadToZenodo,
    args: {}
});

mainMenu.addMenu(menu, { rank: 40 });

*/
