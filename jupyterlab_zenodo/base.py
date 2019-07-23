from notebook.base.handlers import APIHandler
from notebook.utils import url_escape
from re import sub
from tornado.httputil import url_concat

class ZenodoBaseHandler(APIHandler):
    def api_path(self, path, params=None):
        return url_concat(url_escape(self.swift_path(path)), params)

    def api_params(self):
        query = self.request.query_arguments
        return { key: query[key][0].decode() for key in query }

