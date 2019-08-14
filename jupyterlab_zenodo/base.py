from notebook.base.handlers import APIHandler

from .config import ZenodoConfig

class ZenodoBaseHandler(APIHandler):
    """
    A base handler for the Zenodo extension
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir
        c = ZenodoConfig(config=self.config)
        self.dev = c.dev
        self.access_token = c.access_token
        self.dev_access_token = c.dev_access_token
        self.upload_redirect = c.upload_redirect_url
        self.db_dest = c.database_location
        self.db_name = c.database_name
        self.community = c.community


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
            'status':'failure',
            'message': error_message,
        }
        self.set_status(400)
        self.write(info)
        self.finish()
