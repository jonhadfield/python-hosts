# -*- coding: utf-8 -*-
import datetime
import os
import pwd
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from python_hosts.hosts import Hosts, HostsEntry
from python_hosts import exception


def test_import_from_url_without_force(tmpdir):
    """
    Test that a bare import from URL does not replace names in existing entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("1.2.3.4\texample1.com example2.com example3.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts_win3"
    hosts.import_url(url=import_url)
    assert hosts.exists(names=['example3.com'])


def test_import_from_url_with_force(tmpdir):
    """
    Test that a bare import from URL does replace names in existing entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("1.2.3.4\texample1.com example2.com example3.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts_win3"
    hosts.import_url(url=import_url, force=True)
    assert not hosts.exists(names=['example3.com'])


def test_remove_existing_entry_using_name_only(tmpdir):
    """
    Test removal of an existing entry using name only
    """
    entries = '1.2.3.4 example.com example\n# this is a comment\n\n3.4.5.6 random.com' # two newlines intentionally follow, see issue  #11
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(entries)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.exists(address='1.2.3.4')
    assert hosts_entries.exists(names=['example.com'])
    hosts_entries.remove_all_matching(name='example.com')
    assert not hosts_entries.exists(names=['example.com'])
    hosts_entries.write()
    assert '# this is a comment\n' in open(hosts_file.strpath).read()
    assert '3.4.5.6\trandom.com' in open(hosts_file.strpath).read()


def test_remove_existing_entry_using_address_only(tmpdir):
    """
    Test removal of an existing entry using ip4 address only
    """
    entries = '1.2.3.4 example.com example\n# this is a comment'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(entries)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.exists(address='1.2.3.4')
    assert hosts_entries.exists(names=['example.com'])
    hosts_entries.remove_all_matching(address='1.2.3.4')
    assert not hosts_entries.exists(address='1.2.3.4')


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def test_hosts_str(tmpdir):
    """ Test that the str method returns an accurate, user readable output
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    assert (str(hosts)) == "hosts_path={0}, TYPE=ipv4, ADDR=6.6.6.6, NAMES=example.com".format(hosts_file.strpath)


def test_hosts_write_to_custom_path(tmpdir):
    """ Test that the hosts file can be written to a different path to the one it was read from
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    alternate_hosts_file = tmpdir.mkdir("tmp").join("hosts2")
    hosts.write(path=alternate_hosts_file.strpath)
    alternate_hosts = Hosts(path=alternate_hosts_file.strpath)
    assert alternate_hosts.count() == 1
    assert hosts.exists(address='6.6.6.6', names=['example.com'])


def test_hosts_repr(tmpdir):
    """ Test that the repr method returns a useful representation of the hosts object
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    assert (repr(hosts)) == "Hosts(hosts_path='{0}', " \
                            "entries=[HostsEntry(entry_type='ipv4', " \
                            "address='6.6.6.6', " \
                            "comment=None, " \
                            "names=['example.com'])])".format(hosts_file.strpath)


def test_import_from_url_counters_for_part_success(tmpdir):
    """
    Test that correct counters are returned when there is at least a
    single successful imported host entry

    There will be a single entry written before import.
    Importing file will include three valid IPV4 entries and an invalid entry.
    One of the three valid import lines will include a duplicate set of names.
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts"
    result = hosts.import_url(url=import_url)
    add_result = result.get('add_result')
    write_result = result.get('write_result')
    assert add_result.get('ipv4_count') == 4
    assert write_result.get('total_written') == 5


def test_exception_raised_when_unable_to_write_hosts(tmpdir):
    """ Test that the correct exception is raised when a hosts file
    is not writeable.
    """
    if get_username() != 'root':
        hosts_file = tmpdir.mkdir("etc").join("hosts")
        hosts_file.write("127.0.0.1\tlocalhost\n")
        hosts = Hosts(path=hosts_file.strpath)
        os.chmod(hosts_file.strpath, 0o444)
        new_entry = HostsEntry(entry_type='ipv4', address='123.123.123.123', names=['test.example.com'])
        hosts.add(entries=[new_entry])
        with pytest.raises(exception.UnableToWriteHosts):
            hosts.write()


def test_write_will_create_path_if_missing():
    """
    Test that the hosts file declared when constructing a Hosts instance will
    be created if it doesn't exist
    """
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    hosts_path = '/tmp/testwrite.{0}'.format(timestamp)
    hosts = Hosts(path=hosts_path)
    entry = HostsEntry.str_to_hostentry('1.2.3.4 example.com example.org')
    hosts.add(entries=[entry])
    hosts.write()
    hosts2 = Hosts(path=hosts_path)
    os.remove(hosts_path)
    assert hosts2.exists(address='1.2.3.4')


def test_add_adblock_entry_without_force_multiple_names(tmpdir):
    """
    Test that addition of an adblock entry does not succeed if force is not set
    and there is a matching name
    """
    ipv4_line = '0.0.0.0 example2.com example3.com'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry.str_to_hostentry('0.0.0.0 example.com example3.com')
    hosts_entries.add(entries=[new_entry], force=False)
    assert hosts_entries.exists(names=['example2.com'])


def test_add_adblock_entry_with_force_single_name(tmpdir):
    """
    Test that an addition of an adblock entry replaces one with a matching name
    if force is True
    """
    ipv4_line = '0.0.0.0 example2.com example3.com'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry.str_to_hostentry('0.0.0.0 example.com example3.com')
    hosts_entries.add(entries=[new_entry], force=True)
    assert hosts_entries.exists(names=['example.com'])


def test_add_adblock_entry_with_force_with_target_having_multiple_names(tmpdir):
    """
    Test that an addition of an adblock entry replaces one with a matching name
    if force is True (multiple names)
    """
    ipv4_line = '0.0.0.0 example.com example2.com'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.exists(address='0.0.0.0')
    new_entry = HostsEntry.str_to_hostentry('0.0.0.0 example.com example2.com')
    hosts_entries.add(entries=[new_entry], force=True)
    assert hosts_entries.exists(names=['example2.com'])


def test_add_adblock_entry_without_force_with_target_having_multiple_names(tmpdir):
    """
    Test that addition of an adblock entry does not succeed if force is not set
    and there is a matching name (matching names)
    """
    ipv4_line = '0.0.0.0 example.com'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.exists(address='0.0.0.0')
    new_entry = HostsEntry.str_to_hostentry('0.0.0.0 example.com')
    hosts_entries.add(entries=[new_entry])


def test_remove_existing_ipv4_address_using_hostsentry(tmpdir):
    """
    Test removal of an existing ip4 address
    """
    ipv4_line = '1.2.3.4 example.com example'
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(ipv4_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.exists(address='1.2.3.4')
    assert hosts_entries.exists(names=['example.com'])
    hosts_entries.remove_all_matching(address='1.2.3.4', name='example.com')
    assert not hosts_entries.exists(address='1.2.3.4')
    assert not hosts_entries.exists(names=['example.com'])


def test_add_single_ipv6_host(tmpdir):
    """
    Test addition of an ipv6 entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv6', address='::1', names=['localhost6.localdomain6', 'localhost6'])
    hosts_entries.add(entries=[new_entry], force=False)
    assert hosts_entries.exists(address='::1')


def test_replace_ipv4_host_where_name_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the name differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['example2.com', 'example'])
    hosts_entries.add(entries=[new_entry], force=True)
    assert hosts_entries.exists(address='82.132.132.132')
    assert hosts_entries.exists(names=['example2.com', 'example'])


def test_add_single_ipv4_host(tmpdir):
    """
    Test the addition of an ipv4 host succeeds
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost\n")
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='123.123.123.123', names=['test.example.com'])
    hosts.add(entries=[new_entry])
    assert hosts.exists(address='123.123.123.123')


def test_import_from_url(tmpdir):
    """
    Test that correct counters values are returned
    when a text file of host entries is imported via url
    Existing host file has: 1 entry
    URL has: 24 entries with 1 duplicate

    Add should return 23 ipv4 (to add) and 1 duplicate
    Write will write new 23 plus existing 1 (23 + 1 = 24)
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n")
    hosts = Hosts(path=hosts_file.strpath)
    import_url = "https://dl.dropboxusercontent.com/u/167103/hosts_win"
    import_url_result = hosts.import_url(url=import_url)
    import_url_add_result = import_url_result.get('add_result')
    import_url_write_result = import_url_result.get('write_result')
    assert not import_url_result == 'failed'
    assert import_url_add_result.get('ipv4_count') == 24
    assert import_url_write_result.get('ipv4_entries_written') == 25
    assert import_url_write_result.get('total_written') == 25


def test_import_file_increments_invalid_counter(tmpdir):
    """
    Test that correct counters values are returned
    when a text file of host entries is imported
    Existing host file has: 1 ipv4 entry
    Import file has: 2 ipv4 entries plus 1 invalid entry

    Add should return 2
    Dedupe will find a single duplicate
    Add will return 1 as invalid
    Write will write 1 new entry plus the existing entry (1 + 1 = 2)
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    import_file = tmpdir.mkdir("input").join("infile")
    import_file.write("example\n\n10.10.10.10\thello.com\n82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    import_file_result = hosts_entries.import_file(import_file.strpath)
    assert not import_file_result.get('result') == 'failed'
    import_file_write_result = import_file_result.get('write_result')
    assert import_file_result.get('invalid_count') == 1
    assert import_file_write_result.get('ipv4_entries_written') == 2
    assert import_file_write_result.get('total_written') == 2


def test_replacement_of_ipv4_entry_where_address_differs(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    Add:
    82.132.132.132 example.com example
    Then add (with force):
    82.132.132.133 example.com example
    The second addition should replace the former as there is an address match
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.133', names=['example.com', 'example'])
    hosts_entries.add(entries=[new_entry], force=True)
    assert hosts_entries.exists(address='82.132.132.133')
    assert hosts_entries.exists(names=['example.com', 'example'])


def test_addition_of_ipv4_entry_where_matching_exists(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['something.com', 'example'])
    hosts_entries.add(entries=[new_entry], force=False)
    assert hosts_entries.exists(address='82.132.132.132')


def test_import_file_returns_duplicate_correctly(tmpdir):
    """
    Test that adding an entry that exists will return a duplicate count of 1
    and a write count of 2 (where existing 82.132.132.132 is written along with
    new 10.10.10.10 entry)
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    import_file = tmpdir.mkdir("input").join("infile")
    import_file.write("10.10.10.10\thello.com\n82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    feedback = hosts_entries.import_file(import_file_path=import_file.strpath)
    add_result = feedback.get('add_result')
    write_result = feedback.get('write_result')
    assert add_result.get('duplicate_count') == 1
    assert write_result.get('ipv4_entries_written') == 2


def test_addition_of_ipv6_entry_where_matching_name_exists_and_force_false(tmpdir):
    """
    Test no replacement of an ipv6 entry where the address is different
    but there is a matching name and force is false
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("fe80::200:f8ff:fe21:67cf\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv6', address='2001:db8:a0b:12f0::1',
                           names=['example.com', 'example'])
    hosts_entries.add(entries=[new_entry], force=False)
    assert not hosts_entries.exists(address='2001:db8:a0b:12f0::1')
    assert hosts_entries.exists(address='fe80::200:f8ff:fe21:67cf')
    assert hosts_entries.exists(names=new_entry.names)


def test_existing_ipv6_addresses_are_preserved(tmpdir):
    """
    Test that existing ipv6 addresses are preserved after adding
    an ipv4 entry
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("fe80::1\tlocalhost\n6.6.6.6\texample.com\n# A test comment\n\n")
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['something.com', 'example'])
    hosts.add(entries=[new_entry], force=False)
    write_result = hosts.write()
    assert write_result.get('ipv6_entries_written') == 1
    assert write_result.get('ipv4_entries_written') == 2
    assert write_result.get('comments_written') == 1
    assert write_result.get('blanks_written') == 1


def test_addition_of_ipv4_entry_where_matching_exists_and_force_true(tmpdir):
    """
    Test replacement of an ipv4 entry where just the address differs
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("82.132.132.132\texample.com\texample\n")
    hosts_entries = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['something.com', 'example'])
    hosts_entries.add(entries=[new_entry], force=True)
    assert hosts_entries.exists(address='82.132.132.132')
    assert hosts_entries.exists(names=['something.com', 'example'])


def test_existing_comments_and_blanks_are_preserved(tmpdir):
    """
    Test that comments and newlines/blanks that exist in the file prior to
    changes are preserved after a new entry is added
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("6.6.6.6\texample.com\n# A test comment\n\n")
    hosts = Hosts(path=hosts_file.strpath)
    new_entry = HostsEntry(entry_type='ipv4', address='82.132.132.132', names=['something.com', 'example'])
    hosts.add(entries=[new_entry], force=False)
    write_result = hosts.write()
    assert write_result.get('comments_written') == 1
    assert write_result.get('blanks_written') == 1


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


def test_no_entries_if_hosts_path_does_not_exist():
    """
    Test that no entries are returned if the hosts path is invalid
    """
    hosts = Hosts(path="invalid")
    assert hosts.count() == 0


def test_line_break_identified_as_blank(tmpdir):
    """
    Test that a new line is identified as a blank
    """
    new_line = "\n"
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write(new_line)
    hosts_entries = Hosts(path=hosts_file.strpath)
    assert hosts_entries.entries[0].entry_type == 'blank'


def test_get_entry_type():
    """
    Test that the correct entry type is returned for an ipv6 address
    """
    assert HostsEntry.get_entry_type('# This is a comment') == 'comment'
    assert HostsEntry.get_entry_type('\n') == 'blank'
    assert HostsEntry.get_entry_type('1.2.3.4 example.com example') == 'ipv4'
    assert HostsEntry.get_entry_type('2001:0db8:85a3:0042:1000:8a2e:0370:7334 example.com example') == 'ipv6'
    assert not HostsEntry.get_entry_type('example.com example 1.2.3.4')


def test_windows_platform_detection():
    """
    Test that specifying platform 'windows' returns the default windows
    path to the hosts file
    """
    assert Hosts.determine_hosts_path(platform='windows') == r'c:\windows\system32\drivers\etc\hosts'


def test_osx_platform_detection():
    """
    Test that specifying platform 'darwin' returns the default OSX
    path to the hosts file
    """
    assert Hosts.determine_hosts_path(platform='darwin') == '/etc/hosts'


def test_linux_platform_detection():
    """
    Test that specifying platform 'linux' returns the default linux
    path to the hosts file
    """
    assert Hosts.determine_hosts_path(platform='linux') == '/etc/hosts'


def test_read_hosts_with_platform_detection():
    """
    Test that an instance of Hosts is returned using detection and initialiser
    """
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


def test_remove_all_matching_multiple(tmpdir):
    """ 
    Test removal of multiple entries with a common alias
    """
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("1.2.3.4\tfoo-1 foo\n"
                     "2.3.4.5\tfoo-2 foo\n")
    hosts = Hosts(path=hosts_file.strpath)
    hosts.remove_all_matching(name="foo")
    hosts.write()
    assert not hosts_file.read()


def test_remove_all_matching_failure(tmpdir):
    """
    Test removal of multiple entries with a common alias
    """
    with pytest.raises(ValueError):
        hosts_file = tmpdir.mkdir("etc").join("hosts")
        hosts_file.write("1.2.3.4\tfoo-1 foo\n"
                         "2.3.4.5\tfoo-2 foo\n")
        hosts = Hosts(path=hosts_file.strpath)
        hosts.remove_all_matching()
        hosts.write()
