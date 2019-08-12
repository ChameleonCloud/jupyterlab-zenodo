""" JupyterLab Zenodo : Updating Zenodo Deposition """

from datetime import datetime
import logging
import os
import requests
import sqlite3

from notebook.base.handlers import APIHandler
from tornado import gen, web

from .base import ZenodoBaseHandler
from .utils import get_id, store_record, UserMistake, zip_dir
from .zenodo import Deposition

LOG = logging.getLogger(__name__)

class ZenodoUpdateHandler(ZenodoBaseHandler):
    """
    A handler that updates your files on Zenodo
    """
    def initialize(self, dev=False):
        self.dev = dev


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
        db_dest = "/work/.zenodo/"

        try:
            # Try to complete update
            upload_data = get_last_upload(db_dest)
            new_filepath = zip_dir(upload_data['directory'],
                upload_data['filepath'].split('/')[-1])
            doi = self.update_file(new_filepath, get_id(upload_data['doi']), 
                upload_data['access_token'])

        except UserMistake as e:
            # UserMistake exceptions contain messages for the user
            self.return_error(str(e))
        except Exception as x:
            # All other exceptions are internal
            LOG.exception("There was an error!")
            return
        else:
            self.set_status(201)
            self.write({'status':'success', 'doi':doi})
            store_record(db_dest, doi, new_filepath, upload_data['directory'],
                upload_data['access_token'])
            self.finish()

def get_last_upload(db_dest):
    """Get information about the last upload
    Parameters
    ----------
    db_dest : string
        Supposed location of sqlite database with upload information

    Returns
    -------
    Dictionary
        Contains date, doi, directory, filepath, and access token
    """

    no_uploads_error = ("No previous upload. Press 'Upload to Zenodo' "
                         "to create a new deposition")
    # If the database location doesn't exist, there are no uploads
    if not os.path.exists(db_dest):
        LOG.warning("No db folder")
        raise UserMistake(no_uploads_error)

    # Connect to database
    conn = sqlite3.connect(db_dest+'zenodo.db')
    c = conn.cursor()
    # If the table is empty or doesn't exist, there are no uploads
    try:
        c.execute("SELECT date_uploaded, doi, directory, filepath, access_token"
                  " FROM uploads ORDER BY date_uploaded DESC")
    except sqlite3.OperationalError as e:
        raise UserMistake(no_uploads_error)
     
    # Fetch info, close connection
    last_upload = c.fetchone()
    conn.close()

    if last_upload == []:
        LOG.warn("data is empty: "+str(data))
        raise UserMistake(no_uploads_error)

    if any(map(lambda x : x == '', last_upload)):
        raise Exception("Missing information in last upload: empty values")

    labels = ['date','doi','directory','filepath','access_token']
    return dict(zip(labels, last_upload))

