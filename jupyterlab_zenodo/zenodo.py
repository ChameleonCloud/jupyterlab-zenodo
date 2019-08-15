""" A module for creating and editing depositions on Zenodo """

import json
import logging
import requests

from .utils import UserMistake

LOG = logging.getLogger(__name__)

ZENODO_NO_FILE_CHANGE_CODE = 10


class Deposition:
    """
    A class to represent Zenodo-style depositions
    """

    def __init__(self, dev, access_token, existing_id=None):
        """ Create new deposition object

        Parameters
        ---------
        dev : boolean
            True if in development environment, False in deployment
        access_token : string
            Access token for Zenodo
        existing_id : string
            Optional: provide id of existing deposition

        Returns
        -------
        Deposition
        """
        self.client = Client(dev, access_token)
        if existing_id:
            self.id = existing_id

    def zenodo_init(self):
        """ Initializes new deposition on Zenodo

        Parameters
        ---------
        none

        Returns
        -------
        void

        Notes
        -----
        - Not necessary if id has already been set by existing_id
        - Sets self.id on success, raises exception on failure
        """
        self.id = self.client.create_deposition()

    def new_version(self):
        """ Create new version of the deposition

        Parameters
        ----------
        none

        Returns
        -------
        void

        Notes
        -----
        - Changes self.id on success, raises exception on failure
        """
        self.id = self.client.new_deposition_version(self.id)

    def set_metadata(self, metadata):
        """ Add metadata to deposition

        Parameters
        ---------
        metadata : dictionary
            Contains non-empty title, upload_type, publication_type,
              description, communities, and creators,
              all satisfying Zenodo's specifications

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
    """
    A class to interface with the Zenodo API
    """

    def process_zenodo_response(self, response, message, field=None):
        """ Process a response from a request to the Zenodo API

        Parameters
        ---------
        response : Response
            Response from zenodo request
        message : string
            Message to include with exception
        field : string (optional)
            If present, return this field on success

        Returns
        -------
        if field is provided: response.json()[field]
        otherwise: response.json()
        """
        # Check the response status
        status = response.status_code

        # Successful response with no body
        if status == 204:
            # Make sure nothing was expected
            if field:
                raise Exception(message + "\nExpected a response body")
            else:
                return {}

        # Retrieve response body, include in exception messages
        info = response.json()
        exception_message = message + "\nResponse: " + str(info)

        # On success, return the requested field if present
        # (If no field was requested, return the whole dictionary)
        if status < 400:
            if field:
                data = info.get(field)
                if data:
                    return data
                else:
                    LOG.warning("This probably shouldn't happen")
                    raise Exception(message)
            else:
                return info

        # On a 400 error, check the error code
        # If it's not a known code, return the generic exception
        elif status == 400:
            errors = info.get('errors', {})
            code = ZENODO_NO_FILE_CHANGE_CODE
            if any([err.get('code', 0) == code for err in errors]):
                raise UserMistake("You need to update some files before trying"
                                  " to update your deposition on Zenodo")
            else:
                raise Exception(exception_message)

        # A 401 error means unauthorized access
        elif status == 401:
            raise UserMistake("Invalid access token. To use our default token,"
                              " leave the 'access token' field blank. Or, go "
                              "to https://zenodo.org/account/settings/"
                              "applications/tokens/new/ to create one")
        # For all other errors, return the generic error exception
        else:
            raise Exception(exception_message)

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
        err_msg = "Issue creating a new deposition"

        r = requests.post(self.url_base + '/deposit/depositions',
                          params={'access_token': self.access_token}, json={},
                          headers=self.headers)

        # Return deposition id if nothing went wrong
        return self.process_zenodo_response(r, err_msg, 'id')

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
        err_msg = "Issue creating a new deposition version"
        r = requests.post((self.url_base + '/deposit/depositions/'
                           + str(deposition_id)
                           + '/actions/newversion'),
                          params={'access_token': self.access_token})

        # Return new record id if nothing went wrong
        links = self.process_zenodo_response(r, err_msg, 'links')

        new_record_loc = links['latest_draft']
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
        err_msg = "Issue with the metadata uploading"
        r = requests.put(self.url_base + '/deposit/depositions/%s'
                         % deposition_id,
                         params={'access_token': self.access_token},
                         data=json.dumps({'metadata': metadata}),
                         headers=self.headers)

        # Make sure nothing went wrong
        self.process_zenodo_response(r, err_msg)

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
        err_msg = "Something went wrong with the file upload"

        with open(path_to_file, 'rb') as open_file:
            data = {'filename': path_to_file.split('/')[-1]}
            files = {'file': open_file}
            r = requests.post(self.url_base + '/deposit/depositions/%s/files'
                              % deposition_id,
                              params={'access_token': self.access_token},
                              data=data, files=files)

        # Return file id if nothing went wrong
        return self.process_zenodo_response(r, err_msg, 'id')

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
        err_msg = "Something went wrong retrieving files"

        # Get file information
        r = requests.get((self.url_base + '/deposit/depositions/'
                          + deposition_id + '/files'),
                         params={'access_token': self.access_token})

        # Make sure nothing went wrong
        response_dict = self.process_zenodo_response(r, err_msg)

        # Extract file ids, return if there are any
        file_ids = [f['id'] for f in response_dict if 'id' in f]
        if file_ids == []:
            raise Exception("Something went wrong getting the last upload-"
                            " seems like there aren't files: "
                            + str(response_dict))
        else:
            return file_ids

    def delete_deposition_files(self, deposition_id, file_ids):
        """Delete files from a deposition

        Parameters
        ----------
        deposition_id : string
            Zenodo id of the existing deposition
        file_ids : list of strings
            Ids of files to delete

        Returns
        -------
        void

        Notes
        -----
        - Raises an exception if the operation fails
        """
        # Delete the file
        err_msg = "Something went wrong deleting files"
        for file_id in file_ids:
            r = requests.delete(self.url_base + '/deposit/depositions/'
                                + deposition_id + '/files/' + file_id,
                                params={'access_token': self.access_token})
            self.process_zenodo_response(r, err_msg)

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
        err_msg = "Something went wrong publishing the deposition"

        # Publish deposition
        r = requests.post((self.url_base
                           + '/deposit/depositions/%s/actions/publish'
                           % deposition_id),
                          params={'access_token': self.access_token})

        return self.process_zenodo_response(r, err_msg, 'doi')
