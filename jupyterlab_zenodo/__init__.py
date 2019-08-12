""" JupyterLab Zenodo : Exporting from JupyterLab to Zenodo """

from notebook.utils import url_path_join

from ._version import __version__
from .upload import ZenodoUploadHandler
from .update import ZenodoUpdateHandler
from .status import ZenodoStatusHandler
# from .synctex import LatexSynctexHandler

def _jupyter_server_extension_paths():
    return [{
        'module': 'jupyterlab_zenodo'
    }]

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.
    Args:
        nb_server_app (NotebookApp): handle to the Notebook webserver instance.
    """
    print("The Zenodo extension has loaded")
    web_app = nb_server_app.web_app
    # Prepend the base_url so that it works in a jupyterhub setting
    base_url = web_app.settings['base_url']
    base_endpoint = url_path_join(base_url, 'zenodo')
    upload_endpoint = url_path_join(base_endpoint, 'upload')
    status_endpoint = url_path_join(base_endpoint, 'status')
    update_endpoint = url_path_join(base_endpoint, 'update')

    handlers = [(upload_endpoint, ZenodoUploadHandler, {"notebook_dir": nb_server_app.notebook_dir}),(status_endpoint, ZenodoStatusHandler, {}),(update_endpoint, ZenodoUpdateHandler, {})]
    web_app.add_handlers('.*$', handlers)