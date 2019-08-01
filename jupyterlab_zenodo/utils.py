
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
    try:
        # Go to directly outside work directory
        cmd = "cd "+notebook_dir+"/.."
        os.system(cmd)
    except:
        raise Exception("Invalid directory. Please provide a real path, excluding leading /'s")
    
    try:
        # Zip work directory to filename
        cmd = "zip -r "+filename+" "+notebook_dir+"/"
        os.system(cmd) 
    except:
        raise Exception("Your files were unable to be compressed. Please try again.")

    # Final filename will end in .zip
    if filename[-4:] == '.zip':
        filepath = notebook_dir+'/../'+filename
    else:
        filepath = notebook_dir+'/../'+filename+'.zip'
        return filepath

def store_record(doi, filename, directory, access_token):
    """Store a record of publication in a local sqlite database

    Parameters
    ----------
    doi : string
        Zenodo DOI given to uploaded record
    filename : string
        Name of zip file that was uploaded
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
    c.execute("INSERT INTO uploads VALUES (?,?,?,?)",[datetime.now(),doi, directory, filename])
        # Commit and close
    conn.commit()
    conn.close()

