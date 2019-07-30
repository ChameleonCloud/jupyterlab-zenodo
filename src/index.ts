/*
 * NOTE: All of this was copy/pasted from jupyterlab/jupyterlab-latex from src/index.ts and then edited */ 

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    ICommandPalette, MainAreaWidget
} from '@jupyterlab/apputils';

import {
    ISettingRegistry,
} from '@jupyterlab/coreutils';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { IEditorTracker } from '@jupyterlab/fileeditor';

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


function newInput(
    label: string,
    id: string
  ): HTMLElement {
    let input_row = document.createElement('tr');
    input_row.id = id;

    let label_cell = document.createElement('th')
    label_cell.innerHTML = label + ": ";

    let input_cell = document.createElement('td');
    let input = document.createElement('input');
    input.type = 'text';
    input.name = id;
    input_cell.appendChild(input); 

    input_row.appendChild(label_cell); 
    input_row.appendChild(input_cell); 
    return input_row; 
}

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

    let header = document.createElement('h2');
    header.innerHTML = "Submission Details"
    let subheader = document.createElement('p');
    subheader.innerHTML = "Please fill out the bolded fields and then click 'Submit' to upload to Zenodo"

    upload_form.appendChild(header);
    upload_form.appendChild(subheader);

    let form_table = document.createElement('table')
    let form_body = document.createElement('tbody')
    form_body.appendChild(newInput('Title','title'));
    form_body.appendChild(newInput('Prefix for zip file','file_prefix'));
    form_body.appendChild(newInput('Author','author'));
    form_body.appendChild(newInput('Description','description'));
    form_body.appendChild(newInput('Access token (optional)','zenodo-token'));
    
    let submit_row = document.createElement('tr')
    let submit_label = document.createElement('th')
    let submit_cell = document.createElement('td')
    let submit_button = document.createElement('input');
    submit_button.type = 'submit';
    submit_button.value = 'Submit';
    submit_button.classList.add("submit-btn");
    submit_cell.appendChild(submit_button);
    submit_row.appendChild(submit_label);
    submit_row.appendChild(submit_cell);
    form_body.appendChild(submit_row);

    form_table.appendChild(form_body);
    upload_form.appendChild(form_table);
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
        },
    
    }); 

    palette.addItem({command, category: 'Sharing'})
    const menu = new Menu({ commands: app.commands });
    
    menu.addItem({
        command: command,
        args: {},
    });
    menu.title.label = 'Share';
    

    mainMenu.addMenu(menu, { rank: 20 });

} 
 
/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [zenodoPlugin];
export default plugins;


