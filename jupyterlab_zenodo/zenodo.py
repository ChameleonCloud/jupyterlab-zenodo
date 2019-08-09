""" A module for creating and editing depositions on Zenodo """

import json
import requests

from .utils import UserMistake

class Deposition:
    
    def __init__(self, dev, access_token, existing_id=None):
        """ Initialize new deposition 
        
        Parameters
        ---------
        dev : boolean
            True if in development environment, False in deployment
        access_token : string
            Access token for Zenodo
        existing_id : string
            Optional: provide id of existing deposition
            If none is provided, a new deposition is created

        Returns
        -------
        Deposition
        """
        
        self.client = Client(dev, access_token)
        self.id = existing_id or self.client.create_deposition()

    def new_version(self):
        """ Create new version the deposition
        
        Parameters
        ----------
        none

        Returns
        -------
        void

        Notes
        -----
        - Changes self.id on success, raises Exception on failure
        """
        self.id = self.client.new_deposition_version(self.id)
	
    def set_metadata(self, metadata):
        """ Add metadata to deposition
        
        Parameters
        ---------
        metadata : dictionary
            Contains non-empty title, upload_type, publication_type, 
              description, and creators, satisfying Zenodo's specifications

        Returns
        -------
        void

        Notes
        -----
        - sets self.metadata on success
        """
        
        self.client.add_metadata(self.id, metadata)
        self.metadata = metadata
        
    def set_file(self, path_to_file):
        """ Add metadata to deposition
        
        Parameters
        ---------
        path_to_file : string
            Path to file to be uploaded

        Returns
        -------
        void

        Notes
        -----
        - sets self.file_id on success
        """
        self.file_id = self.client.add_file(self.id, path_to_file)

    def clear_files(self):
        """ Add metadata to deposition
        
        Parameters
        ---------
        none

        Returns
        -------
        void
        """
        file_ids = self.client.get_deposition_files(self.id)
        self.client.delete_deposition_files(self.id, file_ids)

    def publish(self):
        """ Publish deposition
        
        Parameters
        ---------
        none

        Returns
        -------
        void

        Notes
        -----
        - sets self.doi on success
        """
        self.doi = self.client.publish_deposition(self.id)


class Client:
    def check_access_token(self):
        """ Raise an exception if an invalid token is provided
        
        Parameters
        ---------
        none

        Returns
        -------
        void
        """

        r = requests.get(self.url_base + '/deposit/depositions',
                         params={'access_token': self.access_token})
        status = r.status_code
        if int(status) == 401:
            raise UserMistake("Invalid access token. To use our default token,"
                              " leave the 'access token' field blank")

    def __init__(self, dev, access_token):
        """ Initialize Zenodo client 
        
        Parameters
        ---------
        dev : boolean
            True if in development environment, False in deployment
        access_token : string
            Access token for Zenodo

        Returns
        -------
        Client
        """

        if dev is True:
            self.url_base = 'https://sandbox.zenodo.org/api'
        else:
            self.url_base = 'https://zenodo.org/api'
            
        self.access_token = access_token
        self.headers = {"Content-Type": "application/json"}
        self.check_access_token()

    def create_deposition(self):
        """ Create new deposition on Zenodo 
        
        Parameters
        ----------
        none

        Returns
        -------
        string
            id of newly created deposition
        """
	
        r = requests.post(self.url_base + '/deposit/depositions',
                          params={'access_token': self.access_token}, json={},
                          headers=self.headers)
        # retrieve deposition id
        r_dict = r.json()
        deposition_id = r_dict.get('id')
        if deposition_id is None:
            raise Exception("Issue creating a new deposition")
        else:
            return deposition_id

    def new_deposition_version(self, deposition_id):
        """ Create new version of a published deposition on Zenodo 
        
        Parameters
        ----------
        deposition_id : string
            Id of published deposition

        Returns
        -------
        string
            Id of newly created deposition draft
        """
        r = requests.post((self.url_base + '/deposit/depositions/' + str(deposition_id)
                     + '/actions/newversion'),
                     params={'access_token': self.access_token})

        response_dict = r.json()
        new_record_loc = response_dict.get('links',{}).get('latest_draft')

        if new_record_loc is None:
            raise Exception("Something went wrong getting the last upload")

        new_record_id = new_record_loc.split('/')[-1]
        return new_record_id

         
    def add_metadata(self, deposition_id, metadata):
        """Add metadata to an existing deposition
    
        Parameters
        ----------
        deposition_id : string
            Zenodo id of the existing deposition
        metadata : dictionary
            Contains non-empty title, upload_type, publication_type, 
              description, and creators, satisfying Zenodo's specifications
    
        Returns
        -------
        void
    
        Notes
        -----
        - Expects metadata and url_base to be of the appropriate format
        - Raises an exception if the operation fails
        """
        
        # Add metadata 
        r = requests.put(self.url_base + '/deposit/depositions/%s' 
                            % deposition_id,
                         params={'access_token': self.access_token}, 
                         data=json.dumps({'metadata': metadata}),
                         headers=self.headers)
        # Make sure nothing went wrong
        r_dict = r.json()
        if int(r_dict.get('status','0')) > 399:
            raise Exception("Something went wrong with the metadata upload: "+str(r_dict))
     

    def add_file(self, deposition_id, path_to_file):
        """Upload a file to an existing deposition
    
        Parameters
        ----------
        deposition_id : string
            Zenodo id of the existing deposition
        path_to_file : string
            Path to file to be uploaded
    
        Returns
        -------
        string
            File id
    
        Notes
        -----
        - Raises an exception if the operation fails
        """
        # Organize and upload file
        data = {'filename': path_to_file.split('/')[-1]}
        open_file = open(path_to_file, 'rb')
        files = {'file': open_file}
        r = requests.post(self.url_base + '/deposit/depositions/%s/files' 
                            % deposition_id,
                          params={'access_token': self.access_token}, data=data,
                          files=files)
        # Close the file after the request
        open_file.close()

        # Return file id if nothing went wrong
        r_dict = r.json()
        file_id = r_dict.get('id')

        if file_id is None:
            raise Exception("Something went wrong with the file upload")
        else:
            return file_id

    def get_deposition_files(self, deposition_id):
        """Get the file id of a deposition
    
        Parameters
        ----------
        deposition_id : string
            Zenodo id of the existing deposition
    
        Returns
        -------
        list of strings
            file_ids
    
        Notes
        -----
        - Raises an exception if the operation fails
        """

        # Get file information
        r = requests.get((self.url_base + '/deposit/depositions/' 
                         + deposition_id + '/files'),
                         params={'access_token': self.access_token})
        response_dict = r.json()

        file_ids = []
        for file_dict in response_dict:
            file_id = file_dict.get('id')
            if file_id is not None:
                file_ids.append(file_id)

        if file_ids == []:
            raise Exception("Something went wrong getting the last upload: seems like there aren't files: "+str(response_dict))
        else:
            return file_ids

    def delete_deposition_files(self, deposition_id, file_ids):
        # Delete the file
        for file_id in file_ids:
            r = requests.delete(self.url_base + '/deposit/depositions/'
                            + deposition_id + '/files/' + file_id, 
                            params={'access_token': self.access_token})
            try:
                r.json()
            except:
                pass
            else:
                raise Exception("Something went wrong deleting the files " + r.status())
 

    def publish_deposition(self, deposition_id):
        """Publish existing deposition
    
        Parameters
        ----------
        deposition_id : string
            Zenodo id of the existing deposition
    
        Returns
        -------
        string
            DOI
    
        Notes
        -----
        - Raises an exception if the operation fails
        """

        # Publish deposition
        r = requests.post(self.url_base + '/deposit/depositions/%s/actions/publish' 
                            % deposition_id,
                          params={'access_token': self.access_token})
    
        # Get doi 
        r_dict = r.json()
        doi = r_dict.get('doi') 

        if doi is None:
            if r_dict.get('errors',[{}])[0].get('code',0) == 10:
                raise UserMistake("You need to update some of your files"
                        " before trying to update your deposition on Zenodo")
            else:
                raise Exception("Something went wrong publishing the deposition.\nResponse: "+str(r_dict))
        else:
            return doi
 

