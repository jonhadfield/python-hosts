# -*- coding: utf-8 -*-
__author__ = 'hadfielj'
import socket

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
