from datetime import datetime
import os
import tempfile
import unittest

from jupyterlab_zenodo.test_init import TEST_API_TOKEN
from jupyterlab_zenodo.zenodo import Deposition

TEST_DEP_ID = '355162'


def setUpModule():
    global test_file
    global test_filename
    test_file = tempfile.NamedTemporaryFile()
    test_file.write(b'Hello world')
    test_filename = test_file.name


class InitTest(unittest.TestCase):
    def test_success(self):
        token = TEST_API_TOKEN
        dep = Deposition(True, token)

    def test_success_existing(self):
        token = TEST_API_TOKEN
        dep = Deposition(True, token, TEST_DEP_ID)


class ZenodoInitTest(unittest.TestCase):
    def test_success(self):
        token = TEST_API_TOKEN
        dep = Deposition(True, token)
        dep.zenodo_init()
        self.assertIsNotNone(dep.id)


class SetMetadataTest(unittest.TestCase):
    def setUp(self):
        token = TEST_API_TOKEN
        self.dep = Deposition(True, token)
        self.dep.zenodo_init()

        self.good_metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name',
                         'affiliation': 'Some Place'}],
        }

    def test_success(self):
        self.dep.set_metadata(self.good_metadata)
        self.assertIsNotNone(self.dep.metadata)

    def test_bad_data(self):
        with self.assertRaises(Exception):
            self.dep.set_metadata({})


class SetFileTest(unittest.TestCase):
    def setUp(self):
        token = TEST_API_TOKEN
        self.dep = Deposition(True, token)
        self.dep.zenodo_init()
        self.good_filepath = test_filename

    def test_success(self):
        self.dep.set_file(self.good_filepath)
        self.assertIsNotNone(self.dep.file_id)

    def test_bad_data(self):
        with self.assertRaises(Exception):
            self.dep.set_file('notafile')


class PublishTest(unittest.TestCase):
    def setUp(self):
        token = TEST_API_TOKEN
        self.dep = Deposition(True, token)
        self.dep.zenodo_init()
        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name',
                         'affiliation': 'Some Place'}],
        }
        self.dep.set_metadata(metadata)
        self.dep.set_file(test_filename)

    def test_success(self):
        self.dep.publish()
        self.assertIsNotNone(self.dep.doi)


class NewVersionTest(unittest.TestCase):
    def setUp(self):
        token = TEST_API_TOKEN
        self.dep = Deposition(True, token)
        self.dep.zenodo_init()
        metadata = {
            'title': 'Sample Title',
            'upload_type': 'publication',
            'publication_type': 'workingpaper',
            'description': 'This is a description',
            'creators': [{'name': 'Some Name',
                         'affiliation': 'Some Place'}],
        }
        self.dep.set_metadata(metadata)
        self.dep.set_file(test_filename)
        self.dep.publish()

    def test_success(self):
        old_id = self.dep.id
        self.dep.new_version()
        new_id = self.dep.id
        self.assertNotEqual(old_id, new_id)


class ClearFilesTest(unittest.TestCase):
    def setUp(self):
        token = TEST_API_TOKEN
        self.dep = Deposition(True, token, TEST_DEP_ID)
        self.dep.new_version()
        cmd = "echo "+str(datetime.now())+" > "+test_filename
        os.system(cmd)

    def test_success(self):
        self.dep.clear_files()

    def tearDown(self):
        filepath = test_filename
        self.dep.set_file(filepath)
        self.dep.publish()


def tearDownModule():
    test_file.close()
