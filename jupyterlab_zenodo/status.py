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
        doi = check_status()
        if doi is None:
            info = {'status': 'No publications'}
        else:
            info = {'status': 'Deposition published', 'doi': doi}
        self.write(info)
        self.finish()
        
        
