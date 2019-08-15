from datetime import datetime
import shutil
import sqlite3
import tempfile
import unittest

from jupyterlab_zenodo.database import (store_record, check_status,
                                        get_last_upload)
from jupyterlab_zenodo.utils import UserMistake

sample_info = ['somedate', 'somedoi', 'somedir',
               'somedir/somefile', 'sometoken']

DB_DEST = '/work/.zenodo/'
DB_NAME = 'zenodo.db'


class StoreRecordTest(unittest.TestCase):
    def setUp(self):
        self.doi = "some/do.i"
        self.filepath = "some/file/path.zip"
        self.dir = "a_directory"
        self.tok = "atoken"
        self.test_dir = tempfile.mkdtemp()

    def test_no_path(self):
        not_a_dir = self.test_dir + "new/"
        store_record(self.doi, self.filepath, self.dir, self.tok,
                     not_a_dir, DB_NAME)

    def test_existing_db(self):
        name = 'zenodo.db'
        conn = sqlite3.connect(self.test_dir+name)
        c = conn.cursor()
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory,"
                  " filepath, access_token)")
        c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)",
                  ["time", "doi", "directory", "filepath", "access_token"])
        conn.commit()
        conn.close()
        store_record(self.doi, self.filepath, self.dir, self.tok,
                     self.test_dir, name)

    def test_missing_doi(self):
        with self.assertRaises(Exception):
            store_record("", self.filepath, self.dir, self.tok, self.test_dir)

    def test_missing_file(self):
        with self.assertRaises(Exception):
            store_record(self.doi, None, self.dir, self.tok, self.test_dir)

    def test_missing_dir(self):
        with self.assertRaises(Exception):
            store_record(self.doi, self.filepath, "", self.tok, self.test_dir)

    def test_missing_tok(self):
        with self.assertRaises(Exception):
            store_record(self.doi, self.filepath, self.dir, None,
                         self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class GetLastUploadNoDBTest(unittest.TestCase):
    def setUp(self):
        self.db_dest = "/not_a_directory"+str(datetime.now())

    def test_fail(self):
        with self.assertRaises(UserMistake):
            get_last_upload(self.db_dest, DB_NAME)


class GetLastUploadTest(unittest.TestCase):
    def setUp(self):
        self.info = {
            'date_uploaded': datetime.now(),
            'doi': 'some_doi',
            'directory': 'mydir',
            'filepath': 'somedir/file.zip',
            'access_token': 'sometoken',
        }
        self.temp_dir = tempfile.mkdtemp()
        self.temp_name = 'zenodo.db'
        conn = sqlite3.connect(self.temp_dir + self.temp_name)
        c = conn.cursor()
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory,"
                  " filepath, access_token)")

    def test_missing_data(self):
        conn = sqlite3.connect(self.temp_dir + self.temp_name)
        c = conn.cursor()
        c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)", [
            self.info['date_uploaded'],
            "",
            self.info['directory'],
            self.info['filepath'],
            self.info['access_token'],
        ])
        conn.commit()
        c.close()

        with self.assertRaises(Exception):
            get_last_upload(self.temp_dir, self.temp_name)

    def test_success(self):
        conn = sqlite3.connect(self.temp_dir+self.temp_name)
        c = conn.cursor()
        c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)", [
            self.info['date_uploaded'],
            self.info['doi'],
            self.info['directory'],
            self.info['filepath'],
            self.info['access_token'],
        ])
        conn.commit()
        c.close()

        info_dict = get_last_upload(self.temp_dir, self.temp_name)
        self.assertEqual(info_dict['date'], str(self.info['date_uploaded']))
        self.assertEqual(info_dict['doi'], self.info['doi'])
        self.assertEqual(info_dict['directory'], self.info['directory'])
        self.assertEqual(info_dict['filepath'], self.info['filepath'])
        self.assertEqual(info_dict['access_token'], self.info['access_token'])

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
