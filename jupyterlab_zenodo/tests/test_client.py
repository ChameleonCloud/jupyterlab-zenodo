from datetime import datetime
import os
import requests
import unittest

from ..utils import UserMistake
from ..zenodo import Client

class CreateDepositionTest(unittest.TestCase):
   
    def test_success(self):
        token = '***REMOVED***'
        self.client = Client(True, token)
        try:
            self.client.create_deposition()
        except Exception as e:
            print(r)
            self.fail("Add metadata raised an exception: "+str(e)) 

    def test_bad_token(self):
        bad_client = Client(True, 'notatoken')
        with self.assertRaises(Exception): bad_client.create_deposition()

class AddMetadataTest(unittest.TestCase):
   
    def setUp(self):
        url_base = 'https://sandbox.zenodo.org/api'
        good_token = '***REMOVED***'

        r = requests.post(url_base + '/deposit/depositions',
                          params={'access_token': good_token}, json={},
                          headers={"Content-Type": "application/json"})
        # retrieve deposition id
        r_dict = r.json()
        self.deposition_id = r_dict['id']
        self.good_metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
     
        self.client = Client(True, good_token)

    def test_success(self):
        try:
            self.client.add_metadata(self.deposition_id, self.good_metadata)
        except Exception as e:
            self.fail("Add metadata raised an exception: "+str(e)) 

    def test_bad_data(self):
        with self.assertRaises(Exception): self.client.add_metadata(self.deposition_id, {})
    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.add_metadata('1010101', self.good_metadata)
        
class AddFileTest(unittest.TestCase):
    def setUp(self):
        url_base = 'https://sandbox.zenodo.org/api'
        good_token = '***REMOVED***'

        r = requests.post(url_base + '/deposit/depositions',
                          params={'access_token': good_token}, json={},
                          headers={"Content-Type": "application/json"})
        # retrieve deposition id
        r_dict = r.json()
        self.deposition_id = r_dict['id']
        self.good_metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
     
        self.good_filepath = '***REMOVED***test.txt'
        self.client = Client(True, good_token)

    def test_success(self):
        file_id = self.client.add_file(self.deposition_id, self.good_filepath)
        self.assertIsNotNone(file_id)
   
    def test_bad_id(self): 
        with self.assertRaises(Exception): self.client.add_file('1010101', self.good_filepath)

    def test_bad_file(self): 
        with self.assertRaises(Exception): self.client.add_file(self.deposition_id, 'notafile')


class PublishDepositionTest(unittest.TestCase):
    def setUp(self):
        url_base = 'https://sandbox.zenodo.org/api'
        good_token = '***REMOVED***'

        r = requests.post(url_base + '/deposit/depositions',
                          params={'access_token': good_token}, json={},
                          headers={"Content-Type": "application/json"})
        # retrieve deposition id
        r_dict = r.json()
        self.deposition_id = r_dict['id']

        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
        filepath = '***REMOVED***test.txt'

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)

    def test_success(self):
        doi = self.client.publish_deposition(self.deposition_id)
        self.assertIsNotNone(doi)

    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.publish_deposition('1010101')

class NewDepositionVersionTest(unittest.TestCase):

    def setUp(self):
        url_base = 'https://sandbox.zenodo.org/api'
        good_token = '***REMOVED***'

        r = requests.post(url_base + '/deposit/depositions',
                          params={'access_token': good_token}, json={},
                          headers={"Content-Type": "application/json"})
        # retrieve deposition id
        r_dict = r.json()
        self.deposition_id = r_dict['id']

        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
        filepath = '***REMOVED***test.txt'

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)
        self.client.publish_deposition(self.deposition_id)

    def test_success(self):
        new_record_id = self.client.new_deposition_version(self.deposition_id)
        self.assertIsNotNone(new_record_id)

    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.new_deposition_version('1010101')

class PublishNewVersionTest(unittest.TestCase):
    def setUp(self):
        url_base = 'https://sandbox.zenodo.org/api'
        good_token = '***REMOVED***'

        r = requests.post(url_base + '/deposit/depositions',
                          params={'access_token': good_token}, json={},
                          headers={"Content-Type": "application/json"})
        # retrieve deposition id
        r_dict = r.json()
        self.deposition_id = r_dict['id']

        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
        filepath = '***REMOVED***test.txt'

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)
        self.client.publish_deposition(self.deposition_id)

    def test_user_error(self):
        new_id = self.client.new_deposition_version(self.deposition_id)
        with self.assertRaises(UserMistake): self.client.publish_deposition(new_id)


class GetFilesTest(unittest.TestCase):
    def setUp(self):
        good_token = '***REMOVED***'
        self.client = Client(True, good_token)

    def test_success(self):
        new_id = self.client.new_deposition_version('355162')
        file_ids = self.client.get_deposition_files(new_id)
        self.assertNotEqual(len(file_ids),0)

    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.get_deposition_files('1010101')

class DeleteFilesSuccessTest(unittest.TestCase):
    def setUp(self):
        good_token = '***REMOVED***'
        self.client = Client(True, good_token)
        self.new_id = self.client.new_deposition_version('355162')
        self.file_ids = self.client.get_deposition_files(self.new_id)
        cmd = "echo "+str(datetime.now())+" > ***REMOVED***test.txt"
        os.system(cmd)

    def test_success(self):
        try:
            self.client.delete_deposition_files(self.new_id, self.file_ids)
        except Exception as e:
            self.fail("deletion failed: "+str(e))        

    def tearDown(self):
        filepath = '***REMOVED***test.txt'
        self.client.add_file(self.new_id, filepath)
        self.client.publish_deposition(self.new_id)

class DeleteFilesFailTest(unittest.TestCase):
    def setUp(self):
        good_token = '***REMOVED***'
        self.client = Client(True, good_token)

    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.delete_deposition_files('1010101',['1'])
