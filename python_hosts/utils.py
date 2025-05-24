# -*- coding: utf-8 -*-
"""
This module contains utility functions used by the Hosts and HostsEntry methods
"""
import os
import re

import socket


def is_ipv4(entry):
    """Return ``True`` if ``entry`` is a valid IPv4 address."""
    try:
        socket.inet_aton(entry)
    except socket.error:
        return False
    return True


def is_ipv6(entry):
    """Return ``True`` if ``entry`` is a valid IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET6, entry)
    except socket.error:
        return False
    return True


def valid_hostnames(hostname_list):
    """Return ``True`` if all items in ``hostname_list`` are valid hostnames."""
    allowed = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
    return all(len(entry) <= 255 and
               all(allowed.match(x) for x in entry.split('.'))
               for entry in hostname_list)


def is_readable(path=None):
    """Return ``True`` if ``path`` exists and is readable."""
    return os.path.isfile(path) and os.access(path, os.R_OK)


def dedupe_list(seq):
    """
    Utility function to remove duplicates from a list
    :param seq: The sequence (list) to deduplicate
    :return: A list with original duplicates removed
    """
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]
