# -*- coding: utf-8 -*-
import socket
import re
import os


def is_ipv4(entry):
    """ Checks if a string is a valid ipv4 address. """
    try:
        if socket.inet_aton(entry):
            return True
    except socket.error:
        return False


def is_ipv6(entry):
    """ Checks if a string is a valid ipv6 address. """
    try:
        if socket.inet_pton(socket.AF_INET6, entry):
            return True
    except socket.error:
        return False


def valid_hostnames(hostname_list):
    """ Checks if all provided hostnames are valid. """
    for entry in hostname_list:
        if len(entry) > 255:
            return False
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        if not all(allowed.match(x) for x in entry.split(".")):
            return False
    return True


def is_readable(path=None):
    if os.path.isfile(path) and os.access(path, os.R_OK):
        return True


def is_writeable(path=None):
    if os.path.isfile(path) and os.access(path, os.W_OK):
        return True
