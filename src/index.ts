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

const UPLOAD_LABEL = 'Upload to Zenodo';

const zenodoPluginId = '@jupyterlab/zenodo:plugin';

/**
 * The JupyterFrontEnd plugin for the Zenodo extension.
 */
const zenodoPlugin: JupyterFrontEndPlugin<void> = {
  id: zenodoPluginId,
  requires: [
    ICommandPalette,
    IEditorTracker,
    IFileBrowserFactory,
    IMainMenu,
    ISettingRegistry,
  ],
  activate: activateZenodoPlugin,
  autoStart: true,
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
    export const publish_directory = 'zenodo:publish-directory';
}

/**
 * Show a success 'page' with a link to Zenodo, hide other widget content
 *
 * @param doi - the doi to link to on Zenodo
 *
 * @returns void
 */
function show_success_div(
    doi : string,
    dev : boolean
  ){
    // Determine the appropriate URL
    var url_base;
    if (dev){
        url_base = "https://sandbox.zenodo.org/";
    } else {
        url_base = "https://zenodo.org/";
    }
    //Close the loading text
    var loading = document.getElementById("loading-div") as HTMLElement;
    loading.style.display = "None";
   
    //Get record id from doi
    let record_id = (doi.split('.')).pop();

    //Set up link
    var zenodo_button = document.getElementById("zenodo-button") as HTMLLinkElement;
    zenodo_button.target="_blank";
    var info_area = document.getElementById("info-area") as HTMLElement;
    info_area.innerHTML = "<h3> How is my code shared? </h3>"
                          + "Your code is now publicly accessible on"
                          + " <a class='link' href='"+url_base+"'>Zenodo</a> "
                          + "as a Zip file. It has been assigned a DOI"
                          + " (digital object identifier): " + doi + "."
                          + "<br>"
                          + "<h3> What if my code changes? </h3>"
                          + "If you make changes to your files, you can create"
                          + " a new version on Zenodo (which will be linked to the first)"
                          + " by clicking 'Update Zenodo Deposition' in the share menu.";
    
    zenodo_button.href = "https://sandbox.zenodo.org/record/"+record_id;

    //Show success text
    var success = document.getElementById("success-div") as HTMLElement;
    success.style.display = "Flex";
    return;
}

/**
 * Hide all HTML elements that are part of the widget
 *
 * @returns void
 */
function hide_all(){
    let submit_form = document.getElementById("submit-form") as HTMLElement;
    let outer_error = document.getElementById("outer-error-div") as HTMLElement;
    let success_div = document.getElementById("success-div") as HTMLElement;
    let loading_div = document.getElementById("loading-div") as HTMLElement;
    submit_form.style.display = "None";
    outer_error.style.display = "None";
    success_div.style.display = "None";
    loading_div.style.display = "None";
    return;
}

/**
 * Show error or success message depending on response from an upload request
 *
 * @param response - the response from the POST request
 *
 * @returns void
 */
function handleUploadResponse(
    response : Response
   ){
    var loading = document.getElementById("loading-div") as HTMLElement;

    //On error...
    if (response.status > 299) {
        return response.json().then(data => {
            //Hide the loading text
            loading.style.display = "None";

            //Show the form again, along with the error from the response data
            var form = document.getElementById("submit-form") as HTMLElement;
            form.style.display = "Block";
            let error = document.getElementById("form-error-div") as HTMLElement;
            error.innerHTML = "Error: "+data.message + ". Please try again.";
            return;
        });

    //On success...
    } else {
        return response.json().then(data => {
            //Redirect to wherever the configuratoin file wants
            if (data.redirect) {
                window.location.href = data.redirect
            } else {
                //If no redirect was specified, we can show a success screen with a link to Zenodo
                show_success_div(data.doi, data.dev);
            }
            return;
        });
    }
}

/**
 * Show error or success message depending on response from request
 *
 * @param response - the response from the POST request
 *
 * @returns void
 */
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
            show_success_div(doi, data.dev);
        });
    }
}
 
/**
 * Gather data from form and make a POST request to /zenodo/upload/
 *
 * @returns void
 */
function sendFormData(){
    //Hide form
    var form = document.getElementById('submit-form') as HTMLFormElement;
    form.style.display = "None";

    //Show loading text
    var loading = document.getElementById('loading-div') as HTMLElement;
    loading.style.display = "Block";

    //Convert form data to JSON
    var formData = new FormData(form);
    var formbody : { [key: string]: string } = {};
    formData.forEach(function(value,key){
        formbody[key] = value.toString();
    });
    var body_json = JSON.stringify(formbody);

    //Send a POST request with data
    var settings =ServerConnection.makeSettings()
    const parts = [settings.baseUrl, 'zenodo', 'upload']
    const fullURL = URLExt.join.apply(URLExt, parts);
    console.log("about to connect");
    ServerConnection.makeRequest(fullURL,
        {method: 'POST', body: body_json}, settings).then(
        response => { handleUploadResponse(response); });
}

/**
 * Create a new table row with an input block to add to a form
 *
 * @param label - text to label the input with
 *
 * @param id - HTML id for new table row
 *
 * @returns - table row HTML element containing a label and input
 */
function newInput(
    label: string,
    id: string,
    is_long: boolean,
    required: boolean
  ): HTMLElement {
    //Set up row
    let input_row = document.createElement('tr');
    input_row.id = id;

    //Use label to give user instructions
    let label_cell = document.createElement('th')
    label_cell.classList.add('label')

    //Add input cell
    let input_cell = document.createElement('td');
    let input = document.createElement('textarea');
    if (is_long){
        input.rows = 4
    } else {
        input.rows = 1 
        input.style.resize="none"
    }
    input.cols = 30

    let star = "<span style='color:red'>* </span>";
    if (required){
        label_cell.classList.add('required');
        input.required = true;
        label_cell.innerHTML = star + label + ": ";
    } else{
        label_cell.innerHTML = label + ": ";
    }
    
    input.name = id;
    input.id = id+'-input';
    input_cell.appendChild(input); 

    input_row.appendChild(label_cell); 
    input_row.appendChild(input_cell); 
    return input_row; 
}

/**
 * Activate the Zenodo front-end plugin
 *
 * NOTE: arguments must be in the same order as in the zenodoPlugin declaration
 */
function activateZenodoPlugin(
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    factory: IFileBrowserFactory,
    mainMenu: IMainMenu,
    settingRegistry: ISettingRegistry,
  ): void {

    //Set up widget (UI)
    const content = new Widget();
    const widget = new MainAreaWidget({content});
    widget.id = 'zenodo-jupyterlab';
    widget.title.label = 'Zenodo Upload'
    widget.title.closable = true;

    // Create main div for widget
    let main = document.createElement('div');
    main.id = "zenodo-upload-main";

    // Set up and append loading screen 
    let loading_div = document.createElement('div');
    loading_div.style.display = "None";
    loading_div.id = 'loading-div';
    loading_div.innerHTML = "Please wait... your files are being uploaded... ";
    main.appendChild(loading_div);

    // Set up and append success screen 
    let success_div = document.createElement('div');
    success_div.style.display = "None";
    success_div.id = 'success-div';
    success_div.innerHTML = "<h1> Congratulations, your files have been uploaded to Zenodo! </h1>";
    let tr1 = document.createElement("tr");
    let tr2 = document.createElement("tr");
    //Info about zenodo
    let td_info = document.createElement("td");
    let info_div = document.createElement("div");
    info_div.id = "info-area"
    //Button to view on Zenodo
    let zenodo_button = document.createElement("a"); 
    zenodo_button.innerHTML = "View on Zenodo";
    zenodo_button.id = "zenodo-button";
    zenodo_button.classList.add("basic-btn");
    let td_zenodo = document.createElement("td");
    //Attach all elements to main
    td_zenodo.appendChild(zenodo_button);
    td_info.appendChild(info_div);
    tr1.appendChild(td_zenodo);
    tr2.appendChild(td_info);
    success_div.appendChild(tr1);
    success_div.appendChild(tr2);
    main.appendChild(success_div);

    // Set up and append space for general errors
    let outer_error = document.createElement('p');
    outer_error.id = "outer-error-div";
    outer_error.style.color = "red";
    main.appendChild(outer_error);

    // Set up and append form to upload to Zenodo
    let upload_form = document.createElement('form');
    upload_form.id = 'submit-form';
    let form_table = document.createElement('table')
    let form_body = document.createElement('tbody')
    // Headers
    let header_row = document.createElement('tr')
    let header_data = document.createElement('th')
    header_data.colSpan = 2
    let header = document.createElement('h2');
    header.innerHTML = "Final Submission Details"
    header_data.appendChild(header)
    header_row.appendChild(header_data)
    form_body.appendChild(header_row);
    let subheader_row = document.createElement('tr')
    let subheader_data = document.createElement('th')
    subheader_data.colSpan = 2
    let subheader = document.createElement('div');
    subheader.innerHTML = 
        "<p> Please fill out the starred fields and then click 'Publish'"
        + " to publish to Zenodo.<br><span style='font-weight:bold'>"
        + " Note: </span> This will make your code publicly accessible on"
        + " <a class='link' href='http://zenodo.org'>zenodo.org<a> "
    subheader_data.appendChild(subheader)
    subheader_row.appendChild(subheader_data)
    form_body.appendChild(subheader_row);
    // Error messages
    let form_error_row = document.createElement('tr')
    let form_error_data = document.createElement('th')
    form_error_data.colSpan = 2
    let form_error = document.createElement('div');
    form_error.id = "form-error-div";
    form_error.style.color = "red";
    form_error_data.appendChild(form_error);
    form_error_row.appendChild(form_error_data);
    form_body.appendChild(form_error_row);
    // The actual form
    form_body.appendChild(newInput('Title','title', false, true));
    let authors = newInput('Author(s) <span class="hover">(Multiple?)</span>','author', false, true);
    authors.title = "If you have more than one author, enter their names and (below) their affiliations separated by commas"
    form_body.appendChild(authors)
    form_body.appendChild(newInput('Affiliation','affiliation', false, true));
    form_body.appendChild(newInput('Description','description', true, true));
    form_body.appendChild(newInput('Directory to publish (default is "work")',
                                   'directory', false, false));
    let access_token = newInput('Access token <span class="hover">(?)</span>',
                                'zenodo_token', false, false);
    access_token.title = "Developer access token for Zenodo's API (optional if this environment has a default)"
    form_body.appendChild(access_token)
    // Submit button
    let submit_row = document.createElement('tr')
    let submit_label = document.createElement('th')
    let submit_cell = document.createElement('td')
    let submit_button = document.createElement('input');
    submit_button.type = 'submit';
    submit_button.value = 'Publish';
    submit_button.classList.add("basic-btn");
    upload_form.addEventListener('submit', function (event) {
        event.preventDefault();
        sendFormData();
    });
    submit_cell.appendChild(submit_button);
    submit_row.appendChild(submit_label);
    submit_row.appendChild(submit_cell);
    form_body.appendChild(submit_row);

    // Attach everything to main
    form_table.appendChild(form_body);
    upload_form.appendChild(form_table);
    main.appendChild(upload_form);

    // Add main upload div to widget
    content.node.appendChild(main);

    // Add commands to the extension
    addZenodoCommands(app, palette, editorTracker, factory, mainMenu, settingRegistry, widget);
    return;
}

function open_widget(
    app: JupyterFrontEnd,
    widget: MainAreaWidget,
    shown_element: [string, string]
  ){
    //Make widget visible...
    if (!widget.isAttached){
        widget.title.label = 'Zenodo Upload'
        widget.title.closable = true;
        app.shell.add(widget, 'main');
    }
    //..and active
    app.shell.activateById(widget.id);
    hide_all();

    let elem = document.getElementById(shown_element[0]) as HTMLElement;
    elem.style.display = shown_element[1];
}


/*
 * Using arguments from 'activate' and the newly created widget, 
 *   create commands for each action and add them to appropriate menus 
 */
function addZenodoCommands(
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    factory: IFileBrowserFactory,
    mainMenu: IMainMenu,
    settingRegistry: ISettingRegistry,
    widget: MainAreaWidget
  ){
    const { tracker } = factory;

    //Command to publish from a directory
    app.commands.addCommand(CommandIDs.publish_directory, {
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
            //item.path gives the name of the directory selected
            let path = item.path;

            //Pre-set directory name and hide the relevant form field
            let dir_input = document.getElementById("directory-input") as HTMLInputElement;
            dir_input.value = path;
            let dir_row = document.getElementById("directory") as HTMLElement;
            dir_row.style.display = "None";

            open_widget(app, widget, ["submit-form","Block"]);
               //Show only the submit form
            //let submit_form = document.getElementById("submit-form") as HTMLElement;
            //submit_form.style.display = "Block";
        },
        iconClass: 'jp-MaterialIcon jp-FileUploadIcon',
    });

    //Command to upload any set of files
    app.commands.addCommand(CommandIDs.upload, {
        label: UPLOAD_LABEL,
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            console.log("uploading");
            open_widget(app, widget, ["submit-form","Block"]);
        },
    
    }); 

    app.commands.addCommand(CommandIDs.update, {
        label: 'Update Zenodo Deposition',
        isEnabled: () => true,
        isToggled: () => false, 
        iconClass: 'icon-class',
        execute: () => {
            open_widget(app, widget, ["loading-div","Flex"]);

            //Trigger POST request to /zenodo/update/
            var settings =ServerConnection.makeSettings()
            const parts = [settings.baseUrl, 'zenodo', 'update']
            const fullURL = URLExt.join.apply(URLExt, parts);

            ServerConnection.makeRequest(fullURL,
                {method: 'POST'}, settings).then(
                response => { handleUpdateResponse(response); });
        }

    }); 

    //Create sharing menu with 'upload' and 'update' commands
    const menu = new Menu({ commands: app.commands });
    
    menu.addItem({
        command: CommandIDs.upload
    });
    menu.addItem({
        command: CommandIDs.update
    });

    menu.title.label = 'Share';
    mainMenu.addMenu(menu, { rank: 20 });

    //Add commands to Command Palette
    palette.addItem({command: CommandIDs.upload, category: 'Sharing'})
    palette.addItem({command: CommandIDs.update, category: 'Sharing'})

    //Add context menu for directories with 'publish directory' command
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


