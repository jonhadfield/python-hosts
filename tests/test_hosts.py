# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hosts')))
import pytest
from hosts import Hosts, HostsEntry, exception


def test_import_file_increments_failure_counter(tmpdir):
    """
    Test that the addition an invalid entry will reflect in failures count
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    import_file = tmpdir.mkdir("input").join("infile")
    import_file.write("example\n\n10.10.10.10\thello.com\n82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    feedback = hosts_entries.import_file(import_file.strpath)
    assert 'Failed: 1' in feedback.get('message')


def test_add_single_ipv4_host_by_detection(tmpdir):
    """
    Test the addition of an ipv4 host succeeds
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost\n")
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = '3.4.5.6 bob jane.com'
    hosts.add(entry=new_entry, force=False)
    assert hosts.count(new_entry).get('address_matches') == 1


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
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts_win"
    message = hosts.import_url(url=import_url)
    assert 'Added: 23' in message.get('message')


def test_add_single_ipv4_host(tmpdir):
    """
    Test the addition of an ipv4 host succeeds
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost\n")
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='123.123.123.123', names=['test.example.com'])
    hosts.add(entry=new_entry, force=False)
    assert hosts.count(new_entry).get('address_matches') == 1


def test_replacement_of_ipv4_entry_where_address_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.133', names=['example.com', 'example'])
    hosts_entries.add(entry=new_entry, force=True)
    counts = hosts_entries.count(new_entry)
    assert counts.get('address_matches') == 1


def test_addition_of_ipv4_entry_where_matching_exists(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['something.com', 'example'])
    hosts_entries.add(entry=new_entry, force=False)
    counts = hosts_entries.count(new_entry)
    assert counts.get('address_matches') == 1


def test_replace_ipv4_host_where_name_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the name differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
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
    hosts_file.write("127.0.0.1\tlocalhost\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv6', address='::1', names=['localhost6.localdomain6', 'localhost6'])
    hosts_entries.add(entry=new_entry, force=False)
    assert hosts_entries.count(new_entry).get('address_matches') == 1


#def test_add_single_comment(tmpdir):
#    """
#    Test addition of a comment
#    """
#    comment = 'this is a comment'
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write("\n")
#    hosts_entries = Hosts(path=hosts_file.strpath)
#    new_entry = HostsEntry(entry_type='comment', comment=comment)
#    hosts_entries.add(entry=new_entry, force=False)
#    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 1


#def test_add_a_comment_that_already_exists(tmpdir):
#    """
#    Test addition of a comment
#    """
#    comment = '#this is a comment\n'
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write('#this is a comment\n')
#    hosts_entries = Hosts(path=hosts_file.strpath)
#    new_entry = HostsEntry(entry_type='comment', comment=comment)
#    hosts_entries.add(entry=new_entry, force=False)
#    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 1


#def test_add_empty_line(tmpdir):
#    """
#    Test addition of an empty line (blank)
#    """
#    comment = 'this is a comment'
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write("\n")
#    hosts_entries = Hosts(path=hosts_file.strpath)
#    new_entry = HostsEntry(entry_type='comment', comment=comment)
#    hosts_entries.add(entry=new_entry, force=False, )
#    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 1


#def test_remove_single_comment(tmpdir):
#    """
#    Test removal of a single comment
#    """
#    comment1 = "#127.0.0.1\tlocalhost\n"
##    comment2 = "# a second comment\n"
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write(comment1)
#    hosts_entries = Hosts(path=hosts_file.strpath)
#    new_entry = HostsEntry(entry_type='comment', comment=comment2)
#    hosts_entries.add(entry=new_entry)
#    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 1
#    hosts_entries.remove(entry=new_entry)
#    assert hosts_entries.count(entry=new_entry).get('comment_matches') == 0


def test_remove_existing_ipv4_address_using_hostsentry(tmpdir):
    """
    Test removal of an existing ip4 address
    """
    ipv4_line = '1.2.3.4 example.com example'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['example.com'])
    assert hosts_entries.count(entry).get('address_matches') == 1
    hosts_entries.remove(entry)
    assert hosts_entries.count(entry).get('address_matches') == 0


def test_remove_existing_ipv4_address_using_strings(tmpdir):
    """
    Test removal of an existing ip4 address
    """
    ipv4_line = '1.2.3.4 example.com example'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['example.com'])
    assert hosts_entries.count(entry).get('address_matches') == 1
    hosts_entries.remove(address='1.2.3.4', names='example.com')
    assert hosts_entries.count(entry).get('address_matches') == 0


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


def test_hostsentry_initialisation_failure_with_invalid_address():
    """
    Test initialiser returns an exception if type is ipv4|ipv6
    but address or names (or both) are missing
    """
    with pytest.raises(exception.InvalidIPv4Address):
        HostsEntry(entry_type='ipv4', address='255.255.255.256', names=['example.com', 'example'])
    with pytest.raises(exception.InvalidIPv6Address):
        HostsEntry(entry_type='ipv6', address='2001::1::3F', names=['example.com', 'example'])


def test_io_exception_if_hosts_path_does_not_exist():
    with pytest.raises(IOError):
        Hosts(path="invalid")


def test_line_break_identified_as_blank(tmpdir):
    new_line = "\n"
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(new_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.entries[0].entry_type == 'blank'


def test_get_entry_type():
    assert HostsEntry.get_entry_type('# This is a comment') == 'comment'
    assert HostsEntry.get_entry_type('\n') == 'blank'
    assert HostsEntry.get_entry_type('1.2.3.4 example.com example') == 'ipv4'
    assert HostsEntry.get_entry_type('2001:0db8:85a3:0042:1000:8a2e:0370:7334 example.com example') == 'ipv6'
    assert not HostsEntry.get_entry_type('example.com example 1.2.3.4')


def test_windows_platform_detection():
    assert Hosts.determine_hosts_path(platform='windows') == r'c:\windows\system32\drivers\etc\hosts'


def test_osx_platform_detection():
    assert Hosts.determine_hosts_path(platform='darwin') == '/etc/hosts'


def test_linux_platform_detection():
    assert Hosts.determine_hosts_path(platform='linux') == '/etc/hosts'


def test_default_platform_detection():
    assert Hosts.determine_hosts_path() == '/etc/hosts'


def test_read_hosts_with_platform_detection():
    test_hosts = Hosts()
    assert isinstance(test_hosts, Hosts)


def test_file_import_fails_when_not_readable(tmpdir):
    """
    Test import fails if file to import is not readable
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample")
    hosts_entries = Hosts(path=hosts_file.strpath)
    result = hosts_entries.import_file('/invalid_file')
    assert result.get('result') == 'failed'


#def test_import_file_continues_on_empty_line(tmpdir):
#    """
#    Test an entry after an empty line is added successfully
#    """
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write("82.132.132.132\texample.com\texample\n")
#    import_file = tmpdir.mkdir("input").join("infile")
#    import_file.write("\n10.10.10.10\thello.com")
#    hosts_entries = Hosts(path=hosts_file.strpath)
#    feedback = hosts_entries.import_file(import_file_path=import_file.strpath)
#    assert feedback.get('result') == 'success'


def test_import_file_returns_unchanged_correctly(tmpdir):
    """
    Test that adding an entry that exists will return an unchanged number
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    import_file = tmpdir.mkdir("input").join("infile")
    import_file.write("10.10.10.10\thello.com\n82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    feedback = hosts_entries.import_file(import_file_path=import_file.strpath)
    assert 'Unchanged: 1' in feedback.get('message')


def test_import_returns_failure_if_no_successes(tmpdir):
    """
    Test that a failure is returned if no entries can be imported
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    import_file = tmpdir.mkdir("input").join("infile")
    import_file.write("hello mum")
    hosts_entries = Hosts(path=hosts_file.strpath)
    feedback = hosts_entries.import_file(import_file.strpath)
    assert 'failed' in feedback.get('result')


#def test_import_from_url(tmpdir):
#    """
#    Test that a simple import by URL succeeds
#    """
#    hosts_file = tmpdir.mkdir("etc").join("hosts")
#    hosts_file.write("127.0.0.1\tlocalhost\n")
#    hosts = Hosts(path=hosts_file.strpath)
#    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts"
#    hosts.import_url(url=import_url)
#    hosts = Hosts(path=hosts_file.strpath)
#    assert hosts.count('66.66.66.66 example.com example').get('name_matches') == 1


def test_import_from_url_counters_for_part_success(tmpdir):
    """
    Test that correct 'success, fail, skip' counters are returned
    when there is at least a single successful imported host entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts"
    message = hosts.import_url(url=import_url)
    assert 'Added: 1' in message.get('message')
    assert 'Failed: 1' in message.get('message')
    assert 'Unchanged: 1' in message.get('message')


def test_import_from_url_counters_for_no_successes(tmpdir):
    """
    Test that correct 'success, fail, skip' counters are returned
    when there isn't a single successful imported host entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts_invalid"
    message = hosts.import_url(url=import_url)
    assert message.get('result') == 'failed'
    assert 'Failed: 2' in message.get('message')
    assert 'Unchanged: 1' in message.get('message')



