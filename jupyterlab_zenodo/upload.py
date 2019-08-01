""" JupyterLab Zenodo : Exporting from JupyterLab to Zenodo """

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
from .utils import zip_dir, get_id, store_record

class ZenodoUploadHandler(ZenodoBaseHandler):
    """
    A handler that uploads your files to Zenodo
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir

    def return_error(self, error_message):
        info = {
            'status':'failure',
            'message': error_message,
            'doi' : None
        }
        self.set_status(400)
        self.write(json.dumps(info))
        self.finish()
        return

    def assemble_metadata(self, title, authors, description):
        """Turn metadata into a dictionary for Zenodo upload

        Parameters
        ----------
        title : string
        authors : list of strings
        description : string

        Returns
        -------
        dictionary
            Dictionary fields are left empty if not provided

        """
        # Turn list of author strings into list of author dictionaries
        creator_list = []
        for author in authors:
            creator_list.append({'name': author, 'affiliation': 'Chameleon Cloud'})

        metadata = {}
        metadata['title'] = title 
        metadata['upload_type'] = 'publication' 
        metadata['publication_type'] = 'workingpaper'
        metadata['description'] = description 
        metadata['creators'] = creator_list 
        return metadata

    def upload_file(self, path_to_file, metadata, access_token):
        """Upload the given file at the given path to Zenodo
           Add included metadata

        Parameters
        ----------
        path_to_file : string
            Path to the file to be uploaded (including file name)
        metadata : dictionary
            As generated by assemble_metadata()
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

        ACCESS_TOKEN = access_token
        headers = {"Content-Type": "application/json"}
        # Create deposition
        r = requests.post('https://zenodo.org/api/deposit/depositions',
                          params={'access_token': ACCESS_TOKEN}, json={},
                          headers=headers)
        deposition_id = r.json()['id']
        data = {'filename': path_to_file.split('/')[-1]}
        files = {'file': open(path_to_file, 'rb')}
        r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                          params={'access_token': ACCESS_TOKEN}, data=data,
                          files=files)
        r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
                         params={'access_token': ACCESS_TOKEN}, 
                         data=json.dumps({'metadata': metadata}),
                         headers=headers)
        r_dict = r.json()
        doi = r_dict.get('doi') 
        if not doi:
            doi = r_dict.get('metadata',{}).get('prereserve_doi',{}).get('doi')
        return doi
    
    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        print("In GET routine for upload handler")
        info = {'status':'executed get', 'doi':"no doi here"}
        self.set_status(200)
        self.write(json.dumps(info))
        self.finish()

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):

        """
        Takes in a a file prefix string, and metadata
        Zips notebook_dir to filename.zip, uploads to Zenodo
        Returns dictionary with status (success or failure) and doi (if successful)
        """
        self.check_xsrf_cookie()

        request_data = json.loads(self.request.body.decode("utf-8"))
        
        # Get basic metadata from form response
        title = request_data['title']
        filename = request_data['filename']
        authors = request_data['author']
        description = request_data['description']

        # Zenodo requires each field to be at least 4 characters long
        if any([len(title) <= 3, len(authors) <=3, len(description) <= 3]):
            msg = "Title, author, and description fields must all be filled in and at least four characters long"
            self.return_error(msg)
            return

        # Make sure a filename has been provided
        if len(filename) < 1:
           self.return_error("Please provide a name for the zip file")
            

        our_access_token = '***REMOVED***'
        # If the user has no access token, use ours
        access_token = request_data.get('zenodo_token') or our_access_token
        # If the user hasn't specified a directory, use 'work'
        directory_to_zip = request_data.get('directory') or 'work'
            

        try:
            path_to_file = zip_dir(directory_to_zip, filename)
            metadata = self.assemble_metadata(title, authors, description)
            doi = self.upload_file(path_to_file, metadata, access_token) 
        except Exception as e:
            self.return_error(str(e))
            return

        if (doi is not None):
            info = {'status':'success', 'doi':doi}
            print("doi: "+str(doi))
            self.set_status(201)
            self.write(json.dumps(info))
            store_record(doi, filename, directory_to_zip, access_token)
            #self.redirect("http://127.0.0.1:7000/portal/upload/"+doi)
            self.finish()
        else:
            self.return_error("There was an error uploading to Zenodo")
            return
        
