""" A module for creating and editing depositions on Zenodo """

import json
import requests

class Deposition:
    
    def __init__(self, dev, access_token):
        """ Initialize new deposition 
        
        Parameters
        ---------
        dev : boolean
            True if in development environment, False in deployment
        access_token : string
            Access token for Zenodo

        Returns
        -------
        Deposition
        """
        self.client = Client(dev, access_token)
        self.id = self.client.create_deposition() 

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
        files = {'file': open(path_to_file, 'rb')}
        r = requests.post(self.url_base + '/deposit/depositions/%s/files' 
                            % deposition_id,
                          params={'access_token': self.access_token}, data=data,
                          files=files)

        # Return file id if nothing went wrong
        r_dict = r.json()
        file_id = r_dict.get('id')

        if file_id is None:
            raise Exception("Something went wrong with the file upload")
        else:
            return file_id

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
    
        # Get doi (or prereserve_doi)
        r_dict = r.json()
        doi = r_dict.get('doi') 

        if doi is None:
            raise Exception("Something went wrong publishing the deposition.\nResponse: "+str(r_dict))
        else:
            return doi
 


