import json
from notebook.notebookapp import NotebookApp
from tempfile import TemporaryDirectory
import tornado
from tornado.testing import AsyncHTTPTestCase
from tornado import log
from traitlets.config.loader import Config
import os
from os import path

from jupyterlab_zenodo import load_jupyter_server_extension

class TestZenodoHandler(AsyncHTTPTestCase):
    def get_app(self):
        nbapp = NotebookApp(runtime_dir=TemporaryDirectory().name)
        nbapp.initialize()
        load_jupyter_server_extension(nbapp)

        self.config = nbapp.config

        return nbapp.web_app

    #@tornado.testing.gen_test
    '''
    def test_zip_bad_filename(self):
        notebook_dir = "test_1"
        filename = "temp"
        try:
            zip_dir(notebook_dir, filename)
        except Exception as ex:
            self.assertEqual(ex.message,"filename invalid")

    def test_zip_dir(self):
        notebook_dir = "test_1"
        cmd = "mkdir "+notebook_dir
        os.system(cmd)
        cmd = "echo 'hi' > "+notebook_dir+" test.txt"
        os.system(cmd)
        filename = "temp.zip"
        zip_dir(notebook_dir, filename)
        
        self.assertTrue(path.exists(filename))
    '''

    def test_true(self):
        self.assertEqual(True,True)

    def test_upload(self):
        response = self.fetch('/zenodo/upload?title=myTitle&author=me&description=nodescriptionthanks',method='POST', body=b'')
#        self.assertEqual(response.code, 200)
        response_json = json.loads(response.body.decode('utf-8'))
        print("hello")
        print(response_json)
        print("and that was the response")
        self.assertEqual(response_json['status'],'success')
        # self.AssertEqual("yes","no")
        print(response_json['doi'])

