import os
import shutil
import sqlite3
import tempfile
import unittest

from jupyterlab_zenodo.utils import (UserMistake, get_id, zip_dir,
                                     add_query_parameter)


class AddQueryParameterTest(unittest.TestCase):
    def setUp(self):
        self.params = {'arg1': 1, 'arg2': 2, 'arg3': 3}
        self.url = "http://test_url.com"

    def test_no_url(self):
        with self.assertRaises(Exception):
            add_query_parameter(None, params)

    def test_empty_url(self):
        with self.assertRaises(Exception):
            add_query_parameter("", params)

    def test_no_params(self):
        with self.assertRaises(Exception):
            add_query_parameter(self.url, None)

    def test_empty_params(self):
        with self.assertRaises(Exception):
            add_query_parameter(self.url, {})

    def test_one_arg_from_zero(self):
        url = add_query_parameter(self.url, {'arg1': 1})
        self.assertEqual(url, self.url+"?arg1=1")

    def test_multiple_args_from_zero(self):
        url = add_query_parameter(self.url, self.params)
        self.assertEqual(url, self.url+"?arg1=1&arg2=2&arg3=3")

    def test_one_arg_from_multiple(self):
        new_url = self.url + "?test=test"
        url = add_query_parameter(new_url, {'arg1': 1})
        self.assertEqual(url, new_url+"&arg1=1")

    def test_multiple_args_from_multiple(self):
        new_url = self.url + "?test=test"
        url = add_query_parameter(new_url, self.params)
        self.assertEqual(url, new_url+"&arg1=1&arg2=2&arg3=3")


class GetIdTest(unittest.TestCase):
    def test_good_doi(self):
        dep_id = get_id('10.5281/zenodo.3357455')
        self.assertEqual(dep_id, '3357455')

    def invalid_doi(self):
        with self.assertRaises(Exception):
            get_id('notadoi')

    def num_invalid_doi(self):
        with self.assertRaises(Exception):
            get_id('127381273')

    def non_zenodo_doi(self):
        with self.assertRaises(Exception):
            get_id('11111/notzenodo.123123')

    def test_empty_doi(self):
        with self.assertRaises(Exception):
            get_id('')


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
        with self.assertRaises(UserMistake):
            zip_dir(bad_dir, "myfile")

    def tearDown(self):
        shutil.rmtree(self.dir)
        shutil.rmtree(self.loc)
