# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hosts')))
from hosts import Hosts


def test_import_from_url(tmpdir):
    """
    Test that correct 'success, fail, skip' counters are returned
    when there is at least a single successful imported host entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "http://winhelp2002.mvps.org/hosts.txt"
    result = hosts.import_url(url=import_url)
    assert result and int(result.get('ipv4_count')) > 1
