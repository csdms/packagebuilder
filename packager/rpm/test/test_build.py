#! /usr/bin/python

from packager.rpm.build import BuildRPM
from nose.tools import *

model_name = "hydrotrend"

@raises(TypeError)
def test_fail_with_no_parameters():
    BuildRPM()

# def test_model_version_none():
#     BuildRPM(model_name, None, None, None, None)

# def test_model_version_head():
#     BuildRPM(model_name, "head", None, None, None)

#def test_model_tagged_version():
#    BuildRPM(model_name, "3.0.2")
