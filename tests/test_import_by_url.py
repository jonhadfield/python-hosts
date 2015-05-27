# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hosts')))
import pytest
from hosts import Hosts, HostsEntry, exception


def test_import_from_url(tmpdir):
    """
    Test that correct 'success, fail, skip' counters are returned
    when there is at least a single successful imported host entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    print "START"
    for host in hosts.entries:
        print "TYPE: {} ADDRESS: {} NAMES: {} COMMENT: {}".format(host.entry_type, host.address, host.names, host.comment)
    print "END"
    import_url = "http://winhelp2002.mvps.org/hosts.txt"
    message = hosts.import_url(url=import_url, hosts_path=hosts_file.strpath)
    assert 'Added: 23' in message.get('message')

