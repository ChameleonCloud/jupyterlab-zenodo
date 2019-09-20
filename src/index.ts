import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';

import { ISettingRegistry } from '@jupyterlab/coreutils';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { IEditorTracker } from '@jupyterlab/fileeditor';

import { Widget, Menu } from '@phosphor/widgets';

import { ServerConnection } from '@jupyterlab/services';

import { URLExt } from '@jupyterlab/coreutils';

const zenodoPluginId = '@chameleoncloud/jupyterlab_zenodo:plugin';

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
    ISettingRegistry
  ],
  activate: activateZenodoPlugin,
  autoStart: true
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
 * Show a success 'page' with a link to Zenodo, hide other widget content
 *
 * @param doi - the doi to link to on Zenodo
 *
 * @returns void
 */
function showSuccessDiv(doi: string, dev: boolean) {
  // Determine the appropriate URL
  let urlBase;
  if (dev) {
    urlBase = 'https://sandbox.zenodo.org/';
  } else {
    urlBase = 'https://zenodo.org/';
  }
  // Close the loading text
  let loading = document.getElementById('loading-div') as HTMLElement;
  loading.style.display = 'None';

  // Get record id from doi
  let recordId = doi.split('.').pop();

  // Set up link
  let zenodoButton = document.getElementById(
    'zenodo-button'
  ) as HTMLLinkElement;
  zenodoButton.target = '_blank';
  let infoArea = document.getElementById('info-area') as HTMLElement;
  infoArea.innerHTML =
    '<h3> How is my code shared? </h3>' +
    'Your code is now publicly accessible on' +
    " <a class='link' href='" +
    urlBase +
    "'>Zenodo</a> " +
    'as a Zip file. It has been assigned a DOI' +
    ' (digital object identifier): ' +
    doi +
    '.' +
    '<br>' +
    '<h3> What if my code changes? </h3>' +
    'If you make changes to your files, you can create' +
    ' a new version on Zenodo (which will be linked to the first)' +
    " by clicking 'Update Zenodo Deposition' in the share menu.";

  zenodoButton.href = 'https://sandbox.zenodo.org/record/' + recordId;

  // Show success text
  let success = document.getElementById('success-div') as HTMLElement;
  success.style.display = 'Flex';
  return;
}

/**
 * Hide all HTML elements that are part of the widget
 *
 * @returns void
 */
function hideAll() {
  let submitForm = document.getElementById('submit-form') as HTMLElement;
  let outerError = document.getElementById('outer-error-div') as HTMLElement;
  let successDiv = document.getElementById('success-div') as HTMLElement;
  let loadingDiv = document.getElementById('loading-div') as HTMLElement;
  submitForm.style.display = 'None';
  outerError.style.display = 'None';
  successDiv.style.display = 'None';
  loadingDiv.style.display = 'None';
  return;
}

/**
 * Show error or success message depending on response from an upload request
 *
 * @param response - the response from the POST request
 *
 * @returns void
 */
function handleUploadResponse(response: Response) {
  let loading = document.getElementById('loading-div') as HTMLElement;

  // On error...
  if (response.status > 299) {
    return response.json().then(data => {
      // Hide the loading text
      loading.style.display = 'None';

      // Show the form again, along with the error from the response data
      let form = document.getElementById('submit-form') as HTMLElement;
      form.style.display = 'Block';
      let error = document.getElementById('form-error-div') as HTMLElement;
      error.innerHTML = 'Error: ' + data.message + '. Please try again.';
      return;
    });

    // On success...
  } else {
    return response.json().then(data => {
      // Redirect to wherever the configuratoin file wants
      if (data.redirect) {
        window.location.href = data.redirect;
      } else {
        // If no redirect was specified, we can show a success screen with a link to Zenodo
        showSuccessDiv(data.doi, data.dev);
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
function handleUpdateResponse(response: Response) {
  console.log('status', response.status);
  let loading = document.getElementById('loading-div') as HTMLElement;

  if (response.status > 299) {
    return response.json().then(data => {
      let error = document.getElementById('outer-error-div') as HTMLElement;
      loading.style.display = 'None';
      error.style.display = 'Block';
      error.innerHTML = 'Error: ' + data.message + '. Please try again.';
    });
  } else {
    return response.json().then(data => {
      let doi = data.doi;
      showSuccessDiv(doi, data.dev);
    });
  }
}

/**
 * Gather data from form and make a POST request to /zenodo/upload/
 *
 * @returns void
 */
function sendFormData() {
  // Hide form
  let form = document.getElementById('submit-form') as HTMLFormElement;
  form.style.display = 'None';

  // Show loading text
  let loading = document.getElementById('loading-div') as HTMLElement;
  loading.style.display = 'Block';

  // Convert form data to JSON
  let formData = new FormData(form);
  let formbody: { [key: string]: string } = {};
  formData.forEach(function(value, key) {
    formbody[key] = value.toString();
  });
  let body = JSON.stringify(formbody);

  // Send a POST request with data
  let settings = ServerConnection.makeSettings();
  const parts = [settings.baseUrl, 'zenodo', 'upload'];
  const fullURL = URLExt.join.apply(URLExt, parts);
  console.log('about to connect');
  ServerConnection.makeRequest(
    fullURL,
    { method: 'POST', body },
    settings
  ).then(response => {
    handleUploadResponse(response);
  });
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
  isLong: boolean,
  required: boolean
): HTMLElement {
  // Set up row
  let inputRow = document.createElement('tr');
  inputRow.id = id;

  // Use label to give user instructions
  let labelCell = document.createElement('th');
  labelCell.classList.add('label');

  // Add input cell
  let inputCell = document.createElement('td');
  let input = document.createElement('textarea');
  if (isLong) {
    input.rows = 4;
  } else {
    input.rows = 1;
    input.style.resize = 'none';
  }
  input.cols = 30;

  let star = "<span style='color:red'>* </span>";
  if (required) {
    labelCell.classList.add('required');
    input.required = true;
    labelCell.innerHTML = star + label + ': ';
  } else {
    labelCell.innerHTML = label + ': ';
  }

  input.name = id;
  input.id = id + '-input';
  inputCell.appendChild(input);

  inputRow.appendChild(labelCell);
  inputRow.appendChild(inputCell);
  return inputRow;
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
  settingRegistry: ISettingRegistry
): void {
  // Set up widget (UI)
  const content = new Widget();
  const widget = new MainAreaWidget({ content });
  widget.id = 'zenodo-jupyterlab';
  widget.title.label = 'Zenodo Upload';
  widget.title.closable = true;

  // Create main div for widget
  let main = document.createElement('div');
  main.id = 'zenodo-upload-main';

  // Set up and append loading screen
  let loadingDiv = document.createElement('div');
  loadingDiv.style.display = 'None';
  loadingDiv.id = 'loading-div';
  loadingDiv.innerHTML = 'Please wait... your files are being uploaded... ';
  main.appendChild(loadingDiv);

  // Set up and append success screen
  let successDiv = document.createElement('div');
  successDiv.style.display = 'None';
  successDiv.id = 'success-div';
  successDiv.innerHTML =
    '<h1> Congratulations, your files have been uploaded to Zenodo! </h1>';
  let tr1 = document.createElement('tr');
  let tr2 = document.createElement('tr');
  // Info about zenodo
  let tdInfo = document.createElement('td');
  let infoDiv = document.createElement('div');
  infoDiv.id = 'info-area';
  // Button to view on Zenodo
  let zenodoButton = document.createElement('a');
  zenodoButton.innerHTML = 'View on Zenodo';
  zenodoButton.id = 'zenodo-button';
  zenodoButton.classList.add('basic-btn');
  let tdZenodo = document.createElement('td');
  // Attach all elements to main
  tdZenodo.appendChild(zenodoButton);
  tdInfo.appendChild(infoDiv);
  tr1.appendChild(tdZenodo);
  tr2.appendChild(tdInfo);
  successDiv.appendChild(tr1);
  successDiv.appendChild(tr2);
  main.appendChild(successDiv);

  // Set up and append space for general errors
  let outerError = document.createElement('p');
  outerError.id = 'outer-error-div';
  outerError.style.color = 'red';
  main.appendChild(outerError);

  // Set up and append form to upload to Zenodo
  let uploadForm = document.createElement('form');
  uploadForm.id = 'submit-form';
  let formTale = document.createElement('table');
  let formBody = document.createElement('tbody');
  // Headers
  let headerRow = document.createElement('tr');
  let headerData = document.createElement('th');
  headerData.colSpan = 2;
  let header = document.createElement('h2');
  header.innerHTML = 'Final Submission Details';
  headerData.appendChild(header);
  headerRow.appendChild(headerData);
  formBody.appendChild(headerRow);
  let subheaderRow = document.createElement('tr');
  let subheaderData = document.createElement('th');
  subheaderData.colSpan = 2;
  let subheader = document.createElement('div');
  subheader.innerHTML =
    "<p> Please fill out the starred fields and then click 'Publish'" +
    " to publish to Zenodo.<br><span style='font-weight:bold'>" +
    ' Note: </span> This will make your code publicly accessible on' +
    " <a class='link' href='http://zenodo.org'>zenodo.org<a> ";
  subheaderData.appendChild(subheader);
  subheaderRow.appendChild(subheaderData);
  formBody.appendChild(subheaderRow);
  // Error messages
  let formErrorRow = document.createElement('tr');
  let formErrorData = document.createElement('th');
  formErrorData.colSpan = 2;
  let formError = document.createElement('div');
  formError.id = 'form-error-div';
  formError.style.color = 'red';
  formErrorData.appendChild(formError);
  formErrorRow.appendChild(formErrorData);
  formBody.appendChild(formErrorRow);
  // The actual form
  formBody.appendChild(newInput('Title', 'title', false, true));
  let authors = newInput(
    'Author(s) <span class="hover">(Multiple?)</span>',
    'author',
    false,
    true
  );
  authors.title =
    'If you have more than one author, enter their names and (below) their affiliations separated by commas';
  formBody.appendChild(authors);
  formBody.appendChild(newInput('Affiliation', 'affiliation', false, true));
  formBody.appendChild(newInput('Description', 'description', true, true));
  formBody.appendChild(
    newInput(
      'Directory to publish (default is "/work")',
      'directory',
      false,
      false
    )
  );
  let accessToken = newInput(
    'Access token <span class="hover">(?)</span>',
    'zenodo_token',
    false,
    false
  );
  accessToken.title =
    "Developer access token for Zenodo's API (optional if this environment has a default)";
  formBody.appendChild(accessToken);
  // Submit button
  let submitRow = document.createElement('tr');
  let submitLabel = document.createElement('th');
  let submitCell = document.createElement('td');
  let submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'Publish';
  submitButton.classList.add('basic-btn');
  uploadForm.addEventListener('submit', function(event) {
    event.preventDefault();
    sendFormData();
  });
  submitCell.appendChild(submitButton);
  submitRow.appendChild(submitLabel);
  submitRow.appendChild(submitCell);
  formBody.appendChild(submitRow);

  // Attach everything to main
  formTale.appendChild(formBody);
  uploadForm.appendChild(formTale);
  main.appendChild(uploadForm);

  // Add main upload div to widget
  content.node.appendChild(main);

  // Retrive settings
  Promise.all([settingRegistry.load(zenodoPluginId), app.restored])
    .then(([settings]) => {
      // Set the label for the upload command
      let uploadLabel = settings.get('uploadTitle').composite as string;

      // Add commands to the extension, including the 'upload' command
      addZenodoCommands(
        app,
        palette,
        editorTracker,
        factory,
        mainMenu,
        settingRegistry,
        widget,
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
  widget: MainAreaWidget,
  shownElement: [string, string]
) {
  // Make widget visible...
  if (!widget.isAttached) {
    widget.title.label = 'Zenodo Upload';
    widget.title.closable = true;
    app.shell.add(widget, 'main');
  }
  // ..and active
  app.shell.activateById(widget.id);
  hideAll();

  let elem = document.getElementById(shownElement[0]) as HTMLElement;
  elem.style.display = shownElement[1];
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
  widget: MainAreaWidget,
  uploadLabel: string
) {
  console.log('adding commands');
  const { tracker } = factory;

  // Command to publish from a directory
  app.commands.addCommand(CommandIDs.publishDirectory, {
    label: uploadLabel,
    isEnabled: () => true,
    isToggled: () => false,
    execute: () => {
      if (!tracker.currentWidget) {
        return;
      }

      const item = tracker.currentWidget.selectedItems().next();
      if (!item) {
        return;
      }
      // item.path gives the name of the directory selected
      let path = item.path;

      // Pre-set directory name and hide the relevant form field
      let dirInput = document.getElementById(
        'directory-input'
      ) as HTMLInputElement;
      dirInput.value = path;
      let dirRow = document.getElementById('directory') as HTMLElement;
      dirRow.style.display = 'None';

      openWidget(app, widget, ['submit-form', 'Block']);
      // Show only the submit form
      // let submitForm = document.getElementById("submit-form") as HTMLElement;
      // submitForm.style.display = "Block";
    },
    iconClass: 'jp-MaterialIcon jp-FileUploadIcon'
  });

  // Command to upload any set of files
  app.commands.addCommand(CommandIDs.upload, {
    label: uploadLabel,
    isEnabled: () => true,
    isToggled: () => false,
    iconClass: 'icon-class',
    execute: () => {
      console.log('uploading');
      openWidget(app, widget, ['submit-form', 'Block']);
    }
  });

  app.commands.addCommand(CommandIDs.update, {
    label: 'Update Zenodo Deposition',
    isEnabled: () => true,
    isToggled: () => false,
    iconClass: 'icon-class',
    execute: () => {
      openWidget(app, widget, ['loading-div', 'Flex']);

      // Trigger POST request to /zenodo/update/
      let settings = ServerConnection.makeSettings();
      const parts = [settings.baseUrl, 'zenodo', 'update'];
      const fullURL = URLExt.join.apply(URLExt, parts);

      ServerConnection.makeRequest(fullURL, { method: 'POST' }, settings).then(
        response => {
          handleUpdateResponse(response);
        }
      );
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
  zenodoPlugin
];

export default plugins;
