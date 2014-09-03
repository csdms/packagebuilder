#! /usr/bin/python

from packager.rpm.build import BuildRPM
from nose.tools import *

@raises(TypeError)
def test_fail_with_no_parameters():
    BuildRPM(None)

@raises(TypeError)
def test_fail_with_one_parameter():
    BuildRPM("hydrotrend")

def test_hydrotrend_version_none():
    BuildRPM("hydrotrend", None)

def test_hydrotrend_version_head():
    BuildRPM("hydrotrend", "head")

#def test_hydrotrend_tagged_version():
#    BuildRPM("hydrotrend", "3.0.2")

def test_cem_version_head():
    BuildRPM("cem", "head")

#def test_cem_tagged_version():
#    BuildRPM("cem", "0.2")

def test_child_version_head():
    BuildRPM("child", "head")

def test_sedflux_version_head():
    BuildRPM("sedflux", "head")

def test_adi2d_version_head():
    BuildRPM("adi-2d", "head")
