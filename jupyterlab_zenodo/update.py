""" JupyterLab Zenodo : Updating Zenodo Deposition """

from datetime import datetime
import json
import os
import requests
import sqlite3

from notebook.base.handlers import APIHandler
from tornado import gen, web

from .base import ZenodoBaseHandler
from .utils import get_id, store_record, UserMistake, zip_dir
from .zenodo import Deposition

class ZenodoUpdateHandler(ZenodoBaseHandler):
    """
    A handler that updates your files on Zenodo
    """
    def initialize(self):
        #TODO: change dev to False before deployment
        self.dev = True


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

        #TODO: remove 'sandbox' before deployment
        base_url = 'https://sandbox.zenodo.org/api'

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

            filepath = upload_data['filepath']
            directory = upload_data['directory']
            record_id = get_id(upload_data['doi']) 
            access_token = upload_data['access_token']

            new_filepath = zip_dir(directory, filepath.split('/')[-1])

            doi = self.update_file(new_filepath, record_id, access_token)
        except UserMistake as e:
            # UserMistake exceptions contain messages for the user
            self.return_error(str(e))
        except Exception as x:
            # All other exceptions are internal
            print("Internal error: "+str(x))
            self.return_error("Something went wrong")
            return
        else:
            # If nothing has gone wrong, return the doi if it exists
            if (doi is not None):
                info = {'status':'success', 'doi':doi}
                self.set_status(201)
                self.write(json.dumps(info))
                store_record(doi, new_filepath, directory, access_token)
                self.finish()
            else:
                info = {'status':'failure', 'doi': None}
                self.set_status(404)
                self.write(json.dumps(info))
                self.finish()

def process_upload_data(upload_data): 
    """Verify and package data about the last upload

    Parameters
    ----------
    upload_data : list of lists of strings
        Contains all upload information 

    Returns
    -------
    Dictionary
        Contains date, doi, directory, filepath, and access token

    Notes
    -----
    - Raises exception on failure
    """
    # Check that all data is there, fill in appropriately
    last_upload = upload_data[0]

    if len(last_upload) != 5:
        raise Exception("Missing information in last upload: too few fields")
    if any(map(lambda x : len(x) == '', last_upload)):
        raise Exception("Missing information in last upload: empty values")

    upload_data = {
        'date': last_upload[0],
        'doi': last_upload[1],
        'directory': last_upload[2],
        'filepath': last_upload[3],
        'access_token': last_upload[4]
    }
    return upload_data


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
        raise UserMistake(no_uploads_error)
        print("No db folder")
        return
    # Connect to database
    conn = sqlite3.connect(db_dest+'zenodo.db')
    c = conn.cursor()
    # If the table is empty or doesn't exist, there are no uploads
    try:
        c.execute("SELECT date_uploaded, doi, directory, filepath, access_token"
                  " FROM uploads ORDER BY date_uploaded DESC")
    except sqlite3.OperationalError as e:
        raise UserMistake(no_uploads_error)
        return
     
    # Fetch info, close connection
    data = c.fetchall()
    conn.close()

    if data == []:
        print("data is empty: "+str(data))
        raise UserMistake(no_uploads_error)

    return process_upload_data(data)

