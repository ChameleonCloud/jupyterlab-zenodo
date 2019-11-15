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
        self.db_path = f"{self.test_dir}/databasefile"

    def test_no_path(self):
        store_record(self.doi, self.dir, f"{self.test_dir}new/{DB_NAME}")

    def test_existing_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory)")
        c.execute("INSERT INTO uploads VALUES (?,?,?)",
                  ["time", "doi", "directory"])
        conn.commit()
        conn.close()
        store_record(self.doi, self.dir, self.db_path)

    def test_missing_doi(self):
        with self.assertRaises(ValueError):
            store_record('', self.dir, self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class GetLastUploadNoDBTest(unittest.TestCase):
    def setUp(self):
        self.db_path = f"/not_a_directory/{str(datetime.now())}/{DB_NAME}"

    def test_fail(self):
        with self.assertRaises(FileNotFoundError):
            get_last_upload(self.db_path)


class GetLastUploadTest(unittest.TestCase):
    def setUp(self):
        self.info = {
            'date_uploaded': datetime.now(),
            'doi': 'some_doi',
            'directory': 'mydir',
        }
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = f"{self.temp_dir}/databasefile"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory)")

    def test_missing_data(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO uploads VALUES (?,?,?)", [
            self.info['date_uploaded'],
            "",
            self.info['directory'],
        ])
        conn.commit()
        c.close()

        with self.assertRaises(Exception):
            get_last_upload(self.db_path)

    def test_success(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO uploads VALUES (?,?,?)", [
            self.info['date_uploaded'],
            self.info['doi'],
            self.info['directory'],
        ])
        conn.commit()
        c.close()

        info_dict = get_last_upload(self.db_path)
        self.assertEqual(info_dict['date'], str(self.info['date_uploaded']))
        self.assertEqual(info_dict['doi'], self.info['doi'])
        self.assertEqual(info_dict['directory'], self.info['directory'])

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
