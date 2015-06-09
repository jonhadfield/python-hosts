# -*- coding: utf-8 -*-
"""
This package contains all of the modules utilised
by the python-hosts library.
hosts: Contains the Hosts and HostsEntry classes that represent instances
 of a hosts file and it's individual lines/entries
utils: Contains helper functions to check the available operations on a hosts
 file and the validity of a hosts file entry
exception: Contains the custom exceptions that are raised in the event
 of an error in processing a hosts file and its entries
"""
from .hosts import Hosts, HostsEntry
from .utils import is_readable, is_ipv4, is_ipv6, is_writeable, valid_hostnames
from .exception import HostsException,\
    HostsEntryException, \
    InvalidIPv4Address, \
    InvalidIPv6Address, \
    InvalidComment
