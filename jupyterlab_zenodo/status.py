""" JupyterLab Zenodo : Checking status of Zenodo upload """

import sqlite3

from tornado import gen, web

from .base import ZenodoBaseHandler

class ZenodoStatusHandler(ZenodoBaseHandler):
    """
    A handler that checks to see if anything has been uploaded
    """

    def check_status(self):
        """Look in a local sqlite database to see Zenodo upload status

        Parameters
        ---------
        none

        Returns
        -------
        string
            Empty if no record, otherwise contains most recent upload doi


        Notes:
        none
        """

        db_dest = "/work/.zenodo/"

        conn = sqlite3.connect(db_dest+'zenodo.db')
        c = conn.cursor()

        # Get last upload if it exists, otherwise return none
        try:
            c.execute("SELECT doi FROM uploads ORDER BY date_uploaded DESC")
        except:
            return None
        else:
            rows = c.fetchall()
            return rows[0][0]

    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        doi = self.check_status()
        if doi is None:
            info = {'status': 'No publications'}
        else:
            info = {'status': 'Deposition published', 'doi': doi}
        self.write(info)
        self.finish()
        
        
