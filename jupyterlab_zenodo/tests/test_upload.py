import unittest

from ..upload import assemble_upload_data, assemble_metadata
from ..utils import UserMistake

sample_response = {
    'title': 'a title',
    'author': 'an author',
    'description': 'a description',
    'other stuff': 'other',
    'more other stuff': 'other',
    'filename': 'myfile',
    'directory': 'my_directory',
    'zenodo_token': 'sometoken',
}
 
class AssembleUploadDataTest(unittest.TestCase):
    def setUp(self):
        self.response = sample_response.copy()
        self.access_token = '***REMOVED***'

    def test_no_filename(self):
        self.response.pop('filename')
        with self.assertRaises(UserMistake): assemble_upload_data(self.response, True)

    def test_zerolength_filename(self):
        self.response['filename'] = ''
        with self.assertRaises(UserMistake): assemble_upload_data(self.response, True)

    def test_no_dir(self):
        self.response.pop('directory')
        data = assemble_upload_data(self.response, True)
        self.assertEqual(data['directory_to_zip'],'work')

    def test_no_tok(self):
        self.response.pop('zenodo_token')
        data = assemble_upload_data(self.response, True)
        self.assertEqual(data['access_token'],self.access_token)

    def test_all_good(self):
        data = assemble_upload_data(self.response, True)
        self.assertEqual(data['access_token'],self.response['zenodo_token'])
        self.assertEqual(data['directory_to_zip'],self.response['directory'])
        self.assertEqual(data['filename'],self.response['filename'])
    

class AssembleMetadataTest(unittest.TestCase):
    def setUp(self):
        self.response = sample_response.copy()

    def test_no_title(self):
        self.response.pop('title')
        with self.assertRaises(UserMistake): assemble_metadata(self.response)
        
    def test_no_authors(self):
        self.response.pop('author')
        with self.assertRaises(UserMistake): assemble_metadata(self.response)

    def test_no_description(self):
        self.response.pop('description')
        with self.assertRaises(UserMistake): assemble_metadata(self.response)

    def test_short_title(self):
        self.response['title'] = 'j'
        with self.assertRaises(UserMistake): assemble_metadata(self.response)

    def test_short_authors(self):
        self.response['author'] = 'j'
        with self.assertRaises(UserMistake): assemble_metadata(self.response)

    def test_short_description(self):
        self.response['description'] = 'j'
        with self.assertRaises(UserMistake): assemble_metadata(self.response)

    def test_success(self):
        metadata = assemble_metadata(self.response)
        self.assertEqual(metadata['title'],self.response['title'])
        self.assertEqual(metadata['creators'][0]['name'],self.response['author'])
        self.assertEqual(metadata['description'],self.response['description'])
        self.assertEqual(metadata['upload_type'],'publication')
        self.assertEqual(metadata['publication_type'],'workingpaper')
