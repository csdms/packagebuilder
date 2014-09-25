#! /usr/bin/env python
#
# Builds binary and source RPMs for a CSDMS model or tool.
#
# Examples:
#   $ python build.py --help
#   $ python build.py hydrotrend
#   $ python build.py babel
#   $ python build.py cem --tag 0.2
#   $ python build.py hydrotrend --local $HOME/rpm_models
#   $ python build.py babel --prefix /usr/local/csdms
#
# Mark Piper (mark.piper@colorado.edu)

import sys, os, shutil
from subprocess import call
import string
import glob
import shlex
import tempfile
from packager.core import repo_tools as repo
from packager.core.flavor import debian_check

class BuildRPM:
    '''
    Uses `rpmbuild` to build a CSDMS model or tool into an RPM.
    '''
    def __init__(self, module_name, module_version, local_dir, prefix):
        self.module = module_name
        self.version = "head" if module_version == None else module_version
        self.install_prefix = "/usr/local" if prefix == None else prefix

        # Get module setup files 1) from GitHub and store in a tmp directory,
        # or 2) from a local directory.
        if local_dir == None:
            self.tmpdir = tempfile.mkdtemp()
            self.module_dir = repo.get_module(self.module, dest=self.tmpdir)
        else:
            self.module_dir = self.get_local_dir(local_dir)
        if self.module_dir == None:
            print("The module '" + self.module + "' cannot be located.")
            sys.exit(3) # can't find module

        # Model setup files.
        self.deps_file = os.path.join(self.module_dir, "dependencies.txt")
        self.source_file = os.path.join(self.module_dir, "source.txt")
        self.spec_file = os.path.join(self.module_dir, self.module + ".spec")

        # Set up the local rpmbuild directory.
        self.rpmbuild = os.path.join(os.getenv("HOME"), "rpmbuild", "")
        self.prep_directory()

        # Download the module's source code. Make a tarball.
        self.get_source()
        if self.needs_tarball: self.make_tarball()

        # Apply patches, if any.
        self.patch()

        # Build the binary and source RPMs.
        self.is_debian = debian_check()
        self.get_dependencies()
        self.build()
        self.cleanup()
        print("Success!")

    def get_local_dir(self, locdir):
        '''
        Checks that the directory path passed with "--local" is valid.
        '''
        if os.path.basename(os.path.normpath(locdir)) == self.module:
            return locdir
        elif os.path.isdir(os.path.join(locdir, self.module)):
            return os.path.join(locdir, self.module)
        else:
            print("The specified \"--local\" directory cannot be found.")
            sys.exit(5) # local directory doesn't exist

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
        with open(self.source_file, "r") as f:
            cmd = f.readline().strip()

        # Fragile. This needs improvement.
        getter = cmd.split()[0]
        if getter == "wget":
            self.source_target = "-P" + self.sources_dir
            self.needs_tarball = False
        else:
            self.source_target = self.sources_dir \
                + self.module + "-" + self.version
            self.needs_tarball = True

        cmd += " " + self.source_target
        ret = call(cmd, shell=True)
        if ret != 0:
            print("Unable to download module source.")
            sys.exit(4) # can't access source

    def make_tarball(self):
        '''
        Makes a tarball (required by `rpmbuild`) from the module source.
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
        for patch in glob.glob(os.path.join(self.module_dir, "*.patch")):
            shutil.copy(patch, self.sources_dir)

    def get_dependencies(self):
        '''
        Assembles the list of dependencies for the module. These are passed
        into the BuildRequires tag of the module spec file by `rpmbuild`.
        '''
        if not os.path.isfile(self.deps_file):
            self.dependencies = "rpm" # XXX workaround; how to specify null?
        else:
            deps = repo.read(self.deps_file)
            self.dependencies = string.join(deps, ", ")

    def build(self):
        '''
        Builds binary and source RPMS for the module.
        '''
        print("Building RPMs.")
        shutil.copy(self.spec_file, self.specs_dir)
        cmd = "rpmbuild -ba --quiet " \
            + os.path.join(self.specs_dir, os.path.basename(self.spec_file)) \
            + " --define '_prefix " + self.install_prefix + "'" \
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
        if hasattr(self, "tmpdir") and os.path.isdir(self.tmpdir): 
            shutil.rmtree(self.tmpdir)

#-----------------------------------------------------------------------------

def main():
    '''
    Accepts command-line arguments and passes them to an instance of BuildRPM.
    '''
    import argparse

    # Allow only Linuxen.
    if not sys.platform.startswith('linux'):
        print("Error: this OS is not supported.")
        sys.exit(1) # not Linux

    parser = argparse.ArgumentParser()
    parser.add_argument("module",
                        help="the name of the model or tool to build")
    parser.add_argument("--tag",
                        help="build TAG version of the module [head]")
    parser.add_argument("--local",
                        help="use LOCAL path to the module files")
    parser.add_argument("--prefix",
                        help="use PREFIX as install path for RPM [/usr/local]")
    args = parser.parse_args()

    BuildRPM(args.module, args.tag, args.local, args.prefix)

if __name__ == "__main__":
    main()
