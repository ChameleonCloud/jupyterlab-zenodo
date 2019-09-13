import unittest

from jupyterlab_zenodo.test_init import TEST_API_TOKEN
from jupyterlab_zenodo.upload import assemble_upload_data, assemble_metadata
from jupyterlab_zenodo.utils import UserMistake

sample_response = {
    'title': 'a title',
    'author': 'an author',
    'description': 'a description',
    'affiliation': 'usomewhere',
    'other stuff': 'other',
    'more other stuff': 'other',
    'directory': 'my_directory',
    'zenodo_token': 'sometoken',
}


class AssembleUploadDataTest(unittest.TestCase):
    def setUp(self):
        self.response = sample_response.copy()
        self.access_token = TEST_API_TOKEN

    def test_zerolength_dir(self):
        self.response['directory'] = ''
        data = assemble_upload_data(self.response, self.access_token)
        self.assertEqual(data['directory_to_zip'], 'work')
        self.assertEqual(data['access_token'], 'sometoken')

    def test_no_dir(self):
        self.response.pop('directory')
        data = assemble_upload_data(self.response, self.access_token)
        self.assertEqual(data['directory_to_zip'], 'work')
        self.assertEqual(data['access_token'], 'sometoken')

    def test_no_tok(self):
        self.response.pop('zenodo_token')
        data = assemble_upload_data(self.response, self.access_token)
        self.assertEqual(data['access_token'], self.access_token)

    def test_no_tok_no_default(self):
        self.response.pop('zenodo_token')
        with self.assertRaises(UserMistake):
            assemble_upload_data(self.response, None)

    def test_zerolength_tok(self):
        self.response['zenodo_token'] = ''
        data = assemble_upload_data(self.response, self.access_token)
        self.assertEqual(data['access_token'], self.access_token)

    def test_all_good(self):
        data = assemble_upload_data(self.response, self.access_token)
        self.assertEqual(data['directory_to_zip'], self.response['directory'])
        self.assertEqual(data['access_token'], 'sometoken')


class AssembleMetadataTest(unittest.TestCase):
    def setUp(self):
        self.response = sample_response.copy()

    def test_many_authors_with_spaces(self):
        self.response['author'] = 'Person One, Person Two,    Person Three    '
        self.response['affiliation'] = 'Place one,\n    Place two  ,  Place three '
        combined = [
            {'name':'Person One', 'affiliation': 'Place one'},
            {'name':'Person Two', 'affiliation': 'Place two'},
            {'name':'Person Three', 'affiliation': 'Place three'}]
        data = assemble_metadata(self.response, None)
        self.assertEqual(data['creators'],combined)

    def test_many_authors(self):
        self.response['author'] = 'Person One,Person Two,Person Three'
        self.response['affiliation'] = 'Place one,Place two,Place three'
        combined = [
            {'name':'Person One', 'affiliation': 'Place one'},
            {'name':'Person Two', 'affiliation': 'Place two'},
            {'name':'Person Three', 'affiliation': 'Place three'}]
        data = assemble_metadata(self.response, None)
        self.assertEqual(data['creators'],combined)

    def test_many_authors_one_place(self):
        self.response['author'] = 'Person One,Person Two,Person Three'
        with self.assertRaises(UserMistake):
            data = assemble_metadata(self.response, None)


    def test_no_title(self):
        self.response.pop('title')
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_no_authors(self):
        self.response.pop('author')
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_no_description(self):
        self.response.pop('description')
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_short_title(self):
        self.response['title'] = 'j'
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_short_authors(self):
        self.response['author'] = 'j'
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_short_description(self):
        self.response['description'] = 'j'
        with self.assertRaises(UserMistake):
            assemble_metadata(self.response, None)

    def test_with_community(self):
        metadata = assemble_metadata(self.response, 'Chameleon')
        self.assertEqual(metadata['title'], self.response['title'])
        self.assertEqual(metadata['creators'][0]['name'],
                         self.response['author'])
        self.assertEqual(metadata['description'],
                         self.response['description'])
        self.assertEqual(metadata['upload_type'], 'publication')
        self.assertEqual(metadata['publication_type'], 'workingpaper')

    def test_success(self):
        metadata = assemble_metadata(self.response, None)
        self.assertEqual(metadata['title'], self.response['title'])
        self.assertEqual(metadata['creators'][0]['name'],
                         self.response['author'])
        self.assertEqual(metadata['description'],
                         self.response['description'])
        self.assertEqual(metadata['upload_type'], 'publication')
        self.assertEqual(metadata['publication_type'], 'workingpaper')
