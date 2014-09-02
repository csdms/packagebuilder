import sys
import os, shutil
import urllib
import zipfile
import tempfile

def download(repo, dest="."):
    '''
    Downloads a zip archive of the given repository to the specified 
    (default is current) directory.
    '''
    url = "https://github.com/{0}/archive/master.zip".format(repo)
    local_file = os.path.join(dest, os.path.basename(repo) + ".zip")
    urllib.urlretrieve(url, local_file)
    return local_file

def unpack(file, dest="."):
    '''
    Unpacks a zip archive containing the contents of the repo to the
    specified (default is current) directory. 
    '''
    zip = zipfile.ZipFile(file, mode='r')
    zip.extractall(dest)
    files = zip.namelist()
    prefix = os.path.commonprefix(files)
    return os.path.join(dest, prefix)

def read(fname):
    '''
    Reads a list of items, as strings, from a text file.
    '''
    with open(fname, "r") as f:
        items = f.read().split("\n")
    items.pop(0) # remove first and
    items.pop()  # last items from list
    return items

def get_module(module_name, dest="."):
    '''
    Downloads a set of repositories and attempts to locate the directory
    containing the setup files for the given module. If found, the directory
    path is returned.
    '''
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    repo_file = os.path.join(data_dir, "repositories.txt")
    repos = read(repo_file)
    for r in repos:
        zip_file = download(r, dest)
        unpack_dir = unpack(zip_file, dest)
        module_dir = os.path.join(unpack_dir, module_name, "")
        if os.path.isdir(module_dir):
            return module_dir
    return None

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

