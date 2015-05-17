__author__ = 'hadfielj'
import socket

class InvalidIPv4Address(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def is_ipv4(entry):
    """ Checks if a string is a valid ipv4 address. """
    try:
        if socket.inet_aton(entry):
            return True
    except socket.error:
        raise

def is_ipv6(entry):
    """ Checks if a string is a valid ipv6 address. """
    try:
        if socket.inet_pton(socket.AF_INET6, entry):
            return True
    except socket.error:
        raise
