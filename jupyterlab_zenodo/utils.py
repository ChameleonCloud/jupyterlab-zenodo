from datetime import datetime
import os
import sqlite3
import tempfile
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

    # Create temporary directory for archive
    temp_dir = tempfile.mkdtemp();

    # Filename should end in .zip
    if filename[-4:] != '.zip':
        filename = filename+'.zip'

    # Zip everything in notebook_dir to temp_dir/filename
    filepath = temp_dir + "/" + filename
    
    zipf = zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(notebook_dir):
        for afile in files:
            zipf.write(os.path.join(root,afile));
    zipf.close()

    return filepath

def store_record(doi, filepath, directory, access_token):
    """Store a record of publication in a local sqlite database

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
    

    db_dest = "/work/.zenodo/"
	
    # Create directory if it doesn't exist
    if not os.path.exists(db_dest):
        cmd = "mkdir " + db_dest
        os.system(cmd)

    # Connect to database
    conn = sqlite3.connect(db_dest+'zenodo.db')
    c = conn.cursor()

    # Create uploads table if it doesn't exist
    try:
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory, filepath, access_token)")
    except sqlite3.OperationalError:
        pass

    # Add data to table
    c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)",[datetime.now(),doi, directory, filepath, access_token])

    # Commit and close
    conn.commit()
    conn.close()

