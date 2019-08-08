import requests
import unittest

from zenodo import Deposition

class InitTest(unittest.TestCase):
   
    def test_success(self):
        token = '***REMOVED***'
        dep = Deposition(True, token)
        self.assertIsNotNone(dep.id)

    def test_bad_token(self):
        with self.assertRaises(Exception): Deposition(True, 'notatoken')

class SetMetadataTest(unittest.TestCase):
   
    def setUp(self):
        token = '***REMOVED***'
        self.dep = Deposition(True, token)

        self.good_metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  

    def test_success(self):
        self.dep.set_metadata(self.good_metadata)
        self.assertIsNotNone(self.dep.metadata)

    def test_bad_data(self):
        with self.assertRaises(Exception): self.dep.set_metadata({})

class SetFileTest(unittest.TestCase):
    def setUp(self):
        token = '***REMOVED***'
        self.dep = Deposition(True, token)
        self.good_filepath = '***REMOVED***test.txt'

    def test_success(self):
        self.dep.set_file(self.good_filepath)
        self.assertIsNotNone(self.dep.file_id)

    def test_bad_data(self):
        with self.assertRaises(Exception): self.dep.set_file('notafile')


class PublishTest(unittest.TestCase):
    def setUp(self):
        token = '***REMOVED***'
        self.dep = Deposition(True, token)
        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
        self.dep.set_metadata(metadata)
        self.dep.set_file('***REMOVED***test.txt')


    def test_success(self):
        self.dep.publish()
        self.assertIsNotNone(self.dep.doi)

class NewVersionTest(unittest.TestCase):
    def setUp(self):
        token = '***REMOVED***'
        self.dep = Deposition(True, token)
        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name', 
                         'affiliation': 'Chameleon Cloud'}],
        }  
        self.dep.set_metadata(metadata)
        self.dep.set_file('***REMOVED***test.txt')
        self.dep.publish()

    def test_success(self):
        old_id = self.dep.id
        self.dep.new_version()
        new_id = self.dep.id
        self.assertNotEqual(old_id, new_id)


