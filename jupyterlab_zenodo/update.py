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

        c.execute("SELECT date_uploaded, doi, directory, filename, access_token FROM uploads ORDER BY date_uploaded DESC")

        rows = c.fetchall()
        # Close connection
        conn.close()
        print(rows[0])
        last_upload = rows[0]
        upload_data = {
            'date': last_upload[0],
            'doi': last_upload[1],
            'directory': last_upload[2],
            'filename': last_upload[3],
            'access_token': last_upload[4]
        }

        print(upload_data)
        return upload_data


    def update_file(self, filename, path_to_file, doi, access_token):
        """Upload the given file at the given path to Zenodo
           Add included metadata

        Parameters
        ----------
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

        """
        ACCESS_TOKEN = access_token
        headers = {"Content-Type": "application/json"}

        # Create deposition
        r = requests.post('https://zenodo.org/api/deposit/depositions',
                          params={'access_token': ACCESS_TOKEN}, json={},
                          headers=headers)
        deposition_id = r.json()['id']
        """

        deposition_id = record_id
        data = {'filename': filename}
        files = {'file': open(path_to_file, 'rb')}
        r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                          params={'access_token': ACCESS_TOKEN}, data=data,
                          files=files)
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
        db_dest = "/work/.zenodo/"
        print(os.path.exists(db_dest))
        if not os.path.exists(db_dest):
            cmd = "mkdir" + db_dest
            os.system(cmd)
        conn = sqlite3.connect(db_dest+'zenodo.db')
        c = conn.cursor()
        try:
            c.execute("CREATE TABLE uploads (date_uploaded, doi)")
        except:
            pass
        c.execute("INSERT INTO uploads VALUES (?,?)",[datetime.now(),doi])

        # Commit and close
        conn.commit()
        conn.close()

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
          r.requests.post('https://zenodo.org/api/deposit/depositions/'+record+'/actions/newversion', params={'access_token': ACCESS_TOKEN})
        2. Upload file to that

        """

        upload_data = self.get_last_upload()

        filename = upload_data['filename']
        directory = upload_data['directory']
        record_id = get_id(upload_data['doi']) 
        access_token = upload_data['access_token']

        doi = self.update_file(filename, directory+'/../'+filename, record_id, access_token)

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
        
