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
import tempfile
from subprocess import call
import string
import glob
import shlex
from packager.core import repo_tools as repo

class BuildRPM:
    '''
    Uses rpmbuild to build a CSDMS model or tool into an RPM.
    '''
    def __init__(self, module_name, module_version):

        # Get module setup files from GitHub and store in a tmp directory.
        
        self.tmpdir = tempfile.mkdtemp()

        # XXX Ugly
        models_zipfile = repo.download("csdms/rpm_models", self.tmpdir)
        tools_zipfile = repo.download("csdms/rpm_tools", self.tmpdir)
        models_dir = repo.unpack(models_zipfile, self.tmpdir) 
        tools_dir = repo.unpack(tools_zipfile, self.tmpdir) 

        # XXX Ugly
        tmp1 = os.path.join(models_dir, module_name, "")
        tmp2 = os.path.join(tools_dir, module_name, "")
        if os.path.isdir(tmp1):
            self.module_dir = tmp1
        elif os.path.isdir(tmp2):
            self.module_dir = tmp2
        else:
            print("The module '" + module_name + "' cannot be located.")
            sys.exit(3) # can't find module

        self.module = module_name
        self.version = "head" if module_version == None else module_version

        # Model setup files.
        self.deps_file = os.path.join(self.module_dir, "dependencies.txt")
        self.source_file = os.path.join(self.module_dir, "source.txt")
        self.spec_file = os.path.join(self.module_dir, self.module + ".spec")

        # Set up the local rpmbuild directory.
        self.rpmbuild = os.path.join(os.getenv("HOME"), "rpmbuild", "")
        self.prep_directory()

        # Download the module's source code.
        self.get_source()

        # Make a tarball from the module's source.
        self.make_tarball()

        # Apply patches, if any.
        self.patch()

        # Build the binary and source RPMs.
        self.debian_check()
        self.get_dependencies()
        self.build()
        self.cleanup()
        print("Success!")

    def debian_check(self):
        ''' 
        True if this is a Debian-based Linux system.
        '''
        self.is_debian = (call(["test", "-f", "/etc/debian_version"]) == 0)

    def prep_directory(self):
        '''
        Prepares the RPM build directory (~/rpmbuild) with built-in RPM dev
        tools. Sets up member variables for paths in the build directory.
        '''
        print("Setting up rpmbuild directory structure.")
        if os.path.isdir(self.rpmbuild):
            call(["rpmdev-wipetree"])
        else:
            call(["rpmdev-setuptree"])
        self.sources_dir = os.path.join(self.rpmbuild,  "SOURCES", "")
        self.specs_dir = os.path.join(self.rpmbuild,  "SPECS", "")

    def get_source(self):
        '''
        Retrieves the module source from an external repository.
        '''
        print("Getting " + self.module + " source.")
        self.source_target = self.sources_dir + self.module + "-" + self.version
        with open(self.source_file, "r") as f:
            cmd = f.readline().strip()
        cmd += " " + self.source_target
        ret = call(cmd, shell=True)
        if ret != 0:
            print("Unable to download module source.")
            sys.exit(4) # can't access source

    def make_tarball(self):
        '''
        Makes a tarball (required by rpmbuild) from the module source.
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
        for patch in glob.glob(self.module_dir + "*.patch"):
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
        Assembles the list of dependencies for the module.
        '''
        if not os.path.isfile(self.deps_file):
            self.dependencies = "rpm" # XXX workaround; how to specify null?
        else:
            deps = self.read(self.deps_file)
            self.dependencies = string.join(deps, ", ")

    def build(self):
        '''
        Build binary and source RPMS.
        '''
        print("Building RPMs.")
        shutil.copy(self.spec_file, self.specs_dir)
        cmd = "rpmbuild -ba --quiet " \
            + os.path.join(self.specs_dir, os.path.basename(self.spec_file)) \
            + " --define '_version " + self.version + "'"
        if not self.is_debian:
            cmd += " --define '_buildrequires " + self.dependencies + "'"
        print(cmd)
        ret = call(shlex.split(cmd))
        if ret != 0:
            print("Error in building module RPM.")
            sys.exit(2) # can't build RPM

    def cleanup(self):
        '''
        Deletes the directory used to store the downloaded archives from
        the rpm_models and rpm_tools repos.
        '''
        shutil.rmtree(self.tmpdir)
    
#-----------------------------------------------------------------------------

def main():
    '''
    Accepts command-line arguments and passes them to an instance of BuildRPM.
    '''
    # Allow only Linuxen.
    # if not sys.platform.startswith('linux'):
    #     print("Error: this OS is not supported.")
    #     sys.exit(1) # not Linux

    # What's being built?
    parser = argparse.ArgumentParser()
    parser.add_argument("module",
                        help="the name of the model or tool to build")
    parser.add_argument("-t", "--tag",
                        help="the tagged version of the module")
    args = parser.parse_args()

    BuildRPM(args.module, args.tag)

if __name__ == "__main__":
    main()
