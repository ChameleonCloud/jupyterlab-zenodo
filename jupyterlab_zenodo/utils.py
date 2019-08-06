from datetime import datetime
import os
import sqlite3
import tempfile
import zipfile



def get_id(doi):
    """Parses Zenodo DOI to isolate record id"""
    if doi is None:
        raise Exception("Not given a doi")
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
        File prefix (ie before the '.zip') to zip to
    Returns
    -------
    string
        Full path of zipped file
    Notes
    -----
    - Error handling incomplete
    """  
    temp_dir = tempfile.mkdtemp();
    if filename[-4:] != '.zip':
        filename = filename+'.zip'
    # Final filename will end in .zip

    filepath = temp_dir + "/" + filename
    print(filepath)
    
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
    print(os.path.exists(db_dest))
    if not os.path.exists(db_dest):
        cmd = "mkdir" + db_dest
        os.system(cmd)
    conn = sqlite3.connect(db_dest+'zenodo.db')
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE uploads (date_uploaded, doi, directory, filename, access_token)")
    except:
        pass
    c.execute("INSERT INTO uploads VALUES (?,?,?,?,?)",[datetime.now(),doi, directory, filepath, access_token])
        # Commit and close
    conn.commit()
    conn.close()

