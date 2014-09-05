from ez_setup import use_setuptools # https://pypi.python.org/pypi/setuptools
use_setuptools()
from setuptools import setup, find_packages

# Get the long description from the README file.
def get_long_description():
    from codecs import open
    from os import path

    here = path.abspath(path.dirname(__file__))
    try:
        with open(path.join(here, 'README.md'), encoding='utf-8') as f:
            long_description = f.read()
    except:
        return []
    else:
        return long_description

setup(
    name='packagebuilder',
    version='0.1.0',
    description='Tools for building rpm and deb packages for CSDMS software',
    long_description=get_long_description(),
    url='https://github.com/csdms/packagebuilder',
    author='Mark Piper',
    author_email='mark.piper@colorado.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        ],
    keywords='CSDMS, earth system modeling, packaging, Linux, rpm, deb',
    packages=find_packages(),
    install_requires=['nose'],
    package_data={
        'packager.data': ['repositories.txt'],
        },
    entry_points={
        'console_scripts': [
            'build_rpm=packager.rpm.build:main',
            ],
        },
    )
