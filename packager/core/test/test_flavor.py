#! /usr/bin/python

from packager.core.flavor import debian_check
from nose.tools import *
from subprocess import call

def test_debian_check():
    ret = call(["test", "-f", "/etc/debian_version"]) == 0
    assert debian_check() == ret
