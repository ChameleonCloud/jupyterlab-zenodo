""" Helper functions for storing and retrieving data about Zenodo uploads """
from datetime import datetime
import logging
import os
import sqlite3

from .utils import UserMistake

LOG = logging.getLogger(__name__)


def store_record(doi, filepath, directory, access_token, db_loc, db_name):
    """Store a record of publication in the sqlite database db_name

    Parameters
    ----------
    doi : string
        Zenodo DOI given to uploaded record
    filepath : string
        Full path of zip file that was uploaded
    directory : string
        Directory just compressed and uploaded
    access_token : string
        Zenodo access token used

    Returns
    -------
    void
    """
    LOG.info("Database: "+db_loc+db_name)

    if any(map(lambda x: not x, [doi, filepath, directory, access_token])):
        raise Exception("Given empty fields")

    # Create directory if it doesn't exist
    if not os.path.exists(db_loc):
        cmd = "mkdir " + db_loc
        os.system(cmd)

    # Connect to database
    conn = sqlite3.connect(db_loc+db_name)
    c = conn.cursor()

    # Create uploads table if it doesn't exist
    try:
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory,"
                  " filepath, access_token)")
    except sqlite3.OperationalError:
        pass

    # Add data to table
    c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)",
              [datetime.now(), doi, directory, filepath, access_token])

    # Commit and close
    conn.commit()
    conn.close()


def check_status(db_loc, db_name):
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
    LOG.info("Database: "+db_loc+db_name)

    conn = sqlite3.connect(db_loc+db_name)
    c = conn.cursor()

    # Get last upload if it exists, otherwise return none
    try:
        c.execute("SELECT doi FROM uploads ORDER BY date_uploaded DESC")
    except sqlite3.OperationalError as e:
        return None
    else:
        row = c.fetchone()
        return row[0]


def get_last_upload(db_loc, db_name):
    """Get information about the last upload
    Parameters
    ----------
    db_loc : string
        Supposed location of sqlite database with upload information

    Returns
    -------
    Dictionary
        Contains date, doi, directory, filepath, and access token
    """
    LOG.info("Database: "+db_loc+db_name)

    no_uploads_error = ("No previous upload. Press 'Upload to Zenodo' "
                        "to create a new deposition")
    # If the database location doesn't exist, there are no uploads
    if not os.path.exists(db_loc):
        LOG.warning("No db folder")
        raise UserMistake(no_uploads_error)

    # Connect to database
    conn = sqlite3.connect(db_loc+db_name)
    c = conn.cursor()

    # If the table is empty or doesn't exist, there are no uploads
    try:
        c.execute("SELECT date_uploaded, doi, directory, filepath, "
                  "access_token FROM uploads ORDER BY date_uploaded DESC")
    except sqlite3.OperationalError as e:
        raise UserMistake(no_uploads_error)

    # Fetch info, close connection
    last_upload = c.fetchone()
    conn.close()

    if last_upload == []:
        LOG.warn("data is empty: "+str(data))
        raise UserMistake(no_uploads_error)

    if any(map(lambda x: x == '', last_upload)):
        raise Exception("Missing information in last upload: empty values")

    labels = ['date', 'doi', 'directory', 'filepath', 'access_token']
    return dict(zip(labels, last_upload))
