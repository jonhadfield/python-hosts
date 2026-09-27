# -*- coding: utf-8 -*-
"""
This module contains utility functions used by the Hosts and HostsEntry methods
"""
from __future__ import unicode_literals
import os
import re
import sys

import socket

from python_hosts.unicode_utils import (ensure_text, ensure_binary,
                                        normalize_hostname)

# Four dotted-decimal octets; rejects abbreviated forms accepted by inet_aton
# such as "127.1" or "1.2.3".
_IPV4_RE = re.compile(
    r'^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}'
    r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$'
)


def _socket_address(entry):
    """Return address as a native socket-friendly string (bytes on Py2)."""
    text = ensure_text(entry)
    if sys.version_info[0] == 2:
        return ensure_binary(text, encoding='ascii')
    return text


def is_ipv4(entry):
    """Return ``True`` if ``entry`` is a valid IPv4 address."""
    if not entry:
        return False
    entry = ensure_text(entry).strip()
    if not _IPV4_RE.match(entry):
        return False
    try:
        socket.inet_aton(_socket_address(entry))
    except (socket.error, UnicodeError, TypeError, ValueError):
        return False
    return True


def is_ipv6(entry):
    """Return ``True`` if ``entry`` is a valid IPv6 address."""
    if not entry:
        return False
    try:
        socket.inet_pton(socket.AF_INET6, _socket_address(entry))
    except (socket.error, UnicodeError, TypeError, ValueError, AttributeError):
        return False
    return True


def valid_hostnames(hostname_list):
    """Return ``True`` if all items in ``hostname_list`` are valid hostnames."""
    if not hostname_list:
        return False
    
    # ASCII hostname pattern
    allowed_ascii = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
    
    for entry in hostname_list:
        # Ensure it's a text string
        entry = ensure_text(entry)
        
        if not entry or len(entry) > 255:
            return False
            
        # Try to normalize the hostname (handles IDN conversion)
        try:
            normalized = normalize_hostname(entry)
            
            # Check if normalized hostname is valid ASCII
            if len(normalized) <= 255 and all(allowed_ascii.match(x) for x in normalized.split('.')):
                continue
                
            # If normalization didn't work, check if it's already ASCII-compatible
            if all(ord(c) < 128 for c in entry):
                if all(allowed_ascii.match(x) for x in entry.split('.')):
                    continue
                    
            # For Unicode hostnames, check basic structure
            # Allow Unicode characters in hostname parts
            parts = entry.split('.')
            if not parts:
                return False
                
            valid_parts = True
            for part in parts:
                if not part or len(part) > 63:
                    valid_parts = False
                    break
                # Check that part doesn't start or end with hyphen
                if part.startswith('-') or part.endswith('-'):
                    valid_parts = False
                    break
                    
            if not valid_parts:
                return False
                
        except Exception:
            # If any error occurs during validation, be conservative
            return False
            
    return True


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
