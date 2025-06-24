python-hosts
========
[![codecov](https://codecov.io/gh/jonhadfield/python-hosts/branch/devel/graph/badge.svg)](https://codecov.io/gh/jonhadfield/python-hosts) [![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](http://python-hosts.readthedocs.org/en/latest/)


`python-hosts` is a small Python library for reading and writing hosts files.
It provides a simple API for adding or removing entries as well as importing
records from another file or a remote URL.  The package has no heavy
dependencies and works on Linux, macOS and Windows.

It remains compatible with Python 2.7 in addition to modern Python 3 releases.

Features
--------
* Add, remove or merge host entries programmatically.
* Import entries from a plain text file or from a URL.
* Works across platforms by automatically selecting the correct hosts file
  location.
* Python 2.7 and Python 3.5+ support.

Documentation
-------------
The docs are hosted on RTD (Read The Docs) here:  
<http://python-hosts.readthedocs.org/en/latest/index.html>.

Changelog available [here](CHANGELOG.md).

Installation
------------
pip install python-hosts

Example usage
-------------
Adding an entry to a hosts file

    from python_hosts import Hosts, HostsEntry
    hosts = Hosts(path='hosts_test')
    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['www.example.com', 'example'])
    hosts.add([new_entry])
    hosts.write()

Importing a list of host entries by URL

    from python_hosts import Hosts
    hosts = Hosts(path='hosts_test')
    hosts.import_url(url='https://gist.githubusercontent.com/jonhadfield/5b6cdf853ef629f9b187345d89157280/raw/ddfa4a069fb12bf3c1f285249d44922aeb75db3f/hosts')
    hosts.write()

Importing entries from another file

    from python_hosts import Hosts
    hosts = Hosts(path='hosts_test')
    hosts.import_file(import_file_path='other_hosts')
    hosts.write()

CLI
---
A command line client using python-hosts can be found here: https://github.com/jonhadfield/hostman


Requirements
------------

Tested on Python 2.7 and Python 3.5+, including PyPy variants

Running tests
-------------
Install the development requirements and run::

    pip install -r test-requirements.txt
    pytest



License
-------

MIT
