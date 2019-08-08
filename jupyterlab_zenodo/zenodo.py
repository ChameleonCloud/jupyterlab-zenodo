""" A module for creating and editing depositions on Zenodo """

import json
import requests

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
     
