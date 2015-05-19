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

def test_hostsentry_initialisation_failure_with_invalid_type():
    """
    Test initialiser returns an exception if the type is invalid 
    """
    with pytest.raises(Exception):
        HostsEntry()
    with pytest.raises(Exception):
        HostsEntry('IPv4')
    with pytest.raises(Exception):
        HostsEntry('IP')

def test_hostsentry_initialisation_failure_with_missing_comment():
    """
    Test initialiser returns an exception if comment type
    is set by no comment is provided
    """
    with pytest.raises(Exception):
        HostsEntry(entry_type='comment')
    with pytest.raises(Exception):
        HostsEntry(entry_type='comment', address='1.2.3.4')

def test_hostsentry_initialisation_failure_with_missing_name_or_address():
    """
    Test initialiser returns an exception if type is ipv4|ipv6
    but address or names (or both) are missing
    """
    with pytest.raises(Exception):
        HostsEntry(entry_type='ipv4')
    with pytest.raises(Exception):
        HostsEntry(entry_type='ipv4', address='1.2.3.4')
    with pytest.raises(Exception):
        HostsEntry(entry_type='ipv4', names=['example.com'])
    with pytest.raises(Exception):
        HostsEntry(entry_type='ipv6', address='fe80::1%lo0')
    with pytest.raises(Exception):
        HostsEntry(entry_type='ipv6', names=['example.com'])

def test_line_break_identified_as_blank(tmpdir):
    new_line = "\n"
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(new_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.entries[0].entry_type == 'blank'

