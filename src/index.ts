/*
 * NOTE: All of this was copy/pasted from jupyterlab/jupyterlab-latex from src/index.ts and then edited */ 
console.log("TESTING 4:46")

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette,
} from '@jupyterlab/apputils';

import {
    ISettingRegistry,
    URLExt,
} from '@jupyterlab/coreutils';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { IEditorTracker } from '@jupyterlab/fileeditor';

import { ServerConnection } from '@jupyterlab/services';

import { Menu } from '@phosphor/widgets';

const zenodoPluginId = '@jupyterlab/zenodo:plugin';

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  autoStart: true,
  requires: [
    ISettingRegistry,
    ICommandPalette,
    IEditorTracker,
    IMainMenu,
  ],
  activate: activateZenodoPlugin
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
    path: string,
    settings: ServerConnection.ISettings
): Promise<any> {
    console.log("upload req");
    let fullUrl = URLExt.join(settings.baseUrl, 'zenodo', 'upload', "hi");

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
    editorTracker: IEditorTracker,
    mainMenu: IMainMenu
  ): void {
    const serverSettings = ServerConnection.makeSettings();
    console.log("Activating plugin");

    const command: string = 'zenodo:upload'
    app.commands.addCommand(command, {
        label: 'Upload to Zenodo',
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            console.log("trying to do a thing");
            zenodoUploadRequest("hi", serverSettings);
            console.log('Executed ${commandIDs.uploadToZenodo}');
        },
    
    }); 

    //palette.addItem({command, category: 'Zenodo'})
    console.log("Checking main menu");
    console.log(mainMenu);
    const menu = new Menu({ commands: app.commands });
    
    menu.addItem({
        command: command,
        args: {},
    });
    menu.title.label = 'Zenodo';
    

    mainMenu.addMenu(menu, { rank: 40 });

} 
 
/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [zenodoPlugin];
export default plugins;

