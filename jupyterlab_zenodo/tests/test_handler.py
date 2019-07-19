import json
from notebook.notebookapp import NotebookApp
from tempfile import TemporaryDirectory
import tornado
from tornado.testing import AsyncHTTPTestCase
from traitlets.config.loader import Config

#from jupyterlab_zenodo import load_jupyter_server_extension
from jupyterlab_zenodo import load_jupyter_server_extension

class TestZenodoHandler(AsyncHTTPTestCase):
    def get_app(self):
        nbapp = NotebookApp(notebook_dir=TemporaryDirectory.name())
        nbapp.initialize()
        load_jupyter_server_extension(nbapp)

        self.config = nbapp.config

        return nbapp.web_app

    #@tornado.testing.gen_test
    def test_upload(self):
        response = self.fetch('/zenodo/upload')
        self.assertEqual(response.code, 200)
        response_json = json.loads(resposne.body.decode('utf-8'))
        self.AssertEqual(response_json['status'],'success')
        # self.AssertEqual("yes","no")
        print(response_json['doi'])

    #def runTest(self):
    #    self.get_app()
    #    self.test_upload()

#if __name__ == "__main__":
#    tornado.testing.main()

#a = TestZenodoHandler()
#a.test_upload()
