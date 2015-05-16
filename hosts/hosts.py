__author__ = 'Jon Hadfield'
import sys
import socket


class HostsEntry(object):
    def __init__(self, entry_type=None, address=None, comment=None, names=None):
        self.entry_type = entry_type
        self.address = address
        self.comment = comment
        self.names = names


class Hosts(object):
    def __init__(self, path=None):
        platform = sys.platform
        if path:
            self.hosts_path = path
        elif 'linux' in platform or 'darwin' == platform:
            self.hosts_path = '/etc/hosts'
        elif any(platform == 'win32', platform == 'windows'):
            self.hosts_path = r'c:\windows\system32\drivers\etc\hosts'
        else:
            exit("cannot determine platform")
        self.entries = []
        self.populate_entries()


    @staticmethod
    def is_ipv4(entry):
        try:
            if socket.inet_aton(entry):
                return True
        except socket.error:
            return False

    @staticmethod
    def is_ipv6(entry):
        try:
            if socket.inet_pton(socket.AF_INET6, entry):
                return True
        except socket.error:
            return False

    def write(self):
        with open(self.hosts_path, 'w') as hosts_file:
            for line in self.entries:
                if line.entry_type == 'comment':
                    hosts_file.write(line.comment)
                if line.entry_type == 'blank':
                    hosts_file.write("\n")
                if line.entry_type == 'ipv4':
                    hosts_file.write(
                        "{}\t{}\n".format(
                            line.address,
                            ' '.join(line.names),
                        )
                    )
                if line.entry_type == 'ipv6':
                    hosts_file.write(
                        "{}\t{}\n".format(
                            line.address,
                            ' '.join(line.names),
                        )
                    )

    def add(self, entry_type, address=None,
            names=None, comment=None, force=False):
        entry = HostsEntry(entry_type=entry_type,
                           address=address, names=names, comment=comment)
        if entry.entry_type == "comment":
            existing = self.count(
                comment=entry.comment
            ).get('num_comment_matches')
            if existing:
                return False
        elif entry_type == "ipv4" or entry_type == "ipv6":
            existing = self.count(address=entry.address,
                                  names=entry.names)
            existing_addresses = existing.get('num_address_matches')
            existing_names = existing.get('num_name_matches')
            if not force and (existing_addresses or existing_names):
                return False
            elif force:
                self.remove(address=address, passed_names=names)
        self.entries.append(entry)
        self.write()

    def count(self, address=None, names=None, comment=None):
        num_address_matches = 0
        num_name_matches = 0
        num_comment_matches = 0
        for host in self.entries:
            existing_names = host.names
            existing_host_address = host.address
            existing_comment = host.comment
            if host.entry_type == "ipv4" or host.entry_type == "ipv6":
                if all((existing_names, names)) and \
                        set(names).intersection(existing_names):
                    print existing_names
                    num_name_matches += 1
                if existing_host_address and existing_host_address == address:
                    print existing_host_address
                    num_address_matches += 1
            if host.entry_type == "comment":
                if existing_comment == comment:
                    num_comment_matches += 1
        return {'address_matches':num_address_matches,
                'name_matches':num_name_matches,
                'comment_matches':num_comment_matches}

    def remove(self, address=None, passed_names=None, comment=None):
        removed = 0
        removal_list = []
        for entry in self.entries:
            names_inter = []
            if entry.names and passed_names:
                names_inter = set(entry.names).intersection(passed_names)
            if any((entry.comment == comment, entry.address == address, entry.names == passed_names, names_inter)):
                removal_list.append(entry)
                removed += 1
        for entry_to_remove in removal_list:
            self.entries.remove(entry_to_remove)
        if removed > 0:
            return True
        return False

    def get_entry_type(self, hosts_entry):
        if hosts_entry[0] == "#":
            return 'comment'
        if hosts_entry[0] == "\n":
            return 'blank'
        entry_chunks = hosts_entry.split()
        if self.is_ipv4(entry_chunks[0]):
            return "ipv4"
        if self.is_ipv6(entry_chunks[0]):
            return "ipv6"
        else:
            return False

    def populate_entries(self):
        with open(self.hosts_path, 'r') as hosts_file:
            hosts_entries = [line for line in hosts_file]
            for hosts_entry in hosts_entries:
                entry_type = self.get_entry_type(hosts_entry)
                if entry_type == "comment":
                    self.entries.append(HostsEntry(entry_type="comment", comment=hosts_entry))
                if entry_type == "blank":
                    self.entries.append(HostsEntry(entry_type="blank"))
                if entry_type == "ipv4" or entry_type == "ipv6":
                    chunked_entry = hosts_entry.split()
                    self.entries.append(HostsEntry(entry_type=entry_type, address=chunked_entry[0], names=chunked_entry[1:]))
        return



