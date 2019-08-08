import requests
import unittest

from zenodo import Client

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
        r = 'test'
        try:
            self.client.add_metadata(self.deposition_id, self.good_metadata)
        except Exception as e:
            print(r)
            self.fail("Add metadata raised an exception: "+str(e)) 

    def test_bad_data(self):
        with self.assertRaises(Exception): self.client.add_metadata(self.deposition_id, {})
    def test_bad_id(self):
        with self.assertRaises(Exception): self.client.add_metadata('1010101', self.good_metadata)
        
