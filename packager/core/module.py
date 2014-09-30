#! /usr/bin/env python
#
# Represents a CSDMS model or tool, with methods to get its source and
# list its dependencies.
#
# Mark Piper (mark.piper@colorado.edu)

import sys, os, shutil
from subprocess import call
import tempfile
import string
from packager.core import repo_tools as repo

class Module(object):
    '''
    Represents a CSDMS model or tool.
    '''
    def __init__(self, module_name, module_version, local_dir):
        self._name = module_name
        self._version = "head" if module_version == None else module_version

        # Get module setup files 1) from GitHub and store in a tmp directory,
        # or 2) from a local directory.
        if local_dir == None:
            self.tmpdir = tempfile.mkdtemp()
            self._location = repo.get_module(self._name, dest=self.tmpdir)
        else:
            self._location = self.get_local_dir(local_dir)
        if self._location == None:
            print("The module '" + self._name + "' cannot be located.")
            self.cleanup()
            sys.exit(1) # can't find module

        # Paths to module setup files.
        self.deps_file = os.path.join(self._location, "dependencies.txt")
        self.source_file = os.path.join(self._location, "source.txt")

        # Get module dependencies.
        self.get_dependencies()

    @property
    def name(self):
        '''
        The name of the model or tool.
        '''
        return self._name

    @property
    def version(self):
        '''
        The tagged version of the model or tool.
        '''
        return self._version

    @property
    def location(self):
        '''
        The directory holding the module setup files.
        '''
        return self._location

    @property
    def dependencies(self):
        '''
        A list of dependencies for the module.
        '''
        return self._dependencies

    def get_local_dir(self, locdir):
        '''
        Checks that the directory path passed with "--local" is valid.
        Returns the directory path, or None if invalid.
        '''
        explocdir = os.path.expanduser(locdir)
        explocdir = os.path.expandvars(explocdir)
        explocdir = os.path.normpath(explocdir)
        if os.path.basename(explocdir) == self._name:
            return explocdir
        elif os.path.isdir(os.path.join(explocdir, self._name)):
            return os.path.join(explocdir, self._name)
        else:
            print("The specified \"--local\" directory cannot be found.")

    def get_dependencies(self):
        '''
        Assembles the list of dependencies for the module.
        '''
        if os.path.isfile(self.deps_file):
            deps = repo.read(self.deps_file)
            self._dependencies = string.join(deps, ", ")
        else:
            self._dependencies = "rpm" # XXX workaround

    def get_source(self, debug=False):
        '''
        Retrieves the module source from an external repository, and, if
        needed, makes a tarball from the source. The path to the tarball
        is returned. If the tarball is already present, immediately return
        the path to the tarball.
        '''
        if self.is_tarball_present():
            print("Source tarball for " + self._name + " is present.")
            return self.tarball
        
        print("Getting " + self._name + " source.")
        with open(self.source_file, "r") as f:
            cmd = f.readline().strip()
        
        # Fragile. This needs improvement.
        getter = cmd.split()[0]
        if getter == "wget":
            self.source_target = "-N -O" + self.tarball
        else:
            self.source_target = \
                os.path.join(self._location, self._name + "-" + self._version)

        cmd += " " + self.source_target
        if debug: print(cmd)
        ret = call(cmd, shell=True)
        if ret != 0:
            print("Unable to download module source.")
            sys.exit(2) # can't access source

        if os.path.isdir(self.source_target):
            self.make_tarball()

        if debug: print(self.tarball)
        return self.tarball

    def is_tarball_present(self):
        '''
        Returns True if the source tarball is present.
        '''
        self.tarball = os.path.join( \
            self._location, self._name + "-" + self._version + ".tar.gz")
        return os.path.isfile(self.tarball)

    def make_tarball(self):
        '''
        Makes a tarball from the module source.
        '''
        print("Making tarball.")
        self.tarball = shutil.make_archive(self.source_target, 'gztar', \
                                           self._location, \
                                           os.path.basename(self.source_target))
        shutil.rmtree(self.source_target)

    def cleanup(self):
        '''
        Deletes the directory used to store the downloaded archives from
        the rpm_models and rpm_tools repos.
        '''
        if hasattr(self, "tmpdir") and os.path.isdir(self.tmpdir): 
            shutil.rmtree(self.tmpdir)
