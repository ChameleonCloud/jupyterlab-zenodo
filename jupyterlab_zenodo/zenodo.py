""" A module for creating and editing depositions on Zenodo """

import json
import requests

def add_metadata(url_base, headers, access_token, deposition_id, metadata):
    """Add metadata to an existing deposition

    Parameters
    ----------
    url_base: string
        Base url for api (either zenodo.org or sandbox.zenodo.org) 
    headers : dictionary
        Headers for the api call
    access_token : string
        Access token used to post to the Zenodo api
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
    r = requests.put(url_base + '/deposit/depositions/%s' 
                        % deposition_id,
                     params={'access_token': access_token}, 
                     data=json.dumps({'metadata': metadata}),
                     headers=headers)
    # Make sure nothing went wrong
    r_dict = r.json()
    if int(r_dict.get('status','0')) > 399:
        raise Exception("Something went wrong with the metadata upload: "+str(r_dict))
 
