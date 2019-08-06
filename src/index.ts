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

import {
    IFileBrowserFactory
} from '@jupyterlab/filebrowser';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { IEditorTracker } from '@jupyterlab/fileeditor';

import { Widget, Menu } from '@phosphor/widgets';

import { ServerConnection } from '@jupyterlab/services';

import { URLExt } from '@jupyterlab/coreutils';

const zenodoPluginId = '@jupyterlab/zenodo:plugin';

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  autoStart: true,
  requires: [
    ICommandPalette,
    IEditorTracker,
    IFileBrowserFactory,
    IMainMenu,
    ISettingRegistry,
  ],
  activate: activateZenodoPlugin
};

namespace CommandIDs {
    export const upload = 'zenodo:upload';
    export const update = 'zenodo:update';
    export const publish_directory = 'zenodo:publish-directory';
}

function show_success(
    doi : string
  ){
    var success = document.getElementById("success-div") as HTMLElement;
    var zenodo_button = document.getElementById("zenodo-button") as HTMLLinkElement;

    var loading = document.getElementById("loading-div") as HTMLElement;
    loading.style.display = "None";
    success.style.display = "Flex";
    console.log(doi);
    let record_id = (doi.split('.')).pop();
    zenodo_button.target="_blank";
    //TODO: delete 'sandbox' before Zenodo
    zenodo_button.href = "https://sandbox.zenodo.org/record/"+record_id;
    console.log("it worked!");
}

function handleUploadResponse(
    response : Response
   ){
    console.log('status',response.status);
    var loading = document.getElementById("loading-div") as HTMLElement;

    if (response.status > 299) {
        return response.json().then(data => {
            var form = document.getElementById("submit-form") as HTMLElement;
            let error = document.getElementById("form-error-div") as HTMLElement;
            loading.style.display = "None";
            form.style.display = "Block";
            error.innerHTML = "Error: "+data.message + ". Please try again.";
        });
    } else {
        return response.json().then(data => {
            let doi = data.doi;
            show_success(doi);
            var portal_button = document.getElementById("portal-button") as HTMLLinkElement;
            portal_button.target="_blank";
            //TODO: fix this before deployment
            portal_button.href = "http://localhost:7000/portal/upload/"+doi;
        });
    }
}

function handleUpdateResponse(
    response : Response
   ){
    console.log('status',response.status);
    var loading = document.getElementById("loading-div") as HTMLElement;

    if (response.status > 299) {
        return response.json().then(data => {
            let error = document.getElementById("outer-error-div") as HTMLElement;
            loading.style.display = "None";
            error.style.display = "Block";
            error.innerHTML = "Error: "+data.message + ". Please try again.";
        });
    } else {
        return response.json().then(data => {
            let doi = data.doi;
            show_success(doi);
            var portal_button = document.getElementById("portal-button") as HTMLLinkElement;
            portal_button.style.display = "None"
            //alert("Your deposition was successfully updated");
        });
    }
}
 
function sendFormData(){
    var form = document.getElementById('submit-form') as HTMLFormElement;
    var loading = document.getElementById('loading-div') as HTMLElement;
    form.style.display = "None";
    loading.style.display = "Block";

    var formData = new FormData(form);
    var formbody : { [key: string]: string } = {};
    formData.forEach(function(value,key){
        formbody[key] = value.toString();
    });
    var body_json = JSON.stringify(formbody);

    var settings =ServerConnection.makeSettings()
    const parts = [settings.baseUrl, 'zenodo', 'upload']
    const fullURL = URLExt.join.apply(URLExt, parts);

    console.log("about to connect");
    ServerConnection.makeRequest(fullURL,
        {method: 'POST', body: body_json}, settings).then(
        response => { handleUploadResponse(response); });
}


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
    //input.value = "";
    input.type = 'text';
    input.name = id;
    input.id = id+'-input';
    input_cell.appendChild(input); 

    input_row.appendChild(label_cell); 
    input_row.appendChild(input_cell); 
    return input_row; 
}

function activateZenodoPlugin(
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    factory: IFileBrowserFactory,
    mainMenu: IMainMenu,
    settingRegistry: ISettingRegistry,
  ): void {



    const { tracker } = factory;

    const content = new Widget();
    const widget = new MainAreaWidget({content});
    widget.id = 'zenodo-jupyterlab';
    widget.title.label = 'Zenodo Upload'
    widget.title.closable = true;

    /* Create main div */
    let main = document.createElement('div');
    main.id = "zenodo-upload-main";

    /* Loading screen */
    let loading_div = document.createElement('div');
    loading_div.style.display = "None";
    loading_div.id = 'loading-div';
    loading_div.innerHTML = "Please wait... your files are being uploaded... ";
    // Add to main div
    main.appendChild(loading_div);

    /* Success screen */
    let success_div = document.createElement('div');
    success_div.style.display = "None";
    success_div.id = 'success-div';
    success_div.innerHTML = "<h1> Congratulations, your files have been uploaded to Zenodo! </h1>";
    let tr = document.createElement("tr");
    let zenodo_button = document.createElement("a"); 
    zenodo_button.innerHTML = "View on Zenodo";
    zenodo_button.id = "zenodo-button";
    zenodo_button.classList.add("basic-btn");
    
    let td_zenodo = document.createElement("td");
    let portal_button = document.createElement("a"); 
    portal_button.innerHTML = "Upload to the Chameleon sharing portal";
    portal_button.id = "portal-button";
    portal_button.classList.add("basic-btn");
    let td_portal = document.createElement("td");
    td_zenodo.appendChild(zenodo_button);
    td_portal.appendChild(portal_button);
    tr.appendChild(td_zenodo);
    tr.appendChild(td_portal);
    success_div.appendChild(tr);
    // Add to main div
    main.appendChild(success_div);

    /* Form to upload to Zenodo */
    let upload_form = document.createElement('form');
    upload_form.id = 'submit-form';

    // Headers
    let header = document.createElement('h2');
    header.innerHTML = "Submission Details"
    let subheader = document.createElement('p');
    subheader.innerHTML = "Please fill out the bolded fields and then click 'Submit' to upload to Zenodo"
    upload_form.appendChild(header);
    upload_form.appendChild(subheader);

    // Error messages
    let form_error = document.createElement('p');
    form_error.id = "form-error-div";
    form_error.style.color = "red";
    upload_form.appendChild(form_error);

    let outer_error = document.createElement('p');
    outer_error.id = "outer-error-div";
    outer_error.style.color = "red";
    main.appendChild(outer_error);

    // The actual form
    let form_table = document.createElement('table')
    let form_body = document.createElement('tbody')
    form_body.appendChild(newInput('Title','title'));
    form_body.appendChild(newInput('Name for compressed file','filename'));
    form_body.appendChild(newInput('Author','author'));
    form_body.appendChild(newInput('Description','description'));
    form_body.appendChild(newInput('Directory to zip (default is work)','directory'));
    form_body.appendChild(newInput('Access token (optional)','zenodo_token'));

    // Make space for submit button    
    let submit_row = document.createElement('tr')
    let submit_label = document.createElement('th')
    let submit_cell = document.createElement('td')
    let submit_button = document.createElement('input');

    // Create submit button
    submit_button.type = 'submit';
    submit_button.value = 'Submit';
    submit_button.classList.add("basic-btn");
    upload_form.addEventListener('submit', function (event) {
        event.preventDefault();
        sendFormData();
    });

    // Add submit button to form
    submit_cell.appendChild(submit_button);
    submit_row.appendChild(submit_label);
    submit_row.appendChild(submit_cell);
    form_body.appendChild(submit_row);

    // Add form table to form div
    form_table.appendChild(form_body);
    upload_form.appendChild(form_table);

    // Add form to main upload div
    main.appendChild(upload_form);

    // Add main upload div to widget
    content.node.appendChild(main);

    app.commands.addCommand(CommandIDs.publish_directory, {
        //HERE
        label: 'Publish to Zenodo',
        isEnabled: () => true,
        isToggled: () => false, 
        execute: () => {
            if (!tracker.currentWidget){
                return;
            }
            const item = tracker.currentWidget.selectedItems().next();
            if (!item){
                return;
            } 
            if (!widget.isAttached){
                app.shell.add(widget, 'main');
            }
            let path = item.path;
            console.log(path); 
            let dir_input = document.getElementById("directory-input") as HTMLInputElement
            dir_input.value = path;
            let dir_row = document.getElementById("directory") as HTMLElement;
            dir_row.style.display = "None";
            
            upload_form.style.display = "Block";
            outer_error.style.display = "None";
            success_div.style.display = "None";
            loading_div.style.display = "None";
        },
    });

    app.commands.addCommand(CommandIDs.upload, {
        label: 'Upload to Zenodo',
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            if (!widget.isAttached){
                app.shell.add(widget, 'main');
            }
            upload_form.style.display = "Block";
            outer_error.style.display = "None";
            success_div.style.display = "None";
            loading_div.style.display = "None";
        },
    
    }); 

    app.commands.addCommand(CommandIDs.update, {
        label: 'Update Zenodo Deposition',
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            if (!widget.isAttached){
                app.shell.add(widget, 'main');
            }
            upload_form.style.display = "None";
            outer_error.style.display = "None";
            success_div.style.display = "None";
            loading_div.style.display = "Flex";
            console.log("This causes an update"); 
            var settings =ServerConnection.makeSettings()
            const parts = [settings.baseUrl, 'zenodo', 'update']
            const fullURL = URLExt.join.apply(URLExt, parts);

            ServerConnection.makeRequest(fullURL,
                {method: 'POST'}, settings).then(
                response => { handleUpdateResponse(response); });
        }

    }); 

    const menu = new Menu({ commands: app.commands });
    
    menu.addItem({
        command: CommandIDs.upload
    });
 
    menu.addItem({
        command: CommandIDs.update
    });

    palette.addItem({command: CommandIDs.upload, category: 'Sharing'})
    palette.addItem({command: CommandIDs.update, category: 'Sharing'})

    menu.title.label = 'Share';

    mainMenu.addMenu(menu, { rank: 20 });

    const selectorItem = '.jp-DirListing-item[data-isdir=true]';

    app.contextMenu.addItem({
        command: CommandIDs.publish_directory,
        selector: selectorItem,
        rank: 4
    });

} 
 
/**
 * Export the plugins as default.
 */
const plugins: JupyterFrontEndPlugin<any>[] = [zenodoPlugin];
export default plugins;


