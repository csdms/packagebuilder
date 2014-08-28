#! /usr/bin/python
#
# Builds binary and source RPMs for a model in the CSDMS repository.
#
# Arguments:
#   the model name (required)
#   -t is the tagged model version (optional)
#   -h shows the help message
#
# Usage:
#   $ python build_rpm.py --help
#   $ python build_rpm.py hydrotrend
#   $ python build_rpm.py cem --tag 0.2
#
# Mark Piper (mark.piper@colorado.edu)

import sys, os, shutil
import argparse
from subprocess import call
import string
import glob
import shlex

class BuildModelRPM:
    '''
    Calls the distro-specific tool to build an RPM for a model from
    its source code.
    '''
    def __init__(self, model_name, model_version):
        self.top_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep

        if not os.path.isdir(self.top_dir + model_name):
            print("The model '" + model_name + "' cannot be located.")
            sys.exit(3) # can't find model

        self.model = model_name            
        self.version = "head" if model_version == None else model_version

        # Model directory and setup files.
        self.model_dir = self.top_dir + self.model + os.sep
        self.dependencies_file = self.model_dir + "dependencies.txt"
        self.source_file = self.model_dir + "source.txt"
        self.spec_file = self.model_dir + self.model + ".spec"

        # Set up the rpmbuild directory.
        self.rpmbuild = os.getenv("HOME") + os.sep + "rpmbuild" + os.sep
        self.prep_directory()

        # Download the model's source code.
        self.get_source()

        # Make a tarball from the model's source.
        self.make_tarball()

        # Apply patches, if any.
        self.patch()

        # Build the binary and source RPMs.
        self.debian_check()
        self.get_dependencies()
        self.build()
        print("Success!")

    def debian_check(self):
        ''' 
        True if this is a Debian-based Linux system.
        '''
        self.is_debian = (call(["test", "-f", "/etc/debian_version"]) == 0)

    def prep_directory(self):
        '''
        Prepares the RPM build directory with built-in RPM dev tools.
        Sets up member variables for paths in the build directory.
        '''
        print("Setting up rpmbuild directory structure.")
        if os.path.isdir(self.rpmbuild):
            call(["rpmdev-wipetree"])
        else:
            call(["rpmdev-setuptree"])
        self.sources_dir = self.rpmbuild + "SOURCES" + os.sep
        self.specs_dir = self.rpmbuild + "SPECS" + os.sep

    def get_source(self):
        '''
        Retrieves the model source from an external repository.
        '''
        print("Getting " + self.model + " source.")
        self.source_target = self.sources_dir + self.model + "-" + self.version
        with open(self.source_file, "r") as f:
            cmd = f.readline().strip()
        cmd += " " + self.source_target
        ret = call(cmd, shell=True)
        if ret != 0:
            print("Unable to download model source.")
            sys.exit(4) # can't access source

    def make_tarball(self):
        '''
        Makes a tarball (required by rpmbuild) from the model source.
        '''
        print("Making tarball.")
        shutil.make_archive(self.source_target, 'gztar', self.sources_dir, \
                            os.path.basename(self.source_target))
        shutil.rmtree(self.source_target)

    def patch(self):
        '''
        Locates and includes patches (if any) for the build process. 
        Patches must use the extension ".patch".
        '''
        print("Applying patches.")
        for patch in glob.glob(self.model_dir + "*.patch"):
            shutil.copy(patch, self.sources_dir)

    def read(self, fname):
        '''
        Reads a list of items, as strings, from a text file.
        '''
        with open(fname, "r") as f:
            items = f.read().split("\n")
        items.pop(0) # remove first and
        items.pop()  # last items from list
        return items

    def get_dependencies(self):
        '''
        Assembles the list of dependencies for the model.
        '''
        if not os.path.isfile(self.dependencies_file):
            self.dependencies = "rpm" # XXX workaround; how to specify null?
        else:
            deps = self.read(self.dependencies_file)
            self.dependencies = string.join(deps, ", ")

    def build(self):
        '''
        Build binary and source RPMS.
        '''
        print("Building RPMs.")
        shutil.copy(self.spec_file, self.specs_dir)
        cmd = "rpmbuild -ba --quiet " \
            + self.specs_dir + os.path.basename(self.spec_file) \
            + " --define '_version " + self.version + "'"
        if not self.is_debian:
            cmd += " --define '_buildrequires " + self.dependencies + "'"
        print(cmd)
        ret = call(shlex.split(cmd))
        if ret != 0:
            print("Error in building model RPM.")
            sys.exit(2) # can't build RPM

#-----------------------------------------------------------------------------

def main():
    '''
    Accepts command-line arguments and passes them to an instance of
    BuildModelRPM.
    '''
    # Allow only Linuxen.
    if not sys.platform.startswith('linux'):
        print("Error: this OS is not supported.")
        sys.exit(1) # not Linux

    # Which model is being built?
    parser = argparse.ArgumentParser()
    parser.add_argument("model",
                        help="the name of the model to build")
    parser.add_argument("-t", "--tag",
                        help="the tagged version of the model")
    args = parser.parse_args()

    BuildModelRPM(args.model, args.tag)

if __name__ == "__main__":
    main()
