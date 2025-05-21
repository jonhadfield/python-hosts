# -*- coding: utf-8 -*-
import os
import sys

from python_hosts.utils import is_ipv4, is_ipv6, valid_hostnames, dedupe_list, is_readable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_ipv4_validation_success():
    """ Test function returns True if valid IPv4 address is specified """
    assert is_ipv4('8.8.8.8')


def test_ipv4_validation_failure():
    """
    Test function returns False if invalid IPv4 address is specified
    """
    assert not is_ipv4('256.8.8.8')


def test_ipv6_validation_success():
    """
    Test function returns True if valid IPv4 address is specified
    """
    assert is_ipv6('2001:db8::ff00:42:8329')


def test_ipv6_validation_failure():
    """
    Test function returns False if invalid IPv4 address is specified
    """
    assert not is_ipv6('2001::0234:C1ab::A0:aabc:003F')


def test_hostname_validation_success():
    """
    Test function returns True if valid hostnames are specified
    """
    assert valid_hostnames(['example.com', 'example'])


def test_hostname_validation_failure_too_long():
    """
    Test function returns False if a hostname over 255 chars is specified
    """
    long_hostname = 'x' * 256
    assert not valid_hostnames(['example.com', long_hostname])


def test_hostname_validation_failure_with_leading_hyphen():
    """
    Test function returns False if a hostname with a leading hyphen is specified
    """
    assert not valid_hostnames(['example.com', '-example'])


def test_dedupe_list_preserves_order():
    """Ensure dedupe_list removes duplicates while keeping order."""
    items = ['a', 'b', 'a', 'c', 'b']
    assert dedupe_list(items) == ['a', 'b', 'c']


def test_is_readable(tmpdir):
    """Check is_readable returns expected values."""
    readable = tmpdir.join('file')
    readable.write('data')
    assert is_readable(readable.strpath)
    assert not is_readable(readable.strpath + '_missing')
