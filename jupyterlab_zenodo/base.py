from notebook.base.handlers import APIHandler

from .config import ZenodoConfig
from .utils import add_query_parameter


class ZenodoBaseHandler(APIHandler):
    """
    A base handler for the Zenodo extension
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir
        c = ZenodoConfig(config=self.config)
        self.dev = c.dev
        self.access_token = c.access_token
        self.redirect = c.upload_redirect_url
        self.db_dest = c.database_location
        self.db_name = c.database_name
        self.community = c.community

    def return_creation_success(self, doi):
        """Package and return doi and upload_redirct (if applicable)
        Parameters
        ----------
        doi : string
            DOI of successfully created deposition

        Returns
        -------
        none
        """
        info = {'status': 'success', 'doi': doi, 'dev': self.dev}

        # If a redirect was specified in configuration, add doi as
        #   a query variable and send full url in the response
        if self.redirect:
            info['redirect'] = add_query_parameter(self.redirect, {'doi': doi})

        # Return info with a 201 status
        self.set_status(201)
        self.write(info)
        self.finish()

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
