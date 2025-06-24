python-hosts
========
[![codecov](https://codecov.io/gh/jonhadfield/python-hosts/branch/devel/graph/badge.svg)](https://codecov.io/gh/jonhadfield/python-hosts) [![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](http://python-hosts.readthedocs.org/en/latest/)


This is a python library for managing a hosts file.
It enables you to add and remove entries, import them from a file or URL and
query existing entries. Utility functions have been streamlined for easier
maintenance.
It remains compatible with Python 2.7 as well as modern Python 3 releases.

Documentation
-------------
The docs are hosted on RTD (Read The Docs) here:  
<http://python-hosts.readthedocs.org/en/latest/index.html>.

Changelog available [here](CHANGELOG.md).

Installation
------------
pip install python-hosts

Example usage
------------
Create a ``Hosts`` instance and add an entry::

    from python_hosts import Hosts, HostsEntry
    hosts = Hosts(path='hosts_test')
    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['www.example.com', 'example'])
    hosts.add([new_entry])
    hosts.write()

Import entries from a URL or file::

    hosts.import_url('https://example.com/hosts')
    hosts.import_file('extra_hosts')
    hosts.write()

Remove or query entries::

    hosts.remove_all_matching(name='example')
    hosts.exists(address='1.2.3.4')

Entries can also be merged with existing ones::

    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['alias'])
    hosts.add([new_entry], merge_names=True)

CLI
---
A command line client using python-hosts can be found here: https://github.com/jonhadfield/hostman


Requirements
------------

Tested on Python 2.7 and Python 3.5+, including PyPy variants


License
-------

MIT
