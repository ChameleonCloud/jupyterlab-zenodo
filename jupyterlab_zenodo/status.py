""" JupyterLab Zenodo : Checking status of Zenodo upload """

import glob, json, re, os
import requests
import sqlite3
from urllib.parse import unquote_plus, parse_qs
from datetime import datetime
from contextlib import contextmanager

from tornado import escape, gen, web

from notebook.base.handlers import APIHandler

from .base import ZenodoBaseHandler

class ZenodoStatusHandler(ZenodoBaseHandler):
    """
    A handler that uploads your files to Zenodo
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
        print(db_dest)
        try:
            conn = sqlite3.connect(db_dest+'zenodo.db')
            c = conn.cursor()
            c.execute("SELECT doi FROM uploads ORDER BY date_uploaded DESC")
            rows = c.fetchall()
            return rows[0][0]
        except Exception as e:
            print(e)
            return None

    @web.authenticated
    @gen.coroutine
    def get(self, path=''):
        doi = self.check_status()
        if doi is None:
            info = {'status': 'No publications'}
        else:
            info = {'status': 'Deposition published', 'doi': doi}
        self.write(json.dumps(info))
        self.finish()
        
        
