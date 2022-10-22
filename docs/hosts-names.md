Host names
==========

Hosts an domain name management.

Variables
---------

### Feature flipping

By default, hosts names management is disabled for containers.

```yaml
system_manage_hosts_names: "{{ 'container' not in ansible_virtualization_tech_guest }}"
```

You can force enabling or disabling throw defining the `system_manage_hosts_names` to `true` or `false`.

### Custom hosts names

```yaml
system_domainname: localdomain
system_hostname: "{{ inventory_hostname }}"
system_hostname_aliases: []
system_custom_hosts: []
```

You can customize the system hostname by setting the `system_hostname` variable. By default, the inventory hostname is used.

If You need to add hosts aliases to the loopback interfaces in `/etc/hosts`, set them in the `system_hostname_aliases` list. For exemple :

```yaml
system_hostname_aliases:
  - webserver
  - www
```

Set your domain name throw the variable `system_domainname`.

If your nodes need to resolve external custom hosts in `/etc/hosts`, You can set them in `system_custom_hosts` list of dict :

```yaml
system_custom_hosts:
  - ip: '10.0.0.7'
    names: ['host7']
```
