from notebook.base.handlers import APIHandler
from notebook.utils import url_escape
from re import sub
from tornado.httputil import url_concat
import json

class ZenodoBaseHandler(APIHandler):

    def return_error(self, error_message):
        info = {
            'status':'failure',
            'message': error_message,
            'doi' : None
        }
        self.set_status(400)
        self.write(json.dumps(info))
        self.finish()
        return


