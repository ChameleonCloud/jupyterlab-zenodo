from datetime import datetime
import os
import requests
import tempfile
import unittest

from jupyterlab_zenodo.test_init import TEST_API_TOKEN
from jupyterlab_zenodo.utils import UserMistake
from jupyterlab_zenodo.zenodo import Client

# API bases for dev and non-dev
API_BASE_URL_DEV = 'https://sandbox.zenodo.org/api'
API_BASE_URL = 'https://zenodo.org/api'


def setUpModule():
    global test_file
    global test_filename
    test_file = tempfile.NamedTemporaryFile()
    test_file.write(b'Hello world')
    test_filename = test_file.name


class CreateDepositionTest(unittest.TestCase):
    def test_success(self):
        token = TEST_API_TOKEN
        self.client = Client(True, token)
        self.client.create_deposition()

    def test_bad_token(self):
        token = 'notatoken'
        self.client = Client(True, token)
        with self.assertRaises(UserMistake):
            self.client.create_deposition()


class AddMetadataTest(unittest.TestCase):
    def setUp(self):
        url_base = API_BASE_URL_DEV
        good_token = TEST_API_TOKEN

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
                         'affiliation': 'Some Place'}],
        }
        self.client = Client(True, good_token)

    def test_success(self):
        self.client.add_metadata(self.deposition_id, self.good_metadata)

    def test_bad_data(self):
        with self.assertRaises(Exception):
            self.client.add_metadata(self.deposition_id, {})

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.add_metadata('1010101', self.good_metadata)


class AddFileTest(unittest.TestCase):
    def setUp(self):
        url_base = API_BASE_URL_DEV
        good_token = TEST_API_TOKEN

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
                         'affiliation': 'Some Place'}],
        }

        self.good_filepath = test_filename
        self.client = Client(True, good_token)

    def test_success(self):
        file_id = self.client.add_file(self.deposition_id, self.good_filepath)
        self.assertIsNotNone(file_id)

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.add_file('1010101', self.good_filepath)

    def test_bad_file(self):
        with self.assertRaises(Exception):
            self.client.add_file(self.deposition_id, 'notafile')


class PublishDepositionTest(unittest.TestCase):
    def setUp(self):
        url_base = API_BASE_URL_DEV
        good_token = TEST_API_TOKEN

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
                         'affiliation': 'Some Place'}],
        }
        filepath = test_filename

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)

    def test_success(self):
        doi = self.client.publish_deposition(self.deposition_id)
        self.assertIsNotNone(doi)

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.publish_deposition('1010101')


class NewDepositionVersionTest(unittest.TestCase):

    def setUp(self):
        url_base = API_BASE_URL_DEV
        good_token = TEST_API_TOKEN

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
                         'affiliation': 'Some Place'}],
        }
        filepath = test_filename

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)
        self.client.publish_deposition(self.deposition_id)

    def test_success(self):
        new_record_id = self.client.new_deposition_version(self.deposition_id)
        self.assertIsNotNone(new_record_id)

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.new_deposition_version('1010101')


class PublishNewVersionTest(unittest.TestCase):
    def setUp(self):
        url_base = API_BASE_URL_DEV
        good_token = TEST_API_TOKEN

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
                         'affiliation': 'Some Place'}],
        }
        filepath = test_filename

        self.client = Client(True, good_token)
        self.client.add_metadata(self.deposition_id, metadata)
        self.client.add_file(self.deposition_id, filepath)
        self.client.publish_deposition(self.deposition_id)

    def test_user_error(self):
        new_id = self.client.new_deposition_version(self.deposition_id)
        with self.assertRaises(UserMistake):
            self.client.publish_deposition(new_id)


class GetFilesTest(unittest.TestCase):
    def setUp(self):
        good_token = TEST_API_TOKEN
        self.client = Client(True, good_token)

    def test_success(self):
        new_id = self.client.new_deposition_version('355162')
        file_ids = self.client.get_deposition_files(new_id)
        self.assertNotEqual(len(file_ids), 0)

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.get_deposition_files('1010101')


class DeleteFilesSuccessTest(unittest.TestCase):
    def setUp(self):
        good_token = TEST_API_TOKEN
        self.client = Client(True, good_token)
        self.new_id = self.client.new_deposition_version('355162')
        self.file_ids = self.client.get_deposition_files(self.new_id)
        cmd = "echo "+str(datetime.now())+" > "+test_filename
        os.system(cmd)

    def test_success(self):
        self.client.delete_deposition_files(self.new_id, self.file_ids)

    def tearDown(self):
        filepath = test_filename
        self.client.add_file(self.new_id, filepath)
        self.client.publish_deposition(self.new_id)


class DeleteFilesFailTest(unittest.TestCase):
    def setUp(self):
        good_token = TEST_API_TOKEN
        self.client = Client(True, good_token)

    def test_bad_id(self):
        with self.assertRaises(Exception):
            self.client.delete_deposition_files('1010101', ['1'])


def tearDownModule():
    test_file.close()
