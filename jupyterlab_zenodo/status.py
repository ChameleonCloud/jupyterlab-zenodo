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
            doi = check_status(self.db_dest, self.db_name)
        except Exception as x:
            # All other exceptions are internal
            LOG.exception("There was an error!")
            self.return_error("Something went wrong")
        else:
            if doi is None:
                info = {'status': 'No publications'}
            else:
                info = {'status': 'Deposition published', 'doi': doi}
            self.write(info)
            self.finish()
