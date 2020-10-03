#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand
version = "1.0.1"

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a {0} -m 'version {1}'".format(version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.md').read()

requirements = []


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.version_info[0] == 2:
    importlib = "importlib"

setup(
    name='python-hosts',
    version=version,
    author='Jon Hadfield',
    author_email='jon@lessknown.co.uk',
    url='https://github.com/jonhadfield/python-hosts',
    download_url='https://github.com/jonhadfield/python-hosts/tarball/{0}'.format(version),
    description='A hosts file manager library written in python',
    long_description='A hosts file manager library written in python',
    packages=['python_hosts'],
    install_requires=['win_inet_pton'],
    platforms='any',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Operating System',
        'Topic :: System :: Networking',
    ],
    keywords=(
        'hosts, python, network'
    ),
    cmdclass={'test': PyTest},
    tests_require=['pytest',
                   'pytest-cov',
                   'PyYAML']
)
