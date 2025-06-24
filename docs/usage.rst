Usage
=====
**Create an instance of a hosts file**::

 from python_hosts import Hosts, HostsEntry
 my_hosts = Hosts()

**Add an entry**::

 new_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4', names=['example.com', 'example'])
 my_hosts.add([new_entry])

**Remove an entry/entries matching an address**::

 my_hosts.remove_all_matching(address='1.2.3.4')

**Remove an entry/entries matching an address**::

 my_hosts.remove_all_matching(name='example.com')

**Write entries**::

 my_hosts.write()

**Import entries from a URL**::

 from python_hosts import Hosts
 my_hosts = Hosts(path='hosts_test')
 my_hosts.import_url(url='https://example.com/hosts')
 my_hosts.write()

**Import entries from another file**::

 from python_hosts import Hosts
 my_hosts = Hosts(path='hosts_test')
 my_hosts.import_file(import_file_path='other_hosts')
 my_hosts.write()
