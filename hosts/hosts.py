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

    def dedupe_entries(self):
        import hashlib
        existing_hashes = []
        deduped = []
        for entry in self.entries:
            if entry.entry_type in ('ipv4', 'ipv6'):
                entry_hash = hashlib.sha224("{}{}{}".format(entry.entry_type,
                                                            entry.address,
                                                            entry.names
                                                            )
                                            ).hexdigest()
                if entry_hash not in existing_hashes:
                    deduped.append(entry)
                    existing_hashes.append(entry_hash)
        self.entries = deduped

    def write(self):
        """
        Write the list of host entries back to the hosts file.
        """
        written_count = 0
        comments_written = 0
        blanks_written = 0
        ipv4_entries_written = 0
        ipv6_entries_written = 0
        if is_writeable(self.hosts_path):
            print "WRITING START"
            with open(self.hosts_path, 'w') as hosts_file:
                for written_count, line in enumerate(self.entries):
                    print "entry: {} {} {}".format(line.entry_type, line.address, line.names)
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
                print "END WRITING"
                print "comments_written {}".format(comments_written)
                print "blanks_written {}".format(blanks_written)
                print "ipv4_entries_written {}".format(ipv4_entries_written)
                print "ipv6_entries_written {}".format(ipv6_entries_written)
                return {'total_written': written_count+1,
                        'comments_written': comments_written,
                        'blanks_written': blanks_written,
                        'ipv4_entries_written': ipv4_entries_written,
                        'ipv6_entries_written': ipv6_entries_written}

    @staticmethod
    def get_hosts_by_url(url=None):
        response = urllib2.urlopen(url)
        return response.read()

    def import_url(self, url=None):
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
                import_entry = HostsEntry.str_to_hostentry(line)
                import_entries.append(import_entry)
        add_result = self.add(entries=import_entries)
        self.dedupe_entries()
        write_result = self.write()
        return {'result': 'success',
                'skipped': skipped,
                'add_result': add_result,
                'write_result': write_result}

    def import_file(self, import_file_path=None):
        skipped = 0
        if is_readable(import_file_path):
            import_entries = []
            with open(import_file_path, 'r') as infile:
                for entries_count, line in enumerate(infile):
                    stripped_entry = line.strip()
                    if (not stripped_entry) or (stripped_entry.startswith('#')):
                        skipped += 1
                    else:
                        import_entry = HostsEntry.str_to_hostentry(line)
                        import_entries.append(import_entry)
                add_result = self.add(entries=import_entries)
                self.dedupe_entries()
                write_result = self.write()
                return {'result': 'success',
                        'skipped': skipped,
                        'add_result': add_result,
                        'write_result': write_result}
        else:
            return {'result': 'failed',
                    'message': 'Cannot read: file {0}.'.format(import_file_path)}

    def exists(self, entry):
        address_matches = 0
        name_matches = 0
        for existing_entry in self.entries:
            if entry.entry_type == existing_entry.entry_type:
                if entry.address == existing_entry.address:
                    address_matches += 1
                if set(existing_entry.names).intersection(set(entry.names)):
                    name_matches += 1
        return {'address_matches': address_matches,
                'name_matches': name_matches}

    def remove_matching(self, entry):
        removed_count = 0
        entries_to_remove = []
        for existing_entry in self.entries:
            if entry.entry_type == existing_entry.entry_type:
                if entry.address == existing_entry.address:
                    self.entries.remove(existing_entry)
                    removed_count += 1
                    continue
                for name in entry.names:
                    if name in existing_entry.names:
                        entries_to_remove.append(existing_entry)
                        removed_count += 1
                        continue
        purged_list = [x for x in self.entries if x not in entries_to_remove]
        self.entries = purged_list
        return removed_count

    def add(self, entries=None, force=None):
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

        for count, item in enumerate(entries):
            if not isinstance(item, HostsEntry):
                invalid_count += 1
                continue
            if item.entry_type == 'ipv4':
                exists = self.exists(item)
                if (exists.get('name_matches')) and (item.address in ('0.0.0.0', '127.0.0.1')):
                    duplicate_count += 1
                    continue
                elif item.address in ('0.0.0.0', '127.0.0.1'):
                    ipv4_count += 1
                elif exists.get('address_matches') or exists.get('name_matches'):
                    if force:
                        replaced_count += self.remove_matching(item)
                        ipv4_count += 1
                    else:
                        duplicate_count += 1
                        continue
                else:
                    ipv4_count += 1
            elif item.entry_type == 'ipv6':
                exists_res = self.exists(item)
                if exists_res.get('address_matches') or exists_res.get('name_matches'):
                    if force:
                        replaced_count += self.remove_matching(item)
                        ipv6_count += 1
                    else:
                        duplicate_count += 1
                        continue
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
