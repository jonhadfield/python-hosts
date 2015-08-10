python-hosts
========
[![Build Status](https://api.travis-ci.org/jonhadfield/python-hosts.svg?branch=devel)](https://travis-ci.org/jonhadfield/python-hosts)

This is a python library for managing a hosts file. 
It enables you to add and remove entries, or import them from a file or URL.

Documentation
-------------
The docs are hosted on RTD (Read The Docs) here:  
<http://python-hosts.readthedocs.org/en/latest/index.html>.

Installation
------------
pip install python-hosts

Example usage
------------
Adding an entry to a hosts file

    from python_hosts import Hosts, HostsEntry
    hosts = Hosts(path='hosts_test')
    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['www.example.com', 'example'])
    hosts.add([new_entry])
    hosts.write()

Importing a list of host entries by URL

    from python_hosts import Hosts, HostsEntry
    hosts = Hosts(path='hosts_test')
    hosts.import_url(url='https://dl.dropboxusercontent.com/u/167103/hosts')
    hosts.write()

Requirements
------------

Tested on python 2.6, 2.7 and 3.4


License
-------

MIT
