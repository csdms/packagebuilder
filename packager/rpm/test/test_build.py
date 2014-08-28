#! /usr/bin/python

from build_rpm import BuildModelRPM
from nose.tools import *

@raises(TypeError)
def test_fail_with_no_parameters():
    BuildModelRPM(None)

@raises(TypeError)
def test_fail_with_one_parameter():
    BuildModelRPM("hydrotrend")

def test_hydrotrend_version_none():
    BuildModelRPM("hydrotrend", None)

def test_hydrotrend_version_head():
    BuildModelRPM("hydrotrend", "head")

#def test_hydrotrend_tagged_version():
#    BuildModelRPM("hydrotrend", "3.0.2")

def test_cem_version_head():
    BuildModelRPM("cem", "head")

#def test_cem_tagged_version():
#    BuildModelRPM("cem", "0.2")

def test_child_version_head():
    BuildModelRPM("child", "head")

def test_child_version_head():
    BuildModelRPM("sedflux", "head")
