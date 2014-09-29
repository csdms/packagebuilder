#! /usr/bin/env python

from packager.core.module import Module
from nose.tools import *
from nose import with_setup

name = "hydrotrend"

@raises(TypeError)
def test_Module_noargs_fails():
    Module()

