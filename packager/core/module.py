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
            self._module_dir = repo.get_module(self._name, dest=self.tmpdir)
        else:
            self._module_dir = self.get_local_dir(local_dir)
        if self._module_dir == None:
            print("The module '" + self._name + "' cannot be located.")
            sys.exit(1) # can't find module

        # Model setup files.
        self.deps_file = os.path.join(self._module_dir, "dependencies.txt")
        self.source_file = os.path.join(self._module_dir, "source.txt")

        self._dependencies = None
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
    def module_dir(self):
        '''
        The directory holding the module setup files.
        '''
        return self._module_dir

    @property
    def dependencies(self):
        '''
        A list of dependencies for the module.
        '''
        return self._dependencies

    def get_local_dir(self, locdir):
        '''
        Checks that the directory path passed with "--local" is valid.
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
            sys.exit(2) # local directory doesn't exist

    def get_dependencies(self):
        '''
        Assembles the list of dependencies for the module.
        '''
        if not os.path.isfile(self.deps_file):
            self._dependencies = "rpm" # XXX workaround; how to specify null?
        else:
            deps = repo.read(self.deps_file)
            self._dependencies = string.join(deps, ", ")

    def get_source(self, target_dir):
        '''
        Retrieves the module source from an external repository.
        '''
        print("Getting " + self._name + " source.")
        with open(self.source_file, "r") as f:
            cmd = f.readline().strip()

        self.target_dir = target_dir

        # Fragile. This needs improvement.
        getter = cmd.split()[0]
        if getter == "wget":
            self.source_target = "-P" + self.target_dir
            self.needs_tarball = False
        else:
            self.source_target = self.target_dir \
                + self._name + "-" + self._version
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
        shutil.make_archive(self.source_target, 'gztar', self.target_dir, \
                            os.path.basename(self.source_target))
        shutil.rmtree(self.source_target)

    def cleanup(self):
        '''
        Deletes the directory used to store the downloaded archives from
        the rpm_models and rpm_tools repos.
        '''
        if hasattr(self, "tmpdir") and os.path.isdir(self.tmpdir): 
            shutil.rmtree(self.tmpdir)
