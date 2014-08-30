import sys
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

def get_module(module_name, dest="."):
    '''
    Given the name of a model or tool, ...
    '''
    models_zipfile = download("csdms/rpm_models", dest) # TODO repositories.txt
    tools_zipfile = download("csdms/rpm_tools", dest)
    models_dir = unpack(models_zipfile, dest) 
    tools_dir = unpack(tools_zipfile, dest) 
    tmp1 = os.path.join(models_dir, module_name, "")
    tmp2 = os.path.join(tools_dir, module_name, "")
    if os.path.isdir(tmp1):
        module_dir = tmp1
    elif os.path.isdir(tmp2):
        module_dir = tmp2
    else:
        print("The module '" + module_name + "' cannot be located.")
        sys.exit(3) # can't find module
    return module_dir

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

