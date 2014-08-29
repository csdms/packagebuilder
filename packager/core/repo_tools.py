import os, shutil
import urllib
import zipfile
import tempfile

def download(repo, dest="."):
    '''
    Downloads a zip archive of the given repository to the current 
    directory.
    '''
    url = "https://github.com/{0}/archive/master.zip".format(repo)
    local_file = os.path.join(dest, os.path.basename(repo) + ".zip")
    urllib.urlretrieve(url, local_file)
    return local_file

def unpack(file, dest="."):
    '''
    Unpacks a zip archive containing the contents of the repo to the 
    current directory.
    '''
    zip = zipfile.ZipFile(file, mode='r')
    zip.extractall(dest)
    files = zip.namelist()
    prefix = os.path.commonprefix(files)
    return os.path.join(dest, prefix)

def main():
    repo = "csdms/rpm_models"
    tmp_dir = tempfile.mkdtemp(prefix=main.__module__)
    try:
        zip_file = download(repo, dest=tmp_dir)
        unpack_dir = unpack(zip_file, dest=tmp_dir)
    except Exception:
        raise
    finally:
        shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    main()

