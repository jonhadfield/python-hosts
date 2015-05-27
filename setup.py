#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = "0.1.72"

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = []

long_description = readme + '\n\n' + history

if sys.argv[-1] == 'readme':
    print(long_description)
    sys.exit()

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

setup(
    name='hosts',
    version=version,
    url='http://github.com/jonhadfield/hosts/',
    author='Jon Hadfield',
    author_email='jon.hadfield@lessknown.co.uk',
    install_requires=[],
    description='Manage a hosts file',
    long_description=long_description,
    packages=[
        'hosts',
    ],
    package_dir={'hosts': 'hosts'},
    include_package_data=True,
    platforms='any',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Environment :: console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Operating System',
        'Topic :: System :: Networking',
    ],
    keywords=(
        'hosts, Python, network'
    ),
    cmdclass = {'test': PyTest},
    test_suite='tests',
    tests_require=['pytest']
)
