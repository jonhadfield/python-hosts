# -*- coding: utf-8 -*-
import socket
import re

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

def are_valid_hostnames(hostname_list):
    """ Checks if all provided hostnames are valid. """
    for entry in hostname_list:
        if len(entry) > 255:
            return False
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        if not all(allowed.match(x) for x in entry.split(".")):
            return False
    return True