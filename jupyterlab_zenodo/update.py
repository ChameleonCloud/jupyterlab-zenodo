""" JupyterLab Zenodo : Updating Zenodo Deposition """

import logging
import os
import requests

from notebook.base.handlers import APIHandler
from tornado import gen, web

from .base import ZenodoBaseHandler
from .database import get_last_upload, store_record
from .utils import get_id, UserMistake, zip_dir
from .zenodo import Deposition

LOG = logging.getLogger(__name__)


class ZenodoUpdateHandler(ZenodoBaseHandler):
    """
    A handler that updates your files on Zenodo
    """
    def update_file(self, path_to_file, record_id, access_token):
        """Upload the given file at the given path to Zenodo
           Add included metadata

        Parameters
        ----------
        path_to_file : string
            Path to the file to upload (including file name)
        record_id : string
            Record id of previous version
        access_token : string
            Zenodo API token

        Returns
        -------
        string
            Doi of successfully uploaded deposition

        Notes
        -----
        - Currently, base url is zenodo sandbox
        """
        # Create new version
        deposition = Deposition(self.dev, access_token, record_id)
        deposition.new_version()
        deposition.clear_files()
        deposition.set_file(path_to_file)
        deposition.publish()
        return deposition.doi

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        """
        Updates Zenodo deposition with new files, if possible
        """
        self.check_xsrf_cookie()

        try:
            # Try to complete update
            upload_data = get_last_upload(self.db_path)
            directory = os.path.join(self.notebook_dir, upload_data['directory'])
            archive = zip_dir(directory)
            doi = self.update_file(archive, get_id(upload_data['doi']),
                                   upload_data['access_token'])

        except UserMistake as e:
            # UserMistake exceptions contain messages for the user
            self.return_error(str(e))
        except Exception as x:
            # All other exceptions are internal
            LOG.exception("There was an error!")
            return
        else:
            # Record the deposition creation and return success
            store_record(doi, upload_data['directory'], self.db_path)
            self.return_creation_success(doi)
