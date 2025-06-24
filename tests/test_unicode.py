# -*- coding: utf-8 -*-
"""
Tests for Unicode support in python-hosts.

These tests verify that the library correctly handles Unicode hostnames,
comments, and file I/O in both Python 2.7 and 3.x.
"""

from __future__ import unicode_literals
import os
import sys
import tempfile

import pytest

from python_hosts.hosts import Hosts, HostsEntry
from python_hosts.unicode_utils import (ensure_text, ensure_binary, 
                                        normalize_hostname, normalize_comment,
                                        text_type, string_types)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_unicode_hostname_normalization():
    """Test that Unicode hostnames are properly normalized."""
    # Basic Unicode hostname
    hostname = 'тест.com'  # Cyrillic 'test'
    normalized = normalize_hostname(hostname)
    assert isinstance(normalized, text_type)
    
    # IDN (Internationalized Domain Name) conversion
    idn_hostname = 'пример.рф'  # Russian example.rf
    normalized_idn = normalize_hostname(idn_hostname)
    assert isinstance(normalized_idn, text_type)
    # Should be converted to ASCII-compatible encoding
    assert 'xn--' in normalized_idn


def test_unicode_comment_normalization():
    """Test that Unicode comments are properly normalized."""
    comment = 'Это комментарий'  # This is a comment in Russian
    normalized = normalize_comment(comment)
    assert isinstance(normalized, text_type)
    assert normalized == comment.strip()


def test_hostsentry_with_unicode_names(tmpdir):
    """Test creating HostsEntry with Unicode hostnames."""
    # Unicode hostname with IDN
    unicode_names = ['пример.com', 'тест.localhost']
    entry = HostsEntry(entry_type='ipv4', address='192.168.1.1', names=unicode_names)
    
    assert entry.entry_type == 'ipv4'
    assert entry.address == '192.168.1.1'
    assert len(entry.names) == 2
    assert all(isinstance(name, text_type) for name in entry.names)


def test_hostsentry_with_unicode_comment(tmpdir):
    """Test creating HostsEntry with Unicode comment."""
    unicode_comment = 'Тестовый комментарий'  # Test comment in Russian
    entry = HostsEntry(entry_type='ipv4', address='192.168.1.1', 
                      names=['example.com'], comment=unicode_comment)
    
    assert isinstance(entry.comment, text_type)
    assert entry.comment == unicode_comment


def test_unicode_file_reading(tmpdir):
    """Test reading hosts file with Unicode content."""
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    unicode_content = """# Тестовый файл hosts
127.0.0.1\tlocalhost
192.168.1.1\tпример.com тест.localhost # Комментарий на русском
"""
    hosts_file.write(unicode_content.encode('utf-8'), mode='wb')
    
    hosts = Hosts(path=hosts_file.strpath)
    assert hosts.count() >= 2
    
    # Check that Unicode entries are properly loaded
    # The hostname will be normalized to IDN format
    normalized_hostname = normalize_hostname('пример.com')
    unicode_entry = None
    for entry in hosts.entries:
        if entry.entry_type in ('ipv4', 'ipv6') and entry.names:
            if normalized_hostname in entry.names or any('пример' in name for name in entry.names):
                unicode_entry = entry
                break
    
    assert unicode_entry is not None
    assert isinstance(unicode_entry.comment, text_type)


def test_unicode_file_writing(tmpdir):
    """Test writing hosts file with Unicode content."""
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts = Hosts(path=hosts_file.strpath)
    
    # Add Unicode entry
    unicode_entry = HostsEntry(
        entry_type='ipv4',
        address='192.168.1.100',
        names=['пример.com', 'тест.example'],
        comment='Комментарий на русском'
    )
    hosts.add([unicode_entry])
    
    # Write to file
    hosts.write()
    
    # Read back and verify
    import codecs
    with codecs.open(hosts_file.strpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Hostnames are normalized to IDN format for storage
    assert normalize_hostname('пример.com') in content
    assert normalize_hostname('тест.example') in content
    # Comments should remain as Unicode
    assert 'Комментарий на русском' in content


def test_unicode_import_from_file(tmpdir):
    """Test importing Unicode content from file."""
    # Create hosts file with Unicode content
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts_file.write("127.0.0.1\tlocalhost\n")
    
    # Create import file with Unicode content
    import_file = tmpdir.mkdir("input").join("import_hosts")
    unicode_import_content = """192.168.1.50\tпример.org тест.org # Импортированный комментарий
192.168.1.51\texample.рф"""
    import_file.write(unicode_import_content.encode('utf-8'), mode='wb')
    
    hosts = Hosts(path=hosts_file.strpath)
    initial_count = hosts.count()
    result = hosts.import_file(import_file.strpath)
    
    assert result['result'] == 'success'
    assert hosts.count() > initial_count  # Should have more entries
    
    # Check using normalized hostnames
    normalized_hostname1 = normalize_hostname('пример.org')
    normalized_hostname2 = normalize_hostname('example.рф')
    
    found_entry1 = False
    found_entry2 = False
    for entry in hosts.entries:
        if entry.entry_type in ('ipv4', 'ipv6') and entry.names:
            if normalized_hostname1 in entry.names:
                found_entry1 = True
            if normalized_hostname2 in entry.names:
                found_entry2 = True
    
    assert found_entry1, "Could not find {} in entries".format(normalized_hostname1)
    assert found_entry2, "Could not find {} in entries".format(normalized_hostname2)


def test_str_to_hostentry_with_unicode():
    """Test str_to_hostentry with Unicode input."""
    unicode_line = '192.168.1.200\tпример.net тест.net # Юникод комментарий'
    entry = HostsEntry.str_to_hostentry(unicode_line)
    
    assert entry is not False
    assert entry.entry_type == 'ipv4'
    assert entry.address == '192.168.1.200'
    # Check normalized hostnames
    assert normalize_hostname('пример.net') in entry.names
    assert normalize_hostname('тест.net') in entry.names
    assert isinstance(entry.comment, text_type)


def test_unicode_compatibility_functions():
    """Test Unicode compatibility utility functions."""
    # Test ensure_text
    byte_string = b'hello'
    text_string = 'hello'
    unicode_string = 'привет'
    
    assert isinstance(ensure_text(byte_string), text_type)
    assert isinstance(ensure_text(text_string), text_type)
    assert isinstance(ensure_text(unicode_string), text_type)
    
    # Test ensure_binary
    assert isinstance(ensure_binary(text_string), bytes)
    assert isinstance(ensure_binary(unicode_string), bytes)


def test_mixed_ascii_unicode_hostnames(tmpdir):
    """Test handling mixed ASCII and Unicode hostnames."""
    hosts_file = tmpdir.mkdir("etc").join("hosts")
    hosts = Hosts(path=hosts_file.strpath)
    
    # Add entry with mixed ASCII and Unicode names
    mixed_entry = HostsEntry(
        entry_type='ipv4',
        address='192.168.1.150',
        names=['example.com', 'пример.com', 'test.localhost']
    )
    hosts.add([mixed_entry])
    
    assert hosts.exists(names=['example.com'])
    assert hosts.exists(names=[normalize_hostname('пример.com')])
    assert hosts.exists(names=['test.localhost'])
    
    # Write and read back
    hosts.write()
    hosts2 = Hosts(path=hosts_file.strpath)
    
    assert hosts2.exists(names=['example.com'])
    assert hosts2.exists(names=[normalize_hostname('пример.com')])
    assert hosts2.exists(names=['test.localhost'])


def test_unicode_hostname_validation():
    """Test that Unicode hostnames are properly validated."""
    # Valid Unicode hostnames should work
    valid_unicode_names = ['пример.com', 'тест.localhost', 'example.рф']
    entry = HostsEntry(entry_type='ipv4', address='192.168.1.1', names=valid_unicode_names)
    assert entry.names == [normalize_hostname(name) for name in valid_unicode_names]


if __name__ == '__main__':
    pytest.main([__file__])