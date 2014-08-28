#! /usr/bin/python
#
# Checks that the packages required to build an RPM for a given model
# are present on the system.
#
# Usage:
#   $ python check_dependencies.py --help
#   $ python check_dependencies.py -m "hydrotrend"
#
# Mark Piper (mark.piper@colorado.edu)

import sys
import os.path
from subprocess import call
import argparse

class CheckDependencies:
    '''
    Checks the dependencies for building an RPM for a given model.
    '''
    def __init__(self, model_name):
        self.dirname = os.path.dirname(os.path.realpath(__file__))
        self.model_name = model_name
        self.debian_check()

        # Read dependencies for all models.
        self.dependencies_file = self.dirname
        if self.is_debian:
            self.dependencies_file += "/config/dependencies_debian.txt"
            self.distro = "Debian"
            self.package_tool = "apt-get"
        else:
            self.dependencies_file += "/config/dependencies.txt"
            self.distro = "RHEL"
            self.package_tool = "yum"
        self.dependencies = self.read(self.dependencies_file)

        # Read additional dependencies for the requested model.
        if (self.model_name != None) and not self.is_debian:
            self.model_dependencies_file = self.dirname \
                                           + "/" + self.model_name \
                                           + "/dependencies.txt"
            if os.path.isfile(self.model_dependencies_file):
                subdependencies = self.read(self.model_dependencies_file)
                self.dependencies.extend(subdependencies)

        # Check that all the dependencies are met.
        self.check()
        print("All required packages are installed.")

    def debian_check(self):
        ''' 
        True if this is a Debian-based Linux system.
        '''
        self.is_debian = (call(["test", "-f", "/etc/debian_version"]) == 0)

    def read(self, fname):
        '''
        Reads a list of required package names, as strings, from the given
        text file.
        '''
        with open(fname, "r") as f:
            deps = f.read().split("\n")
        deps.pop(0) # remove first and
        deps.pop()  # last items from list
        return deps

    def query_package_tool(self, package):
        '''
        Calls the distro-specific package tool to query whether the given
        package is installed.
        '''
        if self.is_debian:
            return call(["dpkg-query", "-W", package])
        else:
            print(" - " + package)
            return call(["rpm", "-q", "--quiet", package])

    def check(self):
        '''
        Performs the checks for the required packages.
        '''
        print("Checking " + self.distro + "-compatible dependencies:")
        for package in self.dependencies:
            ret = self.query_package_tool(package)
            if ret > 0:
                print("The package '" + package + "' is required. "
                      "Install it with:\n$ sudo " + self.package_tool
                      + " install " + package)
                sys.exit(1) # package not installed

#-----------------------------------------------------------------------------

def main():
    '''
    Accepts command-line arguments and passes them to an instance of 
    CheckDependencies.
    '''
    # Allow only Linuxen.
    if not sys.platform.startswith('linux'):
        print("Error: this OS is not supported.")
        sys.exit(1) # not Linux

    # Which model is being checked?
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model",
                        help="the name of the model to check")
    args = parser.parse_args()

    CheckDependencies(args.model)

if __name__ == "__main__":
    main()
