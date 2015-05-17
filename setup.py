from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import hosts 

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt', 'CHANGES.txt')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='hosts',
    version=hosts.__version__,
    url='http://github.com/jonhadfield/hosts/',
    license='MIT',
    author='Jon Hadfield',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={'test': PyTest},
    author_email='jon.hadfield@lessknown.co.uk',
    description='Manage a hosts file',
    long_description=long_description,
    packages=['hosts'],
    include_package_data=True,
    platforms='any',
    test_suite='hosts.tests',
    classifiers = [
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
    extras_require={
        'testing': ['pytest'],
    }
)
