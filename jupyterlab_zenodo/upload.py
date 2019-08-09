""" JupyterLab Zenodo : Exporting from JupyterLab to Zenodo """

import json
import requests

from tornado import gen, web

#TODO: make relative again
from .base import ZenodoBaseHandler
from .utils import get_id, store_record, UserMistake, zip_dir
from .zenodo import Deposition


class ZenodoUploadHandler(ZenodoBaseHandler):
    """
    A handler that uploads your files to Zenodo
    """
    def initialize(self, notebook_dir):
        self.notebook_dir = notebook_dir
        #TODO: change dev to False before deployment
        self.dev = True

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
        - Raises an exception if something goes wrong
        - If it returns, it returns a real DOI
    
        """

        deposition = Deposition(self.dev, access_token)
        deposition.set_file(path_to_file)
        deposition.set_metadata(metadata)
        deposition.publish()

        return deposition.doi
   
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

        try:
            upload_data = assemble_upload_data(request_data, self.dev)
            metadata = assemble_metadata(request_data)
            path_to_file = zip_dir(
                upload_data['directory_to_zip'],
                upload_data['filename'])
            doi = self.upload_file(
                path_to_file, 
                metadata,
                upload_data['access_token']) 

        except UserMistake as e:
            # UserMistake exceptions contain messages for the user
            self.return_error(str(e))

        except Exception as x:
            # All other exceptions are internal
            print("Internal error: "+str(x))
            print(x)
            self.return_error("Something went wrong")
            return

        else:
            info = {'status':'success', 'doi':doi}
            print("doi: "+str(doi))
            self.set_status(201)
            self.write(json.dumps(info))
            store_record(doi, path_to_file, directory_to_zip, access_token)
            self.finish()


def assemble_upload_data(request_data, dev):
    """Gather and validate filename, directory, and access token for upload
    Parameters
    ----------
    request_data : dictionary
        Contains the information sent with the POST request
    dev : boolean
        True if in development mode, false in deployment

    Returns
    -------
    dictionary
        With access_token, directory_to_zip, and filename, all non-empty

    Notes
    -----
    - Raises an exception if data is invalid
    """
    # Make sure a filename has been provided
    filename = request_data.get('filename','')

    if len(filename) < 1:
        raise UserMistake("File name must be provided")
        return
    if dev:
        #Sandbox version:
        our_access_token = '***REMOVED***'
    else:
        #Real version
        our_access_token = '***REMOVED***'
        # If the user has no access token, use ours
    access_token = request_data.get('zenodo_token') or our_access_token
    # If the user hasn't specified a directory, use the notebook directory
    directory_to_zip = request_data.get('directory') or 'work'
        # Assemble into dictionary to return
    upload_data = {
        'access_token' : access_token,
        'directory_to_zip' : directory_to_zip,
        'filename' : filename,
    } 
    return upload_data 
   
def assemble_metadata(request_data):
    """Turn metadata into a dictionary for Zenodo upload
        Parameters
    ----------
    request_data : dictionary
        Contains the information sent with the POST request
    Returns
    -------
    dictionary
        With title, creators, and description
        Each more than three characters long

    Notes
    -----
    - Raises an exception if data is invalid
        """
    # Get basic metadata from form response
    title = request_data.get('title','')
    author = request_data.get('author','')
    description = request_data.get('description','')

    # Zenodo requires each field to be at least 4 characters long
    if any([len(title) <= 3, len(author) <=3, len(description) <= 3]):
        msg = ("Title, author, and description fields must all be filled in"
              " and at least four characters long")
        raise UserMistake(msg)

    # Turn list of author strings into list of author dictionaries
    creator_list = []
    creator_list.append({'name': author, 'affiliation': 'Chameleon Cloud'})

    # Put data into dictionary to return
    metadata = {}
    metadata['title'] = title 
    metadata['upload_type'] = 'publication' 
    metadata['publication_type'] = 'workingpaper'
    metadata['description'] = description 
    metadata['creators'] = creator_list 
    return metadata

