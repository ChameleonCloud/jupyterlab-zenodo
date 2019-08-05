""" JupyterLab Zenodo : Updating Zenodo Deposition """

import cgi
import glob, json, re, os
import requests
import sqlite3
from urllib.parse import unquote_plus, parse_qsl
from datetime import datetime
from contextlib import contextmanager

from tornado import escape, gen, web

from notebook.base.handlers import APIHandler

from .base import ZenodoBaseHandler
from .utils import get_id, store_record, zip_dir

class ZenodoUpdateHandler(ZenodoBaseHandler):
    """
    A handler that updates your files on Zenodo
    """
    def initialize(self):
        print("I'm the update handler")

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

        db_dest = "/work/.zenodo/"
        if not os.path.exists(db_dest):
            raise Exception("No previous upload. Please press 'Upload to Zenodo' to create a new deposition'")
        conn = sqlite3.connect(db_dest+'zenodo.db')
        c = conn.cursor()

        try:
            c.execute("SELECT date_uploaded, doi, directory, filename, access_token FROM uploads ORDER BY date_uploaded DESC")
        except sqlite3.OperationalError:
            raise Exception("There are no previous uplaods. To upload to Zenodo for the first time you need to select 'Upload to Zenodo'")
     
        rows = c.fetchall()
        # Close connection
        conn.close()
        print(rows[0])
        last_upload = rows[0]
        if any(map(lambda x : x is None, last_upload)):
            raise Exception("Not enough information in last upload")
        # true if empty; want to see if any are empty, that's an error
        upload_data = {
            'date': last_upload[0],
            'doi': last_upload[1],
            'directory': last_upload[2],
            'filename': last_upload[3],
            'access_token': last_upload[4]
        }

        print(upload_data)
        return upload_data


    def update_file(self, filename, path_to_file, record_id, access_token):
        """Upload the given file at the given path to Zenodo
           Add included metadata

        Parameters
        ----------
        filename : string
            File to upload
        path_to_file : string
            Path to the file to upload (including file name)
        record_id : string
            Doi of new version
        access_token : string
            Zenodo API token

        Returns
        -------
        string
            Doi of successfully uploaded deposition
                
        Notes
        -----
        - Does not yet have ANY error handling
    
        """

        #TODO: remove 'sandbox' before deployment
        base_url = 'https://sandbox.zenodo.org/api'

        deposition_id = record_id

        # Create new version
        r = requests.post(base_url + '/deposit/depositions/'+record_id 
                            +'/actions/newversion',
                          params={'access_token': access_token})
        response_dict = r.json()
        deposition_id = response_dict['links']['latest_draft'].split('/')[-1]
        # Check response
        print(response_dict)

        r = requests.get(base_url + '/deposit/depositions/'+record_id+'/files',
                 params={'access_token': access_token})
        response_dict = r.json()
        file_id = response_dict[0]['id']
        # TODO: get file id

        # Use this to delete the file
        r = requests.delete(base_url + '/deposit/depositions/' + deposition_id + '/files/' + file_id, params={'access_token': access_token})

        # Organize file data
        data = {'filename': path_to_file.split('/')[-1]}
        files = {'file': open(path_to_file, 'rb')}

        # Upload new file
        r = requests.post(base_url + '/deposit/depositions/%s/files'
                             % deposition_id,
                          params={'access_token': access_token}, data=data,
                          files=files)

        # Re-publish deposition
        r = requests.post(base_url + '/deposit/depositions/%s/actions/publish'
                            % deposition_id,
                          params={'access_token': access_token})
        r_dict = r.json()
        print(r_dict)
        if r_dict['status'] == 400:
            if r_dict['errors'][0]['code'] == 10:
                print("the thing happened")
                raise Exception("You need to update some of your files before trying to update your deposition on Zenodo")
            else:
                raise Exception("Something went wrong with Zenodo")

        # Get doi (or prereserve doi)
        doi = r_dict.get('doi') 
        if not doi:
            doi = r_dict.get('metadata',{}).get('prereserve_doi',{}).get('doi')
        print("doi: "+str(doi))
        return doi
    
    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        print("In GET routine for update handler")
        
        self.get_last_upload()
        info = {'status':'executed get in update', 'doi':"no doi here"}
        self.set_status(200)
        self.write(json.dumps(info))
        self.finish()

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        self.check_xsrf_cookie()
        print("In POST routine for update handler")

        """
        Takes in a a file prefix string
        Zips notebook_dir to file_prefix.zip, updates on Zenodo
        Returns dictionary with status (success or failure)
        """

        """
        In order to update a zenodo deposition, we need to:
        1. make a new version request
          r.requests.post(base_url + '/deposit/depositions/'+record+'/actions/newversion', params={'access_token': ACCESS_TOKEN})
        2. Upload file to that

        """

        doi = ''
        try:
            upload_data = self.get_last_upload()

            filename = upload_data['filename']
            directory = upload_data['directory']
            record_id = get_id(upload_data['doi']) 
            access_token = upload_data['access_token']
            zip_dir(directory, filename)

            doi = self.update_file(filename, directory+'/../'+filename, record_id, access_token)
        except Exception as e:
            print("In update POST: returning error")
            self.return_error(str(e))
            return

        if (doi is not None):
            info = {'status':'success', 'doi':doi}
            print("doi: "+str(doi))
            self.set_status(201)
            self.write(json.dumps(info))
            store_record(doi, filename, directory, access_token)
            #self.redirect("http://127.0.0.1:7000/portal/upload/"+doi)
            self.finish()
        else:
            info = {'status':'failure', 'doi': None}
            print("no doi")
            self.set_status(404)
            self.write(json.dumps(info))
            self.finish()
        
