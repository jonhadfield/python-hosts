import sys
import pytest
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from hosts.hosts import HostsEntry


def test_create_ipv4_instance():
    ''' add an ipv4 type entry '''
    hosts_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['example.com', 'example'])
    assert hosts_entry.entry_type == 'ipv4'
    assert hosts_entry.address == '1.2.3.4'
    assert hosts_entry.names == ['example.com', 'example']