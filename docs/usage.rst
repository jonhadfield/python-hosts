Usage
=====

Basic operations
----------------

Create an instance of a hosts file (the default path for the current platform
is used when ``path`` is not supplied)::

    from python_hosts import Hosts, HostsEntry
    my_hosts = Hosts()

Add an entry::

    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['example.com', 'example'])
    my_hosts.add([new_entry])

Remove entries by address or name::

    my_hosts.remove_all_matching(address='1.2.3.4')
    my_hosts.remove_all_matching(name='example.com')

Write changes back to disk::

    my_hosts.write()

Additional features
-------------------

Import entries from a file or URL::

    my_hosts.import_file('extra_hosts')
    my_hosts.import_url('https://example.com/hosts')

Check if a host entry exists::

    my_hosts.exists(address='1.2.3.4')

Merge names with an existing entry while keeping the same address::

    new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['alias'])
    my_hosts.add([new_entry], merge_names=True)
