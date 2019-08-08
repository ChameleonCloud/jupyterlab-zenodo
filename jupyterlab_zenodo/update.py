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

    def get_last_upload(self):
        """Get information about the last upload

        Parameters
        ----------
        none

        Returns
        -------
        Dictionary
            Contains date, doi, directory, filename, and access token
        """
    
        no_uploads_error = ("No previous upload. Press 'Upload to Zenodo' "
                             "to create a new deposition")

        # If the database location doesn't exist, there are no uploads
        db_dest = "/work/.zenodo/"
        if not os.path.exists(db_dest):
            raise UserMistake(no_uploads_error)
            return

        # Connect to database
        conn = sqlite3.connect(db_dest+'zenodo.db')
        c = conn.cursor()

        # If the table is empty or doesn't exist, there are no uploads
        try:
            c.execute("SELECT date_uploaded, doi, directory, filename, "
                      "access_token FROM uploads ORDER BY date_uploaded DESC")
        except sqlite3.OperationalError:
            raise UserMistake(no_uploads_error)
            return
     

        # Fetch info, close connection
        rows = c.fetchall()
        conn.close()

        # Check that all data is there, fill in appropriately
        last_upload = rows[0]
        if any(map(lambda x : x is None, last_upload)):
            raise Exception("Not enough information in last upload")

        upload_data = {
            'date': last_upload[0],
            'doi': last_upload[1],
            'directory': last_upload[2],
            'filename': last_upload[3],
            'access_token': last_upload[4]
        }
        return upload_data


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
        print('old id: ' + str(record_id))
        deposition = Deposition(self.dev, access_token, record_id)
        deposition.new_version() 

        new_record_id = deposition.id
        print('new id: ' + str(new_record_id))

        # Get file information from new draft
        r = requests.get((base_url + '/deposit/depositions/' 
                         + new_record_id + '/files'),
                         params={'access_token': access_token})
        response_dict = r.json()
        print(response_dict)
        file_id = response_dict[0].get('id')

        if file_id is None:
            raise Exception("Something went wrong getting the last upload")
            
        # Delete the file
        r = requests.delete(base_url + '/deposit/depositions/'
                            + new_record_id + '/files/' + file_id, 
                            params={'access_token': access_token})
        
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
            upload_data = self.get_last_upload()

            filepath = upload_data['filename']
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
            print("Internal error:")
            print(x)
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
        
