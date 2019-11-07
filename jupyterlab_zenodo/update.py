""" JupyterLab Zenodo : Updating Zenodo Deposition """

import logging
import os
import requests

from notebook.base.handlers import APIHandler
from tornado import gen, web

from .base import ZenodoBaseHandler
from .database import get_last_upload, store_record
from .utils import add_query_parameter, get_id, UserMistake, zip_dir
from .zenodo import Deposition

LOG = logging.getLogger(__name__)


class ZenodoUpdateHandler(ZenodoBaseHandler):
    """
    A handler that updates your files on Zenodo
    """
    def update_file(self, path_to_file, record_id):
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
        deposition = Deposition(self.dev, self.access_token, record_id)
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
            doi = self.update_file(archive, get_id(upload_data['doi']))

        except UserMistake as e:
            # UserMistake exceptions contain messages for the user
            self.return_error(str(e))
        except Exception:
            # All other exceptions are internal
            LOG.exception("There was an error!")
            return
        else:
            # Record the deposition creation and return success
            store_record(doi, upload_data['directory'], self.db_path)

            info = dict(status='success', doi=doi, previous_doi=upload_data['doi'])

            redirect = self.zenodo_config.update_redirect_url
            if redirect:
                info['redirect'] = add_query_parameter(redirect, info)
            
            self.set_status(200)
            self.write(info)
            self.finish()
