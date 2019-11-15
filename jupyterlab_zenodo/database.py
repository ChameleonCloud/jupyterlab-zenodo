""" Helper functions for storing and retrieving data about Zenodo uploads """
from datetime import datetime
import logging
import os
import sqlite3

from .utils import UserMistake

LOG = logging.getLogger(__name__)


def store_record(doi, directory, db_path):
    """Store a record of publication in the sqlite database db_path

    Parameters
    ----------
    doi : string
        Zenodo DOI given to uploaded record
    directory : string
        Directory just compressed and uploaded

    Returns
    -------
    void
    """
    if not doi:
        raise ValueError('Missing DOI')

    # Connect to database
    with Connection(db_path) as c:
        # Create uploads table if it doesn't exist
        try:
            c.execute("CREATE TABLE uploads (date_uploaded, doi, directory)")
        except sqlite3.OperationalError:
            pass

        # Add data to table
        c.execute("INSERT INTO uploads VALUES (?,?,?)",
                [datetime.now(), doi, directory])


def check_status(db_path):
    """Look in a local sqlite database to see Zenodo upload status
    Parameters
    ---------
    none
    Returns
    -------
    list
        Empty if no records, otherwise contains DOI and path tuples

    Notes:
    none
    """
    with Connection(db_path) as c:
        # Get last upload if it exists, otherwise return none
        try:
            c.execute("SELECT directory, doi FROM uploads ORDER BY date_uploaded DESC")
        except sqlite3.OperationalError:
            return []
        else:
            return [dict(zip(('path', 'doi'), row)) for row in c.fetchall()]


def get_last_upload(db_path):
    """Get information about the last upload
    Parameters
    ----------
    db_path : string
        Supposed location of sqlite database with upload information

    Returns
    -------
    Dictionary
        Contains date, doi, directory
    """
    no_uploads_error = ("No previous upload. Press 'Upload to Zenodo' "
                        "to create a new deposition")

    with Connection(db_path) as c:
        # If the table is empty or doesn't exist, there are no uploads
        try:
            c.execute("SELECT date_uploaded, doi, directory "
                      "FROM uploads ORDER BY date_uploaded DESC")
        except sqlite3.OperationalError:
            raise UserMistake(no_uploads_error)
        else:
            # Fetch info, close connection
            last_upload = c.fetchone()

    if last_upload == []:
        raise UserMistake(no_uploads_error)

    if any(map(lambda x: x == '', last_upload)):
        raise Exception("Missing information in last upload: empty values")

    labels = ['date', 'doi', 'directory']
    return dict(zip(labels, last_upload))


class Connection(object):
    """
    A simple context manager for a sqlite connection, which handles
    the automatic disconnect/commit of the current transaction
    """
    def __init__(self, db_path):
        dirname = os.path.dirname(db_path)
        if not os.path.exists(dirname):
            os.mkdir(dirname, 0o750)
        # Connect to database
        self.connection = sqlite3.connect(db_path)

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.connection.close()
