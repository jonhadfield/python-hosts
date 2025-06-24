# -*- coding: utf-8 -*-
"""
Unicode compatibility utilities for Python 2.7 and 3.x support.

This module provides utilities to handle Unicode strings consistently
across Python versions while maintaining backward compatibility.
"""

import sys

# Python 2/3 compatibility
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    
    def ensure_text(s, encoding='utf-8', errors='strict'):
        """Ensure string is unicode text type."""
        if isinstance(s, binary_type):
            return s.decode(encoding, errors)
        elif isinstance(s, text_type):
            return s
        else:
            return text_type(s)
    
    def ensure_binary(s, encoding='utf-8', errors='strict'):
        """Ensure string is binary type."""
        if isinstance(s, text_type):
            return s.encode(encoding, errors)
        elif isinstance(s, binary_type):
            return s
        else:
            return text_type(s).encode(encoding, errors)

else:  # Python 2
    text_type = unicode
    binary_type = str
    string_types = (basestring,)
    
    def ensure_text(s, encoding='utf-8', errors='strict'):
        """Ensure string is unicode text type."""
        if isinstance(s, binary_type):
            return s.decode(encoding, errors)
        elif isinstance(s, text_type):
            return s
        else:
            return text_type(s)
    
    def ensure_binary(s, encoding='utf-8', errors='strict'):
        """Ensure string is binary type."""
        if isinstance(s, text_type):
            return s.encode(encoding, errors)
        elif isinstance(s, binary_type):
            return s
        else:
            return binary_type(s)


def safe_open(file_path, mode='r', encoding='utf-8', errors='strict'):
    """
    Open a file with proper Unicode handling for both Python 2 and 3.
    
    :param file_path: Path to the file
    :param mode: File mode ('r', 'w', etc.)
    :param encoding: Text encoding (default: utf-8)
    :param errors: Error handling strategy
    :return: File object
    """
    if PY3:
        if 'b' not in mode:
            return open(file_path, mode, encoding=encoding, errors=errors)
        else:
            return open(file_path, mode)
    else:  # Python 2
        import codecs
        if 'b' not in mode:
            return codecs.open(file_path, mode, encoding=encoding, errors=errors)
        else:
            return open(file_path, mode)


def normalize_hostname(hostname):
    """
    Normalize hostname to ensure consistent Unicode handling.
    
    :param hostname: Hostname string
    :return: Normalized Unicode hostname
    """
    if not hostname:
        return hostname
    
    # Ensure it's Unicode text
    hostname = ensure_text(hostname)
    
    # Basic normalization - lowercase and strip whitespace
    hostname = hostname.lower().strip()
    
    # Handle IDN (Internationalized Domain Names)
    try:
        # Convert Unicode domain to ASCII-compatible encoding
        hostname = hostname.encode('idna').decode('ascii')
    except (UnicodeError, UnicodeDecodeError):
        # If IDN encoding fails, keep as-is but ensure it's valid Unicode
        pass
    
    return hostname


def normalize_comment(comment):
    """
    Normalize comment to ensure consistent Unicode handling.
    
    :param comment: Comment string
    :return: Normalized Unicode comment
    """
    if not comment:
        return comment
    
    # Ensure it's Unicode text
    comment = ensure_text(comment)
    
    # Strip whitespace but preserve internal spacing
    comment = comment.strip()
    
    return comment


def is_unicode_string(s):
    """
    Check if a string is a Unicode text type.
    
    :param s: String to check
    :return: True if Unicode text type, False otherwise
    """
    return isinstance(s, text_type)


def to_native_string(s):
    """
    Convert string to the native string type for the Python version.
    
    In Python 2: Unicode -> str (if ASCII) or keep as Unicode
    In Python 3: Always Unicode (str)
    
    :param s: String to convert
    :return: Native string type
    """
    if PY3:
        return ensure_text(s)
    else:
        # In Python 2, try to convert to str if ASCII, otherwise keep as Unicode
        if isinstance(s, text_type):
            try:
                return s.encode('ascii')
            except UnicodeEncodeError:
                return s
        return s