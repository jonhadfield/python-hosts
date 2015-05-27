# -*- coding: utf-8 -*-
""" This module contains the classes required to manage a hosts file """
import sys
import exception
from utils import is_ipv4, is_ipv6, valid_hostnames, is_readable, is_writeable
import urllib2


class HostsEntry(object):
    """ An entry in a hosts file. """
    __slots__ = ['entry_type', 'address', 'comment', 'names']

    def __init__(self, entry_type=None, address=None, comment=None, names=None):
        if not entry_type or entry_type not in ('ipv4',
                                                'ipv6',
                                                'comment',
                                                'blank'):
            raise Exception('entry_type invalid or not specified')

        if entry_type == 'comment' and not comment:
            raise Exception('entry_type comment supplied without value.')

        if entry_type == 'ipv4':
            if not all((address, names)):
                raise Exception('Address and Name(s) must be specified.')
            if not is_ipv4(address):
                raise exception.InvalidIPv4Address()

        if entry_type == 'ipv6':
            if not all((address, names)):
                raise Exception('Address and Name(s) must be specified.')
            if not is_ipv6(address):
                raise exception.InvalidIPv6Address()

        self.entry_type = entry_type
        self.address = address
        self.comment = comment
        self.names = names

    @staticmethod
    def get_entry_type(hosts_entry=None):
        """
        Return the type of entry for the line of hosts file passed
        :param hosts_entry: A line from the hosts file
        :return: comment | blank | ipv4 | ipv6
        """
        if hosts_entry and isinstance(hosts_entry, str):
            entry = hosts_entry.strip()
            if not entry[0] or entry[0] == "\n":
                return 'blank'
            if entry[0] == "#":
                return 'comment'
            entry_chunks = entry.split()
            if is_ipv4(entry_chunks[0]):
                return 'ipv4'
            if is_ipv6(entry_chunks[0]):
                return 'ipv6'
        else:
            return False

    @staticmethod
    def str_to_hostentry(entry):
        # with Timer() as t:
        if isinstance(entry, str):
            line_parts = entry.strip().split()
            if is_ipv4(line_parts[0]):
                if valid_hostnames(line_parts[1:]):
                    return HostsEntry(entry_type='ipv4', address=line_parts[0], names=line_parts[1:])
            elif is_ipv6(line_parts[0]):
                if valid_hostnames(line_parts[1:]):
                    return HostsEntry(entry_type='ipv6', address=line_parts[0], names=line_parts[1:])
            else:
                return False


class Hosts(object):
    """ A hosts file. """
    __slots__ = ['entries', 'hosts_path']

    def __init__(self, path=None):
        """
        Returns a list of all entries in the hosts file.
        Each entry is represented in the form of a dict.
        """
        self.entries = []
        if path:
            self.hosts_path = path
        else:
            self.hosts_path = self.determine_hosts_path()
        self.populate_entries()

    @staticmethod
    def determine_hosts_path(platform=None):
        """
        Return the hosts file path based on the supplied
        or detected platform.
        :param platform: override platform detection
        :return: path of hosts file
        """
        if not platform:
            platform = sys.platform
        if platform.startswith('win'):
            return r'c:\windows\system32\drivers\etc\hosts'
        else: 
            return '/etc/hosts'

    def dedupe_entries_1(self):
        deduped_entry_list = []
        for item in self.entries:
            if item not in deduped_entry_list:
                deduped_entry_list.append(item)
        self.entries = deduped_entry_list

    def dedupe_entries_2(self):
        self.entries = list(set(self.entries))

    def write(self):
        """
        Write the list of host entries back to the hosts file.
        """
        written_count = 0
        if is_writeable(self.hosts_path):
            with open(self.hosts_path, 'w') as hosts_file:
                for count, line in enumerate(self.entries):
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
                return written_count
        return False

    @staticmethod
    def get_hosts_by_url(url=None):
        response = urllib2.urlopen(url)
        return response.read()

    def import_url(self, url=None):
        file_contents = self.get_hosts_by_url(url=url)
        file_contents = file_contents.rstrip().replace('^M', '\n')
        file_contents = file_contents.rstrip().replace('\r\n', '\n')
        lines = file_contents.split('\n')

        add_result = self.add(lines)
        print add_result
        self.dedupe_entries_2()
        write_result = self.write()
        if write_result:
            print write_result
            return add_result

    def import_file(self, import_file_path=None):
        if is_readable(import_file_path):
            new_entries = []
            with open(import_file_path, 'r') as infile:
                for line in infile:
                    if not line.strip() or str(line.strip).startswith('#'):
                        continue
                    new_entries.append(line)
            return self.add(entries=new_entries)
        else:
            return {'result': 'failed',
                    'message': 'Cannot read: file {0}.'.format(import_file_path)}

    def add(self, entries=None):
        """
        Adds to the instance list of entries.
        :param entries: A list of strings or instances of HostsEntry
        :return: The number of successes and failures
        """
        ipv4_count = 0
        ipv6_count = 0
        invalid_count = 0
        blank_count = 0
        comment_count = 0

        # GENERATE A LIST OF NEW ENTRIES
        if not isinstance(entries, list):
            return False
        for item in entries:
            if isinstance(item, str):
                entry_type = HostsEntry.get_entry_type(hosts_entry=item)
                if entry_type == 'blank':
                    blank_count += 1
                    continue
                elif entry_type == 'comment':
                    comment_count += 1
                    continue
                elif entry_type == 'ipv4':
                    ipv4_count += 1
                elif entry_type == 'ipv6':
                    ipv6_count += 1
                else:
                    invalid_count += 1
                    continue
                new_item = HostsEntry.str_to_hostentry(item)
                if new_item:
                    self.entries.append(new_item)
            elif isinstance(item, HostsEntry):
                self.entries.append(item)
            else:
                invalid_count += 1
        print "FINISHED ADDING LIST OF ENTRIES TO SELF.ENTRIES"
        return {'ipv4_count': ipv4_count,
                'ipv6_count': ipv6_count,
                'blank_count': blank_count,
                'invalid_count': invalid_count}

    @staticmethod
    def count(entry=None, entry_list=None):
        """
        Count the number of address, name or comment matches
        in the given HostsEntry instance or supplied values
        :param entry: An instance of HostsEntry
        :return: A dict listing the number of address, name and comment matches
        """
        if isinstance(entry, str):
            entry = HostsEntry.str_to_hostentry(entry)

        num_address_matches = 0
        num_name_matches = 0
        num_comment_matches = 0
        for host in entry_list:
            existing_names = host.names
            existing_host_address = host.address
            existing_comment = host.comment
            if entry.entry_type == "ipv4" or entry.entry_type == "ipv6":
                # with Timer() as f:
                if all((existing_names, entry.names)) and \
                        set(entry.names).intersection(existing_names):
                    num_name_matches += 1
                if existing_host_address and \
                        existing_host_address == entry.address:
                    num_address_matches += 1
                # print('\tCount took %.03f sec.' % f.interval)
            if entry.entry_type == "comment":
                if existing_comment == entry.comment:
                    num_comment_matches += 1

        return {'address_matches': num_address_matches,
                'name_matches': num_name_matches,
                'comment_matches': num_comment_matches}

    def remove(self, entry=None, address=None, names=None, comment=None, batch=False, entry_list=None):
        """
        Remove an entry from a hosts file
        :param entry: An instance of HostsEntry
        :return:
        """
        removed = 0
        removal_list = []
        ''' if an instance of HostsEntry is supplied '''
        if isinstance(entry, HostsEntry):
            entry_names = entry.names
            entry_address = entry.address
            entry_comment = entry.comment
        else:
            entry_names = names
            entry_address = address
            entry_comment = comment

        for existing_entry in entry_list:
            if existing_entry.entry_type in ['ipv4', 'ipv6']:
                names_inter = None
                if entry_names:
                    names_inter = set(
                        existing_entry.names).intersection(entry_names)
                if any((existing_entry.address == entry_address,
                        existing_entry.names == entry_names,
                        names_inter)):
                    removal_list.append(existing_entry)
                    removed += 1
            if entry_comment and entry_comment == existing_entry.comment:
                removal_list.append(existing_entry)
        for entry_to_remove in removal_list:
            entry_list.remove(entry_to_remove)
        if not batch:
            self.write()
        return entry_list

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
                    elif entry_type == "blank":
                        self.entries.append(HostsEntry(entry_type="blank"))
                    elif entry_type == "ipv4" or entry_type == "ipv6":
                        chunked_entry = hosts_entry.split()
                        self.entries.append(
                            HostsEntry(
                                entry_type=entry_type,
                                address=chunked_entry[0],
                                names=chunked_entry[1:]))
        except IOError:
            raise
