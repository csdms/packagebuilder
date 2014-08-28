from distutils.core import setup

setup(
    name='packagebuilder',
    version='0.1.0',
    author='Mark Piper',
    author_email='mark.piper@colorado.edu',
    packages=['packager', 'packager.rpm', 'packager.deb', 'packager.core'],
    scripts=[],
    url='http://csdms.colorado.edu',
    license='LICENSE',
    description='Tools for building rpm and deb packages for CSDMS software',
    long_description=open('README.md').read(),
    install_requires=[],
)
