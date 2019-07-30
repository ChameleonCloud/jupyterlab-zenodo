""" JupyterLab Zenodo : Exporting from JupyterLab to Zenodo """

from notebook.utils import url_path_join

from ._version import __version__
from .upload import ZenodoUploadHandler
from .status import ZenodoStatusHandler
# from .synctex import LatexSynctexHandler

path_regex = r'(?P<path>(?:(?:/[^/]+)+|/?))'

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
    print("Woauh! My extension has loaded!")
    web_app = nb_server_app.web_app
    # Prepend the base_url so that it works in a jupyterhub setting
    base_url = web_app.settings['base_url']
    base_endpoint = url_path_join(base_url, 'zenodo')
    upload_endpoint = url_path_join(base_endpoint, 'upload')
    status_endpoint = url_path_join(base_endpoint, 'status')
    # synctex = url_path_join(latex, 'synctex')

    handlers = [(upload_endpoint, ZenodoUploadHandler, {"notebook_dir": nb_server_app.notebook_dir}),(status_endpoint, ZenodoStatusHandler, {})]
    web_app.add_handlers('.*$', handlers)
                 # This dict might be where to add the access token
#                ,
#                (f'{synctex}{path_regex}',
#                 LatexSynctexHandler,
#                 {"notebook_dir": nb_server_app.notebook_dir}
#                 )
#                ]
