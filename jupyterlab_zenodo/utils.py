""" Helper functions and exceptions for the Zenodo extension """

from datetime import datetime
import os
import re
import tempfile
from urllib.parse import urlparse, urlencode
import zipfile


class UserMistake(Exception):
    """Raised when something went wrong due to user input"""
    pass


def get_id(doi):
    """Parses Zenodo DOI to isolate record id

    Parameters
    ----------
    doi : string
        doi to isolate record id from; must not be empty

    Returns
    ------
    string
        The Zenodo record id at the end of the doi

    Notes
    -----
    - DOIs are expected to be in the form 10.xxxx/zenodo.xxxxx
    - Behaviour is undefined if they are given in another format
    """

    if not doi:
        raise Exception("No doi")
    elif not re.match(r'10\.[0-9]+\/zenodo\.[0-9]+$', doi):
        raise Exception("Doi is invalid (wrong format)")
    else:
        record_id = doi.split('.')[-1]
        return record_id


def zip_dir(notebook_dir, filename):
    """Create zip file filename from notebook_dir

    Parameters
    ----------
    notebook_dir : string
        Explicit path to directory to be zipped
    filename : string
        Intended name of archive to zip to

    Returns
    -------
    string
        Full path of zipped file
    """
    if not os.path.exists(notebook_dir):
        raise UserMistake("That directory path is not valid. To use your"
                          " work directory, leave the directory field empty")

    # Create temporary directory for archive
    temp_dir = tempfile.mkdtemp()

    # Filename should end in .zip
    if filename[-4:] != '.zip':
        filename = filename+'.zip'

    # Zip everything in notebook_dir to temp_dir/filename
    filepath = temp_dir + "/" + filename

    zipf = zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(notebook_dir):
        for afile in files:
            zipf.write(os.path.join(root, afile))
    zipf.close()

    return filepath


def add_query_parameter(url, params):
    """Add query parameters to an existing url

    Parameters
    ----------
    url : string
        Url to add to
    params : dict
        Labels and values to add to url

    Returns
    -------
    string
        Updated url
    """
    if not params:
        raise Exception("No query arguments given")
    if not url:
        raise Exception("Empty url")

    url += ('&' if urlparse(url).query else '?') + urlencode(params)
    return url
