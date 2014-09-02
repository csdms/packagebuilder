#! /usr/bin/python

import packager.core.repo_tools as repo
from nose.tools import *
from nose import with_setup
import os, shutil
import tempfile

repo_name = "csdms/rpm_tools"

# Setup fixture
def setup_func():
    global tmp_dir 
    tmp_dir = tempfile.mkdtemp()

# Teardown fixture
def teardown_func():
    shutil.rmtree(tmp_dir)    

@raises(TypeError)
def test_download_noargs_fails():
    repo.download()

def test_download_to_cwd():
    zip_file = repo.download(repo_name)
    assert_true(os.path.isfile(zip_file))

@with_setup(setup_func, teardown_func)
def test_download_to_tmp():
    zip_file = repo.download(repo_name, dest=tmp_dir)
    assert_true(os.path.isfile(zip_file))

def test_download_and_unpack_to_cwd():
    zip_file = repo.download(repo_name)
    unpack_dir = repo.unpack(zip_file)
    assert_true(os.path.isdir(unpack_dir))

# TODO
@with_setup(setup_func, teardown_func)
def test_download_and_unpack_to_tmp():
    pass

# TODO
def test_read():
    pass

# TODO
def test_get_module():
    pass

