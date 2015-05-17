import sys
import pytest
from os import path
sys.path.append( path.dirname(path.dirname( path.abspath(__file__))))
from hosts.hosts import Hosts, HostsEntry


def test_add_single_ipv4_host(tmpdir):
    """
    Test the addition of an ipv4 host succeeds
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost")
    print hosts_file.strpath
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='123.123.123.123', names=['test.example.com'])
    hosts.add(entry=new_entry, force=False)
    assert hosts.count(new_entry).get('address_matches') == 1

def test_replacement_of_ipv4_entry_where_address_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.133', names=['example.com', 'example'])
    hosts_entries.add(entry=new_entry, force=True)
    counts = hosts_entries.count(new_entry)
    assert counts.get('address_matches') == 1

def test_replace_ipv4_host_where_name_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the name differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['example2.com', 'example'])
    hosts_entries.add(entry=new_entry, force=True)
    counts = hosts_entries.count(new_entry)
    assert counts.get('address_matches') == 1 and counts.get('name_matches') == 1

def test_add_single_ipv6_host(tmpdir):
    """
    Test addition of an ipv6 entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv6', address='::1', names=['localhost6.localdomain6', 'localhost6'])
    hosts_entries.add(entry=new_entry, force=False)
    assert hosts_entries.count(new_entry).get('address_matches') == 1

def test_add_single_comment(tmpdir):
    """
    Test addition of a comment
    """
    comment = 'this is a comment'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='comment', comment=comment)
    hosts_entries.add(entry=new_entry, force=False, )
    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 1

def test_remove_single_comment(tmpdir):
    """
    Test removal of a single comment
    """
    comment1 = "#127.0.0.1\tlocalhost"
    comment2 = "# a second comment"
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(comment1)
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='comment', comment=comment2)
    hosts_entries.add(new_entry)
    assert hosts_entries.count(new_entry).get('comment_matches') == 1
    hosts_entries.remove(new_entry)
    assert hosts_entries.count(new_entry).get('comment_matches') == 0
