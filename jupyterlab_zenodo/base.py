import os

from notebook.base.handlers import APIHandler

from .config import ZenodoConfig
from .utils import add_query_parameter


class ZenodoBaseHandler(APIHandler):
    @property
    def access_token(self):
        return self.zenodo_config.access_token

    @property
    def dev(self):
        return self.zenodo_config.dev
    
    @property
    def db_path(self):
        return os.path.join(
            self.zenodo_config.database_location, 
            self.zenodo_config.database_name)

    @property
    def community(self):
        return self.zenodo_config.community

    """
    A base handler for the Zenodo extension
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir
        self.zenodo_config = ZenodoConfig(config=self.config)


    def return_error(self, error_message):
        """Set 400 status and error message, return from request

        Parameters
        ----------
        error_message : string
            Message to be returned as reason for error

        Returns
        -------
        none
        """

        info = {
            'status': 'failure',
            'message':  error_message,
        }
        self.set_status(400)
        self.write(info)
        self.finish()
