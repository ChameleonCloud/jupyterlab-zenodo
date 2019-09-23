""" JupyterLab Zenodo : Checking status of Zenodo upload """

from tornado import gen, web

from .base import ZenodoBaseHandler
from .database import check_status


class ZenodoStatusHandler(ZenodoBaseHandler):
    """
    A handler that checks to see if anything has been uploaded
    """
    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        try:
            records = check_status(self.db_path)
        except Exception as x:
            # All other exceptions are internal
            self.log.exception("There was an error!")
            self.return_error("Something went wrong")
        else:
            self.write(dict(records=records))
            self.finish()
