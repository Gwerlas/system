Host names
==========

Hosts an domain name management.

Variables
---------

### Feature flipping

By default, hosts names management is disabled in a container to prevent
conflicts with the engine.

```yaml
system_manage_hosts: "{{ not in_container }}"
```

You can force enabling or disabling it defining the `system_manage_hosts` to `true` or `false`.

### Custom hosts names

Here are the defaults values :

```yaml
system_domain: localdomain
system_hostname: "{{ inventory_hostname }}"
system_hostnames: []
system_hosts: []
```

You can customize the system hostname by setting the `system_hostname` variable. By default, the inventory hostname is used.

If You need to add hosts aliases to the loopback interfaces in `/etc/hosts`, set them in the `system_hostnames` list. For exemple :

```yaml
system_hostnames:
  - webserver
  - www
```

Set your domain name throw the variable `system_domain`.

If your nodes need to resolve external custom hosts in `/etc/hosts`, You can set them in `system_hosts` list of dict :

```yaml
system_hosts:
  - ip: '10.0.0.7'
    names: ['host7']
```
