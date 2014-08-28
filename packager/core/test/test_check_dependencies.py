#! /usr/bin/python

from check_dependencies import CheckDependencies

def test_default():
    CheckDependencies(None)

def test_hydrotrend():
    CheckDependencies("hydrotrend")

def test_cem():
    CheckDependencies("cem")

def test_child():
    CheckDependencies("child")

def test_child():
    CheckDependencies("sedflux")
