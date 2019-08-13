import os
import shutil
import sqlite3
import tempfile
import unittest

from jupyterlab_zenodo.utils import UserMistake, get_id, zip_dir

class GetIdTest(unittest.TestCase):
    def test_good_doi(self):
        dep_id = get_id('10.5281/zenodo.3357455')
        self.assertEqual(dep_id, '3357455') 

    def invalid_doi(self):
        with self.assertRaises(Exception): get_id('notadoi')

    def num_invalid_doi(self):
        with self.assertRaises(Exception): get_id('127381273')

    def non_zenodo_doi(self):
        with self.assertRaises(Exception): get_id('11111/notzenodo.123123')

    def test_empty_doi(self):
        with self.assertRaises(Exception): get_id('')

class ZipDirTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.loc = tempfile.mkdtemp()
        
    def test_empty(self):
        filepath = zip_dir(self.dir, "myfile")

        self.assertTrue(os.path.exists(filepath))

    def test_with_dotzip(self):
        os.system("touch "+self.dir+"/file1")
        os.system("touch "+self.dir+"/file2")
        os.system("echo 'hi' > "+self.dir+"/file1")
        os.system("echo 'hello' > "+self.dir+"/file2")
        filepath = zip_dir(self.dir, "myfile.zip")
        self.assertTrue(os.path.exists(filepath))

    def test_no_dotzip(self):
        os.system("touch "+self.dir+"/file1")
        os.system("touch "+self.dir+"/file2")
        os.system("echo 'hi' > "+self.dir+"/file1")
        os.system("echo 'hello' > "+self.dir+"/file2")
        filepath = zip_dir(self.dir, "myfile")
        self.assertTrue(os.path.exists(filepath))

    def test_with_slash(self):
        os.system("touch "+self.dir+"/file1")
        os.system("echo 'hi' > "+self.dir+"/file1")
        this_dir = self.dir + "/"
        filepath = zip_dir(this_dir, "myfile")
        self.assertTrue(os.path.exists(filepath))

    def test_bad_dir(self):
        bad_dir = self.dir+"not_a_directory"
        self.assertFalse(os.path.exists(bad_dir))
        with self.assertRaises(UserMistake): zip_dir(bad_dir,"myfile")

    def tearDown(self):
        shutil.rmtree(self.dir)
        shutil.rmtree(self.loc)

