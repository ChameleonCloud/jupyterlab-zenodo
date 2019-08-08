import requests
import unittest

from zenodo import add_metadata

class AddMetadataTest(unittest.TestCase):
   
    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        self.url_base = 'https://sandbox.zenodo.org/api'
        self.good_token = '***REMOVED***'

        r = requests.post(self.url_base + '/deposit/depositions',
                          params={'access_token': self.good_token}, json={},
                          headers=self.headers)
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
     

    def test_success(self):
        r = 'test'
        try:
            r = add_metadata(self.url_base, self.headers, self.good_token, self.deposition_id, self.good_metadata)
        except Exception as e:
            print(r)
            self.fail("Add metadata raised an exception: "+str(e)) 

    def test_bad_token(self):
        with self.assertRaises(Exception): add_metadata(self.url_base, self.headers, 'test', self.deposition_id, self.good_metadata)
    def test_bad_data(self):
        with self.assertRaises(Exception): add_metadata(self.url_base, self.headers, self.good_token, self.deposition_id, {})
    def test_bad_id(self):
        with self.assertRaises(Exception): add_metadata(self.url_base, self.headers, self.good_token, '1010101', self.good_metadata)
        
