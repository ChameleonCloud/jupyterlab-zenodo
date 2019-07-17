import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';


/**
 * Initialization data for the jupyterlab_zenodo extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_zenodo',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyterlab_zenodo is activated!');
  }
};

export default extension;
