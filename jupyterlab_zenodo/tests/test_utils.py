import os
import sqlite3
import unittest

from jupyterlab_zenodo.utils import UserMistake, get_id, zip_dir

class GetIdTest(unittest.TestCase):
    def test_good_doi(self):
        dep_id = get_id('10.5281/zenodo.3357455')
        self.assertEqual(dep_id, '3357455') 

    def test_empty_doi(self):
        with self.assertRaises(Exception): get_id('')

class ZipDirTest(unittest.TestCase):
    def setUp(self):
        self.dir = "***REMOVED***directory_of_things/"
        os.system("mkdir "+self.dir)
        self.loc = "***REMOVED***work/"
        
    def test_empty(self):
        filepath = zip_dir(self.dir, "myfile")
        os.system("rm -rf "+self.dir)

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
        bad_dir = "***REMOVED***not_a_directory"
        self.assertFalse(os.path.exists(bad_dir))
        with self.assertRaises(UserMistake): zip_dir(bad_dir,"myfile")

    def tearDown(self):
        os.system("rm -rf "+self.dir)

