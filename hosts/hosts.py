# -*- coding: utf-8 -*-
""" This module contains the classes required to manage a hosts file """
import sys
import exception
from utils import is_ipv4, is_ipv6, valid_hostnames, is_readable, is_writeable
import urllib2

import time

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

class HostsEntry(object):
    """ An entry in a hosts file. """
    __slots__ = ['entry_type', 'address', 'comment', 'names']

    def __init__(self, entry_type=None, address=None, comment=None, names=None):
        #with Timer() as t:
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
        #print('HostsEntry took %.03f sec.' % t.interval)

    @staticmethod
    def get_entry_type(hosts_entry=None):
        """
        Return the type of entry for the line of hosts file passed
        :param hosts_entry: A line from the hosts file
        :return: comment | blank | ipv4 | ipv6
        """
        #with Timer() as t:
        if hosts_entry and isinstance(hosts_entry, str):
            entry = hosts_entry.strip()
            if not entry or entry[0] == "\n":
                return 'blank'
            if entry[0] == "#":
                return 'comment'
            entry_chunks = entry.split()
            if is_ipv4(entry_chunks[0]):
                return "ipv4"
            if is_ipv6(entry_chunks[0]):
                return "ipv6"
        #print('get_entry_type took %.03f sec.' % t.interval)
        return False

    @staticmethod
    def str_to_hostentry(entry):
        #with Timer() as t:
        if isinstance(entry, str):
            line_parts = entry.strip().split()
            if is_ipv4(line_parts[0]):
                if valid_hostnames(line_parts[1:]):
                    return HostsEntry(entry_type='ipv4', address=line_parts[0], names=line_parts[1:])
            elif is_ipv6(line_parts[0]):
                if valid_hostnames(line_parts[1:]):
                    return HostsEntry(entry_type='ipv6', address=line_parts[0], names=line_parts[1:])
            else:
                return None
        #print('str_to_hostentry took %.03f sec.' % t.interval)

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

    @staticmethod
    def write(entry_list=None, hosts_path=None):
        """
        Write the list of host entries back to the hosts file.
        """
        with Timer() as t:
            if is_writeable(hosts_path):
                with open(hosts_path, 'w') as hosts_file:
                    for line in entry_list:
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
        print('write took %.03f sec.' % t.interval)

    @staticmethod
    def get_hosts_by_url(url=None):
        response = urllib2.urlopen(url)
        return response.read()

    def import_url(self, url=None, force=False, hosts_path=None):
        file_contents = self.get_hosts_by_url(url=url)
        file_contents = file_contents.rstrip().replace('^M', '\n')
        file_contents = file_contents.rstrip().replace('\r\n', '\n')
        lines = file_contents.split('\n')
        new_entries = []
        for line in lines:
            if not line.strip() or str(line.strip).startswith('#'):
                continue
            else:
                new_entries.append(line)
        return self.add(entry=new_entries, force=force, hosts_path=hosts_path)

    def import_file(self, import_file_path=None, force=False):
        if is_readable(import_file_path):
            new_entries = []
            with open(import_file_path, 'r') as infile:
                for line in infile:
                    if not line.strip() or str(line.strip).startswith('#'):
                        continue
                    new_entries.append(line)
            return self.add(entry=new_entries, force=force)
        else:
            return {'result': 'failed',
                    'message': 'Cannot read: file {0}.'.format(import_file_path)}

    def add(self, entry=None, force=False, entry_list=None, hosts_path=None):
        """
        Adds an entry to a host file.
        :param entry: A list, string or instance of HostsEntry
                      to add to the hosts file
        :param force: Remove conflicting, existing instances first
        :return: True if successfully added to hosts file
        """
        print "IN ADD"
        new_entries = []
        added_count = 0
        replaced_count = 0
        unchanged_count = 0
        failed_count = 0

        # GENERATE A LIST OF NEW ENTRIES
        if isinstance(entry, list):
            for item in entry:
                if isinstance(item, str):
                    hostentry_item = HostsEntry.str_to_hostentry(item)
                    if hostentry_item:
                        if hostentry_item.entry_type == 'ipv4' or hostentry_item.entry_type == 'ipv4':
                            new_entries.append(hostentry_item)
                    else:
                        failed_count += 1
                        continue
        elif isinstance(entry, str):
            new_entry = HostsEntry.str_to_hostentry(entry)
            if new_entry:
                new_entries.append(new_entry)
            else:
                failed_count += 1
        elif isinstance(entry, HostsEntry):
            new_entries.append(entry)
        print "FINISHED GENERATING A LIST OF NEW ENTRIES"
        # IF THERE'S NOTHING TO BE ADDED - RETURN A FAILURE
        if not new_entries:
            return {'result': 'failed', 'message': 'Cannot add entry. \
                     Not recognised as a valid comment, \
                     ipv4 address or ipv6 address.'}

        # LOOP THROUGH AND ADD THE NEW ENTRIES
        print "Looping through: {} entries".format(len(new_entries))
        mycount = 0
        local_entries = self.entries
        for new_entry in new_entries:
            mycount += 1
            #with Timer() as t:
            #with Timer() as d:
            existing = self.count(entry=new_entry, entry_list=local_entries)
            #print('Finished initial count %.03f sec.' % d.interval)
            existing_addresses = existing.get('address_matches')
            existing_names = existing.get('name_matches')

            """
            If it looks like we're adding ad blocker entries then
            only add if same address and matching names don't exist
            """
            if new_entry.address in ('0.0.0.0', '127.0.0.1'):
                # with Timer() as z:
                if all((existing_addresses, existing_names)):
                    unchanged_count += 1
                else:
                    local_entries.append(new_entry)
                    #self.entries = map(new_entry, self.entries)
                    added_count += 1
                # print('Finished %.03f sec.' % z.interval)
            elif not force and any((existing_addresses, existing_names)):
                print "NOT FORCE AND ANY (addr/name)"
                unchanged_count += 1
            elif not force and not any((existing_addresses, existing_names)):
                print "NOT FORCE AND NOT AN (addr/name)"
                #with Timer() as y:
                local_entries.append(new_entry)
                added_count += 1
                #print('Finished %.03f sec.' % y.interval)
            elif force and any((existing_addresses, existing_names)):
                print "FORCING"
                entry_list = Hosts.remove(entry=new_entry, entry_list=entry_list, batch=True)
                local_entries.append(new_entry)
                replaced_count += 1
            #print('loop took %.03f sec.' % t.interval)
        #self.entries = local_entries
        print "Finished looping through {} entries.".format(mycount)
        Hosts.write(entry_list=local_entries, hosts_path=hosts_path)
        if any((added_count, replaced_count)):
            result_status = 'success'
        else:
            result_status = 'failed'
        return {'result': result_status,
                'message': 'Added: {0} Replaced: {1} Unchanged: {2} Failed: {3}'.format(added_count,
                                                                                        replaced_count,
                                                                                        unchanged_count,
                                                                                        failed_count)}

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
                #with Timer() as f:
                if all((existing_names, entry.names)) and \
                        set(entry.names).intersection(existing_names):
                    num_name_matches += 1
                if existing_host_address and \
                        existing_host_address == entry.address:
                    num_address_matches += 1
                #print('\tCount took %.03f sec.' % f.interval)
            if entry.entry_type == "comment":
                if existing_comment == entry.comment:
                    num_comment_matches += 1

        return {'address_matches': num_address_matches,
                'name_matches': num_name_matches,
                'comment_matches': num_comment_matches}

    @staticmethod
    def remove(entry=None, address=None, names=None, comment=None, batch=False, entry_list=None, hosts_path=None):
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
            Hosts.write(entry_list=entry_list, hosts_path=hosts_path)
        return entry_list

    def populate_entries(self):
        """
        Read all hosts file entries from the hosts file specified
        and store them as HostEntry's in an instance of Hosts.
        """
        try:
            local_entries = []
            with open(self.hosts_path, 'r') as hosts_file:
                hosts_entries = [line for line in hosts_file]
                for hosts_entry in hosts_entries:
                    entry_type = HostsEntry.get_entry_type(hosts_entry)
                    if entry_type == "comment":
                        local_entries.append(HostsEntry(entry_type="comment",
                                                        comment=hosts_entry))
                    elif entry_type == "blank":
                        local_entries.append(HostsEntry(entry_type="blank"))
                    elif entry_type == "ipv4" or entry_type == "ipv6":
                        chunked_entry = hosts_entry.split()
                        local_entries.append(
                            HostsEntry(
                                entry_type=entry_type,
                                address=chunked_entry[0],
                                names=chunked_entry[1:]))
            
            self.entries = local_entries
        except IOError:
            raise
