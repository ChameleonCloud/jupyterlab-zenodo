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
    ISettingRegistry,
    ICommandPalette,
    IEditorTracker,
    IMainMenu,
  ],
  activate: activateZenodoPlugin
};

function handleUploadResponse(
    response : Response
   ){
    console.log('status',response.status);
    var loading = document.getElementById("loading-div") as HTMLElement;

    if (response.status > 299) {
        return response.json().then(data => {
            var form = document.getElementById("submit-form") as HTMLElement;
            let error = document.getElementById("error-div") as HTMLElement;
            loading.style.display = "None";
            form.style.display = "Block";
            error.innerHTML = "Error: "+data.message + ". Please try again.";
        });
    } else {
        return response.json().then(data => {
            var success = document.getElementById("success-div") as HTMLElement;
            var zenodo_button = document.getElementById("zenodo-button") as HTMLLinkElement;
            var portal_button = document.getElementById("portal-button") as HTMLLinkElement;
        
            loading.style.display = "None";
            success.style.display = "Block";
            let doi = data.doi;
            console.log(doi);
            let record_id = (doi.split('.')).pop();
            zenodo_button.target="_blank";
            zenodo_button.href = "https://zenodo.org/record/"+record_id;
            //TODO: fix this before deployment
            portal_button.target="_blank";
            portal_button.href = "http://localhost:7000/portal/upload/"+doi;
            console.log("it worked!");
        });
    }
}


function sendFormData(){
    //var XHR = new XMLHttpRequest();

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

    //var token_param = '?token=729tokMK2019'    
    var settings =ServerConnection.makeSettings()
    //const parts = [settings.baseUrl, 'zenodo', 'upload', token_param]
    const parts = [settings.baseUrl, 'zenodo', 'upload']
    const fullURL = URLExt.join.apply(URLExt, parts);

    console.log("about to connect");
    ServerConnection.makeRequest(fullURL,
        {method: 'POST', body: body_json}, settings).then(
        //response => { handleUploadResponse(JSON.parse(String(response))); });
        response => { handleUploadResponse(response); });
//            handleJsonResponse<void>()).then(() => {});

    //console.log("connected");
    //alert(FD.get('title'));
    
    /*
    XHR.addEventListener(
        "error", function(event){ alert("testing...error!")}
    );

    XHR.addEventListener(
        "load", function(event){ alert("testing...success!")}
    );


    XHR.open("POST","/zenodo/upload?token=729tokMK2019");

    XHR.send(FD);
    */
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
    success_div.innerHTML = "Congratulations, your files have been uploaded to Zenodo!";
    let zenodo_button = document.createElement("a"); 
    zenodo_button.innerHTML = "<p> View on Zenodo </p>";
    zenodo_button.id = "zenodo-button";
    let portal_button = document.createElement("a"); 
    portal_button.innerHTML = "<p> Upload to the Chameleon sharing portal </p>";
    portal_button.id = "portal-button";
    success_div.appendChild(zenodo_button);
    success_div.appendChild(portal_button);
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
    let error = document.createElement('p');
    error.id = "error-div";
    error.style.color = "red";
    upload_form.appendChild(error);

    // The actual form
    let form_table = document.createElement('table')
    let form_body = document.createElement('tbody')
    form_body.appendChild(newInput('Title','title'));
    form_body.appendChild(newInput('Prefix for zip file','file_prefix'));
    form_body.appendChild(newInput('Author','author'));
    form_body.appendChild(newInput('Description','description'));
    form_body.appendChild(newInput('Directory to zip (default is work)','directory'));
    form_body.appendChild(newInput('Access token (optional)','zenodo-token'));

    // Make space for submit button    
    let submit_row = document.createElement('tr')
    let submit_label = document.createElement('th')
    let submit_cell = document.createElement('td')
    let submit_button = document.createElement('input');

    // Create submit button
    submit_button.type = 'submit';
    submit_button.value = 'Submit';
    submit_button.classList.add("submit-btn");
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

    /*  Sample values for testing 
    
    let item = document.getElementById('title-input') as HTMLInputElement;
    item.value = 'test';
    item = document.getElementById('description-input') as HTMLInputElement;
    item.value = 'test';
    item = document.getElementById('file_prefix-input') as HTMLInputElement;
    item.value = 'test';
    item = document.getElementById('author-input') as HTMLInputElement;
    item.value = 'test';

    */

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


