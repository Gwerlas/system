Host names
==========

Hosts an domain name management.

Variables
---------

### Feature flipping

By default, hosts names management is disabled.

```yaml
system_manage_hosts: false
```

You can enable it defining the `system_manage_hosts` to `true`.

### Custom hosts names

Here are the defaults values :

```yaml
system_hosts_domain: localdomain
system_hosts_localhost: "{{ inventory_hostname }}"
system_hosts_localhost_aliases: []
system_hosts_custom: []
```

You can customize the system hostname by setting the `system_hosts_localhost` variable. By default, the inventory hostname is used.

If You need to add hosts aliases to the loopback interfaces in `/etc/hosts`, set them in the `system_hosts_localhost_aliases` list. For exemple :

```yaml
system_hosts_localhost_aliases:
  - webserver
  - www
```

Set your domain name throw the variable `system_hosts_domain`.

If your nodes need to resolve external custom hosts in `/etc/hosts`, You can set them in `system_hosts_custom` list of dict :

```yaml
system_hosts_custom:
  - ip: '10.0.0.7'
    names: ['host7']
```
