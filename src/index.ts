/*
 * NOTE: All of this was copy/pasted from jupyterlab/jupyterlab-latex from src/index.ts and then edited */ 
console.log("TESTING 0939")

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette, MainAreaWidget
} from '@jupyterlab/apputils';

import {
    ISettingRegistry,
    //URLExt,
} from '@jupyterlab/coreutils';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { IEditorTracker } from '@jupyterlab/fileeditor';

//import { ServerConnection } from '@jupyterlab/services';

import { Widget, Menu } from '@phosphor/widgets';

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

/*
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
*/


function newInput(
    label: string,
    id: string
  ): HTMLElement {
    let input_section = document.createElement('div');
    input_section.innerHTML = label + ": ";
    let input_item = document.createElement('input');
    input_item.type = 'text';
    input_item.id = id;
    input_item.name = id;
    //TODO: delete this
    input_item.value = 'test';
    input_section.appendChild(input_item); 
    return input_section; 
}

/*
function submit_form(
  ): void {
    let title = document.getElementById('title-input').value
    console.log("Wow got the title! Here: "+title);
}
*/

function activateZenodoPlugin(
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    mainMenu: IMainMenu
  ): void {
    //const serverSettings = ServerConnection.makeSettings();
    console.log("Activating plugin");
    const content = new Widget();
    const widget = new MainAreaWidget({content});
    widget.id = 'zenodo-jupyterlab';
    widget.title.label = 'Zenodo Upload'
    widget.title.closable = true;

    let upload_form = document.createElement('form');
    upload_form.id = 'submit-form';
    //upload_form.action="/zenodo/upload?_xsrf=444b220ba95f2c2edcb4fa0be19219c2b8c26f3072663b34"
    upload_form.action="/zenodo/upload?token="
    upload_form.method="post"

    upload_form.appendChild(newInput('Title','title'));
    upload_form.appendChild(newInput('Prefix for zip file','file_prefix'));
    upload_form.appendChild(newInput('Author','author'));
    upload_form.appendChild(newInput('Description','description'));
    upload_form.appendChild(newInput('Access token (optional)','zenodo-token'));
    

    let submit_button = document.createElement('input');
    submit_button.type = 'submit';
    submit_button.value = 'submit';
    upload_form.appendChild(submit_button);

    content.node.appendChild(upload_form);
    //HERE


    const command: string = 'zenodo:upload'
    app.commands.addCommand(command, {
        label: 'Upload to Zenodo',
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            if (!widget.isAttached){
                app.shell.add(widget, 'main');
            }
            console.log("trying to do a thing");
            console.log('Executed ${commandIDs.uploadToZenodo}');
        },
    
    }); 

    palette.addItem({command, category: 'Zenodo'})
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


