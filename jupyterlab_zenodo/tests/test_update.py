from datetime import datetime
import os
import sqlite3
import unittest

from ..update import get_last_upload, process_upload_data
from ..utils import UserMistake
 

sample_info = ['somedate','somedoi','somedir','somedir/somefile','sometoken']

class ProcessUploadDataTest(unittest.TestCase):
    def test_missing_data(self):
        sample_info = ['somedate','somedoi','somedir','somedir/somefile','sometoken']

class GetLastUploadNoDBTest(unittest.TestCase):
    def setUp(self):
        self.db_dest = "***REMOVED***work/.zenodo/"
    def test_fail(self):
        with self.assertRaises(UserMistake): get_last_upload(self.db_dest)

class GetLastUploadTest(unittest.TestCase):
    def setUp(self):
        self.info = {
            'date_uploaded' : datetime.now(),
            'doi' : 'some_doi',
            'directory' : 'mydir',
            'filepath' : 'somedir/file.zip',
            'access_token' : 'sometoken',
        }
        self.db_dest = "***REMOVED***work/.zenodo/"
        exists = os.path.exists(self.db_dest)
        if not exists:
            cmd = "mkdir " + self.db_dest
            os.system(cmd)
        conn = sqlite3.connect(self.db_dest+'zenodo.db')
        c = conn.cursor()
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory, filepath, access_token)")

    def test_success(self):
        conn = sqlite3.connect(self.db_dest+'zenodo.db')
        c = conn.cursor()
        c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)",[
            self.info['date_uploaded'],
            self.info['doi'],
            self.info['directory'],
            self.info['filepath'],
            self.info['access_token'],
        ])
        conn.commit()
        c.close()

        info_dict = get_last_upload(self.db_dest)
        self.assertEqual(info_dict['date'], str(self.info['date_uploaded']))
        self.assertEqual(info_dict['doi'], self.info['doi'])
        self.assertEqual(info_dict['directory'], self.info['directory'])
        self.assertEqual(info_dict['filepath'], self.info['filepath'])
        self.assertEqual(info_dict['access_token'], self.info['access_token'])

    def tearDown(self):
        cmd = "rm -rf " + self.db_dest
        os.system(cmd)
         

