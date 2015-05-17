# -*- coding: utf-8 -*-
""" This module contains the classes required to manage a hosts file """
import sys
from .utils import is_ipv4, is_ipv6


class HostsEntry(object):
    """ An entry in a hosts file. """
    def __init__(self, entry_type=None, address=None, comment=None, names=None):
        if not entry_type or entry_type not in ('ipv4',
                                                'ipv6',
                                                'comment',
                                                'blank'):
            raise Exception('entry_type invalid or not specified')

        if entry_type == 'comment' and not comment:
            raise Exception('entry_type comment supplied without value.')

        if entry_type in ('ipv4', 'ipv6'):
            if not all((address, names)):
                raise Exception('Address and Name(s) must be specified.')

        self.entry_type = entry_type
        self.address = address
        self.comment = comment
        self.names = names

    @staticmethod
    def get_entry_type(hosts_entry):
        """
        Return the type of entry for the line of hosts file passed
        :param hosts_entry: A line from the hosts file
        :return: comment | blank | ipv4 | ipv6
        """
        if hosts_entry[0] == "#":
            return 'comment'
        if hosts_entry[0] == "\n":
            return 'blank'
        entry_chunks = hosts_entry.split()
        if is_ipv4(entry_chunks[0]):
            return "ipv4"
        if is_ipv6(entry_chunks[0]):
            return "ipv6"
        else:
            return False

class Hosts(object):
    """ A hosts file. """
    def __init__(self, path=None):
        """
        Returns a list of all entries in the hosts file.
        Each entry is represented in the form of a dict.
        """
        platform = sys.platform
        if path:
            self.hosts_path = path
        elif 'linux' in platform or 'darwin' == platform:
            self.hosts_path = '/etc/hosts'
        elif any((platform == 'win32', platform == 'windows')):
            self.hosts_path = r'c:\windows\system32\drivers\etc\hosts'
        else:
            exit("cannot determine platform")
        self.entries = []
        self.populate_entries()

    def write(self):
        """
        Write the list of host entries back to the hosts file.
        """
        with open(self.hosts_path, 'w') as hosts_file:
            for line in self.entries:
                if line.entry_type == 'comment':
                    hosts_file.write(line.comment)
                if line.entry_type == 'blank':
                    hosts_file.write("\n")
                if line.entry_type == 'ipv4':
                    hosts_file.write(
                        "{0}\t{1}\n".format(
                            line.address,
                            ' '.join(line.names),
                        )
                    )
                if line.entry_type == 'ipv6':
                    hosts_file.write(
                        "{0}\t{1}\n".format(
                            line.address,
                            ' '.join(line.names),))

    def add(self, entry=None, force=False):
        """
        Adds an entry to a host file.
        :param entry: An instance of HostsEntry
        :param force: Remove conflicting, existing instances first
        :return: True if successfully added to hosts file
        """
        new_entry = entry
        if new_entry.entry_type == "comment":
            existing = self.count(new_entry).get('num_comment_matches')
            if existing:
                return False
        elif new_entry.entry_type == "ipv4" or new_entry.entry_type == "ipv6":
            existing = self.count(new_entry)
            existing_addresses = existing.get('num_address_matches')
            existing_names = existing.get('num_name_matches')
            if not force and (existing_addresses or existing_names):
                return False
            elif force:
                self.remove(passed_address=new_entry.address,
                            passed_names=new_entry.names)
        self.entries.append(new_entry)
        self.write()
        return True

    def count(self, entry=None):
        """
        Count the number of address, name or comment matches
        in the given HostsEntry instance or supplied values
        :param entry: An instance of HostsEntry
        :return: A dict listing the number of address, name and comment matches
        """
        if not entry:
            exit('valid entry not provided')

        num_address_matches = 0
        num_name_matches = 0
        num_comment_matches = 0
        for host in self.entries:
            existing_names = host.names
            existing_host_address = host.address
            existing_comment = host.comment
            if entry.entry_type == "ipv4" or entry.entry_type == "ipv6":
                if all((existing_names, entry.names)) and \
                        set(entry.names).intersection(existing_names):
                    num_name_matches += 1
                if existing_host_address and \
                        existing_host_address == entry.address:
                    num_address_matches += 1
            if entry.entry_type == "comment":
                if existing_comment == entry.comment:
                    num_comment_matches += 1
        return {'address_matches': num_address_matches,
                'name_matches': num_name_matches,
                'comment_matches': num_comment_matches}

    def remove(self,
               entry=None,
               passed_address=None,
               passed_names=None,
               passed_comment=None):
        """
        Remove an entry from a hosts file
        :param entry: An instance of HostsEntry
        :param passed_address: The address of the host to remove
        :param passed_names: The name(s) of the host to remove
        :param passed_comment: The comment to remove
        :return:
        """
        removed = 0
        removal_list = []
        for existing_entry in self.entries:
            if entry:
                if existing_entry.names and entry.get("names"):
                    names_inter = set(
                        existing_entry.names).intersection(entry.get("names"))
                    if any((existing_entry.address == entry.get('address'),
                            existing_entry.names == entry.get('names'),
                            names_inter)):
                        removal_list.append(existing_entry)
                        removed += 1
                if entry.comment and existing_entry.comment == entry.comment:
                    removal_list.append(existing_entry)
            else:
                if existing_entry.names and passed_names:
                    names_inter = set(
                        existing_entry.names).intersection(passed_names)
                    if any((existing_entry.address == passed_address,
                            existing_entry.names == passed_names,
                            names_inter)):
                        removal_list.append(existing_entry)
                        removed += 1
                if passed_comment and existing_entry.comment == passed_comment:
                    removal_list.append(existing_entry)
        for entry_to_remove in removal_list:
            self.entries.remove(entry_to_remove)
        self.write()
        if removed > 0:
            return True
        return False

    def populate_entries(self):
        """
        Read all hosts file entries from the hosts file specified
        and store them as HostEntry's in an instance of Hosts.
        """
        try:
            with open(self.hosts_path, 'r') as hosts_file:
                hosts_entries = [line for line in hosts_file]
                for hosts_entry in hosts_entries:
                    entry_type = HostsEntry.get_entry_type(hosts_entry)
                    if entry_type == "comment":
                        self.entries.append(HostsEntry(entry_type="comment",
                                                       comment=hosts_entry))
                    if entry_type == "blank":
                        self.entries.append(HostsEntry(entry_type="blank"))
                    if entry_type == "ipv4" or entry_type == "ipv6":
                        chunked_entry = hosts_entry.split()
                        self.entries.append(HostsEntry(entry_type=entry_type,
                                                       address=chunked_entry[0],
                                                       names=chunked_entry[1:]))
        except IOError:
            exit("File not found: {}".format(self.hosts_path))
