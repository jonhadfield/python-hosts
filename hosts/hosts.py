# -*- coding: utf-8 -*-
""" This module contains the classes required to manage a hosts file """
import sys
import exception
from utils import is_ipv4, is_ipv6, valid_hostnames, is_readable, is_writeable
import urllib2
import os


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
            if not entry or not entry[0] or entry[0] == "\n":
                return 'blank'
            if entry[0] == "#":
                return 'comment'
            entry_chunks = entry.split()
            if is_ipv6(entry_chunks[0]):
                return 'ipv6'
            if is_ipv4(entry_chunks[0]):
                return 'ipv4'

    @staticmethod
    def str_to_hostentry(entry):
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

#    def dedupe_entries(self):
#        existing_type_address_hashes = []
#        existing_names_hashes = []
#        deduped = []
#        for entry in self.entries:
#            if entry.entry_type in ('ipv4', 'ipv6'):
#                type_address_hash = hashlib.sha224("{0}{1}".format(entry.entry_type,
#                                                                   entry.address)).hexdigest()
#                names_hashes = []
#                for name in entry.names:
#                    hl = hashlib.sha224(name).hexdigest()
#                    names_hashes.append(hl)

#                if type_address_hash not in existing_type_address_hashes:
#                    #print set(names_hashes)
#                    #print set(existing_name_hashes)
#                    if not set(tuple(existing_names_hashes)).intersection(tuple(names_hashes)):
#                        deduped.append(entry)
#                existing_type_address_hashes.append(type_address_hash)
#                existing_names_hashes.append(names_hashes)
#            if entry.entry_type in ('comment', 'blank'):
#                    deduped.append(entry)
#        self.entries = deduped

    def write(self):
        """
        Write the list of host entries back to the hosts file.
        """
        written_count = 0
        comments_written = 0
        blanks_written = 0
        ipv4_entries_written = 0
        ipv6_entries_written = 0
        filemode = None
        if not os.path.exists(self.hosts_path):
            filemode = 'a+'
        if os.path.exists(self.hosts_path) and is_writeable(self.hosts_path):
            filemode = 'w'
        with open(self.hosts_path, filemode) as hosts_file:
            for written_count, line in enumerate(self.entries):
                if line.entry_type == 'comment':
                    hosts_file.write(line.comment)
                    comments_written += 1
                if line.entry_type == 'blank':
                    hosts_file.write("\n")
                    blanks_written += 1
                if line.entry_type == 'ipv4':
                    hosts_file.write(
                        "{0}\t{1}\n".format(
                            line.address,
                            ' '.join(line.names),
                            )
                        )
                    ipv4_entries_written += 1
                if line.entry_type == 'ipv6':
                    hosts_file.write(
                        "{0}\t{1}\n".format(
                            line.address,
                            ' '.join(line.names),))
                    ipv6_entries_written += 1
            return {'total_written': written_count+1,
                    'comments_written': comments_written,
                    'blanks_written': blanks_written,
                    'ipv4_entries_written': ipv4_entries_written,
                    'ipv6_entries_written': ipv6_entries_written}

    @staticmethod
    def get_hosts_by_url(url=None):
        response = urllib2.urlopen(url)
        return response.read()

    def exists(self, address=None, names=None):
        for entry in self.entries:
            if address and address == entry.address:
                return True
            if names:
                for name in names:
                    if name in entry.names:
                        return True
        return False

    def remove_all_matching(self, address=None, name=None):
        to_remove = []
        if address and name:
            to_remove = [x for x in self.entries if x.address == address and name in x.names]
        elif address:
            to_remove = [x for x in self.entries if x.address == address]
        elif name:
            to_remove = [x for x in self.entries if name in x.names]
        for item_to_remove in to_remove:
            self.entries.remove(item_to_remove)

    def import_url(self, url=None, force=False):
        file_contents = self.get_hosts_by_url(url=url)
        file_contents = file_contents.rstrip().replace('^M', '\n')
        file_contents = file_contents.rstrip().replace('\r\n', '\n')
        lines = file_contents.split('\n')
        skipped = 0
        import_entries = []
        for line in lines:
            stripped_entry = line.strip()
            if (not stripped_entry) or (stripped_entry.startswith('#')):
                skipped += 1
            else:
                line = line.partition('#')[0]
                line = line.rstrip()
                import_entry = HostsEntry.str_to_hostentry(line)
                if import_entry:
                    import_entries.append(import_entry)
        add_result = self.add(entries=import_entries)
        write_result = self.write()
        return {'result': 'success',
                'skipped': skipped,
                'add_result': add_result,
                'write_result': write_result}

    def import_file(self, import_file_path=None):
        skipped = 0
        invalid_count = 0
        if is_readable(import_file_path):
            import_entries = []
            with open(import_file_path, 'r') as infile:
                for entries_count, line in enumerate(infile):
                    stripped_entry = line.strip()
                    if (not stripped_entry) or (stripped_entry.startswith('#')):
                        skipped += 1
                    else:
                        line = line.partition('#')[0]
                        line = line.rstrip()
                        import_entry = HostsEntry.str_to_hostentry(line)
                        if import_entry:
                            import_entries.append(import_entry)
                        else:
                            invalid_count += 1
            add_result = self.add(entries=import_entries)
            write_result = self.write()
            return {'result': 'success',
                    'skipped': skipped,
                    'invalid_count': invalid_count,
                    'add_result': add_result,
                    'write_result': write_result}
        else:
            return {'result': 'failed',
                    'message': 'Cannot read: file {0}.'.format(import_file_path)}

    def add(self, entries=None, force=False):
        """
        Adds to the instance list of entries.
        :param entries: A list of instances of HostsEntry
        :return: The number of successes and failures
        """
        ipv4_count = 0
        ipv6_count = 0
        invalid_count = 0
        duplicate_count = 0
        replaced_count = 0
        skipped = 0
        import_entries = []
        existing_addresses = [x.address for x in self.entries if x.address]
        existing_names = [x.names for x in self.entries if x.names]
        for count, entry in enumerate(entries):
            if entry.address in ('0.0.0.0', '127.0.0.1'):
                if len(entry.names) > 1:
                    for name in entry.names:
                        if name in existing_names:
                            if not force:
                                skipped += 1
                                duplicate_count += 1
                                break
                            else:
                                self.remove_all_matching(name=name)
                                import_entries.append(entry)
                                break
                elif [entry.names[0]] in existing_names:
                    if not force:
                        duplicate_count += 1
                        skipped += 1
                        continue
                    else:
                        self.remove_all_matching(name=entry.names[0])
                        import_entries.append(entry)
                else:
                    import_entries.append(entry)
            elif entry.address in existing_addresses:
                if not force:
                    duplicate_count += 1
                    skipped += 1
                    continue
                elif force:
                    self.remove_all_matching(address=entry.address)
                    import_entries.append(entry)
            else:
                for name in entry.names:
                    for sublist in existing_names:
                        if name in sublist:
                            if not force:
                                duplicate_count += 1
                                skipped += 1
                                break
                            else:
                                self.remove_all_matching(name=name)
                                import_entries.append(entry)
                                break
                    # Else it's a new entry
                    else:
                        import_entries.append(entry)
                        break

        for item in import_entries:
            if not isinstance(item, HostsEntry):
                invalid_count += 1
                continue
            if item.entry_type == 'ipv4':
                ipv4_count += 1
                self.entries.append(item)
            elif item.entry_type == 'ipv6':
                ipv6_count += 1
                self.entries.append(item)
        return {'ipv4_count': ipv4_count,
                'ipv6_count': ipv6_count,
                'invalid_count': invalid_count,
                'duplicate_count': duplicate_count,
                'replaced_count': replaced_count}

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
                        stripped_name_list = []
                        for name in chunked_entry[1:]:
                            stripped_name_list.append(name.strip())

                        self.entries.append(
                            HostsEntry(
                                entry_type=entry_type,
                                address=chunked_entry[0].strip(),
                                names=stripped_name_list))
        except IOError:
                return {'result': 'failed',
                        'message': 'Cannot read: {0}.'.format(self.hosts_path)}
