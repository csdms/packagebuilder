#! /usr/bin/env python
#
# Builds binary and source RPMs for a CSDMS model or tool.
#
# Create the executable script `build_rpm` with:
#   $ cd path/to/packagebuilder
#   $ sudo python setup.py install
#
# Examples:
#   $ build_rpm --help
#   $ build_rpm --version
#   $ build_rpm hydrotrend
#   $ build_rpm babel --tag 1.4.0
#   $ build_rpm cem --tag 0.2 --quiet
#   $ build_rpm hydrotrend --local $HOME/rpm_models
#   $ build_rpm babel --prefix /usr/local/csdms
#
# Mark Piper (mark.piper@colorado.edu)

import sys, os, shutil
from subprocess import call
import glob
import shlex
from packager.core.module import Module
from packager.core.flavor import debian_check

class BuildRPM(object):
    '''
    Uses `rpmbuild` to build a CSDMS model or tool into an RPM.
    '''
    def __init__(self, name, version, local_dir, prefix, quiet):
        self.is_debian = debian_check()
        self.is_quiet = " --quiet " if quiet else " "
        self.install_prefix = "/usr/local" if prefix is None else prefix

        # Get the model or tool and its spec file.
        self.module = Module(name, version, local_dir)
        self.spec_file = os.path.join(self.module.location, \
                                          self.module.name + ".spec")

        # Set up the local rpmbuild directory.
        self.rpmbuild = os.path.join(os.getenv("HOME"), "rpmbuild", "")
        self.prep_directory()

        # Download the module's source code and make a tarball.
        self.tarball = self.module.get_source()

        # Copy module files to the rpmbuild directory.
        self.prep_files()

        # Build the binary and source RPMs.
        self.build()
        self.cleanup()
        print("Success!")

    def prep_directory(self):
        '''
        Prepares the RPM build directory `~/rpmbuild`. Sets up member
        variables for paths in the build directory.
        '''
        print("Setting up rpmbuild directory structure.")
        if os.path.isdir(self.rpmbuild):
            shutil.rmtree(self.rpmbuild)
        subdirectories = ["BUILD","BUILDROOT","RPMS","SOURCES","SPECS","SRPMS"]
        for dname in subdirectories:
            os.makedirs(os.path.join(self.rpmbuild, dname))
        self.sources_dir = os.path.join(self.rpmbuild,  "SOURCES", "")
        self.specs_dir = os.path.join(self.rpmbuild,  "SPECS", "")

    def prep_files(self):
        '''
        Copies source tarball, spec file, patches (if any) and scripts
        (if any) for the build process.  Patches must use the extension 
        ".patch", scripts must use the extension ".sh" or ".py".
        '''
        print("Copying module files.")
        shutil.copy(self.spec_file, self.specs_dir)
        shutil.copy(self.tarball, self.sources_dir)
        for patch in glob.glob(os.path.join(self.module.location, "*.patch")):
            shutil.copy(patch, self.sources_dir)
        for script in glob.glob(os.path.join(self.module.location, "*.sh")):
            shutil.copy(script, self.sources_dir)
        for script in glob.glob(os.path.join(self.module.location, "*.py")):
            shutil.copy(script, self.sources_dir)

    def build(self):
        '''
        Builds binary and source RPMS for the module.
        '''
        print("Building RPMs.")
        cmd = "rpmbuild -ba" + self.is_quiet \
            + os.path.join(self.specs_dir, os.path.basename(self.spec_file)) \
            + " --define '_prefix " + self.install_prefix + "'" \
            + " --define '_version " + self.module.version + "'"
        if not self.is_debian:
            cmd += " --define '_buildrequires " + self.module.dependencies + "'"
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
        self.module.cleanup()

#-----------------------------------------------------------------------------

def main():
    '''
    Accepts command-line arguments and passes them to an instance of BuildRPM.
    '''
    import argparse
    from packager import __version__

    # Allow only Linuxen.
    if not sys.platform.startswith('linux'):
        print("Error: this OS is not supported.")
        sys.exit(1) # not Linux

    parser = argparse.ArgumentParser(
        description="Builds a CSDMS model or tool into an RPM.")
    parser.add_argument("module_name",
                        help="the name of the model or tool to build")
    parser.add_argument("--local",
                        help="use LOCAL path to the module files")
    parser.add_argument("--prefix",
                        help="use PREFIX as install path for RPM [/usr/local]")
    parser.add_argument("--tag",
                        help="build TAG version of the module [head]")
    parser.add_argument("--quiet", action="store_true",
                        help="provide less detailed output [verbose]")
    parser.add_argument('--version', action='version', 
                        version='build_rpm ' + __version__)
    args = parser.parse_args()

    BuildRPM(args.module_name, args.tag, args.local, args.prefix, args.quiet)

if __name__ == "__main__":
    main()
