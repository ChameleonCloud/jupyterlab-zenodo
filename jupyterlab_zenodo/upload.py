""" JupyterLab Zenodo : Exporting from JupyterLab to Zenodo """

import glob, json, re, os
import requests
import sqlite3
from datetime import datetime
from contextlib import contextmanager

from tornado import gen, web

from notebook.base.handlers import APIHandler

from .base import ZenodoBaseHandler

class ZenodoUploadHandler(ZenodoBaseHandler):
    """
    A handler that uploads your files to Zenodo
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir

    def zip_dir(self, notebook_dir, filename):
        """Create zip file filename from notebook_dir
        
        Parameters
        ----------
        notebook_dir : string
            Explicit path to directory to be zipped
        filename : string
            Filename to zip to; must end with '.zip'

        Returns
        -------
        null
            Raises exception on error

        Notes
        -----
        - Error handling incomplete
        """  

        if filename[-4:] != ".zip":
            raise Exception("filename invalid")

        # Go to directly outside work directory
        cmd = "cd /"+notebook_dir+"/.."
        os.system(cmd)
        
        # Zip work directory to filename
        cmd = "zip -r "+filename+" "+notebook_dir+"/"
        os.system(cmd) 


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

    def upload_file(self, filename, path_to_file, metadata, access_token):
        """Upload the given file at the given path to Zenodo
           Add included metadata

        Parameters
        ----------
        filename : string
            File to be uploaded to zenodo
        path_to_file : string
            Path to the above file (including file name)
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
        data = {'filename': filename}
        files = {'file': open(path_to_file, 'rb')}
        r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                          params={'access_token': ACCESS_TOKEN}, data=data,
                          files=files)
        r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
                         params={'access_token': ACCESS_TOKEN}, 
                         data=json.dumps({'metadata': metadata}),
                         headers=headers)
        r_dict = r.json()
        print(r_dict)
        doi = r_dict.get('doi') 
        if not doi:
            doi = r_dict.get('metadata',{}).get('prereserve_doi',{}).get('doi')
        print("doi: "+str(doi))
        return doi
    
    def store_record(self, doi):
        """Store a record of publication in a local sqlite database
    
        Parameters
        ----------
        doi : string
            Zenodo DOI given to uploaded record
    
        Returns
        -------
            void

        """
        cmd = "cd /work && mkdir .zenodo"
        os.system(cmd)
        conn = sqlite3.connect('zenodo.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE uploads
             (date_uploaded, doi)''')
        c.execute("INSERT INTO uploads VALUES (?,?)",[datetime.now(),doi])

        # Commit and close
        conn.commit()
        conn.close()

    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        # print("In GET routine for upload handler")
        print("testing my store data function")
        info = {'status':'executed get', 'doi':"no doi here"}
        self.set_status(200)
        self.write(json.dumps(info))
        self.finish()

    @web.authenticated
    @gen.coroutine
    def post(self, path=''):
        print("In POST routine for upload handler")

        """
        Takes in a a file prefix string, and metadata
        Zips notebook_dir to file_prefix.zip, uploads to Zenodo
        Returns dictionary with status (success or failure) and doi (if successful)
        """

        zenodo_params = self.api_params()
        try:
            title = zenodo_params['title']
            file_prefix = zenodo_params.get('file_prefix','workingdir')
            authors = [zenodo_params['author']]
            description = zenodo_params['description']      
            access_token = zenodo_params['access_token']      
        except KeyError:
            info = {'status':'failure', 'message':'Missing data', 'doi' : None}
            self.set_status(400)
            self.write(json.dumps(info))
            self.finish()
            return
            

        filename = file_prefix + ".zip"

        self.zip_dir(self.notebook_dir, filename)

        path_to_file = self.notebook_dir + "/" + filename
        metadata = self.assemble_metadata(title, authors, description)

        doi = self.upload_file(filename, path_to_file, metadata, access_token) 
        if (doi is not None):
            info = {'status':'success', 'doi':doi}
            print("doi: "+str(doi))
            self.set_status(201)
            self.write(json.dumps(info))
        else:
            info = {'status':'failure', 'doi': None}
            print("no doi")
            self.set_status(404)
            self.write(json.dumps(info))
        self.finish()
        
