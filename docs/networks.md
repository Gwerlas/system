Network interfaces
==================

> **Experimental**
>
> Interface configuration is written through a per-backend template. Backends
> with one are `ifupdown` (Debian like), `redhat` (EL like) and `systemd`
> (systemd-networkd). Gentoo goes through `netifrc`, which has its own task
> file.

Configure network interfaces.

Variables
---------

### Feature flipping

By default, networks are managed as soon as you declare at least one
interface — otherwise they are left to DHCP and/or your provisionner (foreman,
cobbler, cloud-init, etc.).

```yaml
system_manage_networks: "{{ system_networks_interfaces | length > 0 }}"
```

You can force enabling or disabling it defining the `system_manage_networks`
to `true` or `false`.

### Interfaces

```yaml
system_networks_check_mode: files
system_networks_restart_handler: reboot
system_networks_interfaces: []
system_networks_interfaces_prune: true
system_networks_disable_ipv6: false
```

The `system_networks_interfaces_prune` removes the interface configuration
files this role does not manage, so the declared list is the whole truth.

The `system_networks_disable_ipv6` set to `true` sets the
`net.ipv6.conf.all.disable_ipv6` sysctl. Unlike the rest of this page it
applies whatever `system_manage_networks` is worth.

The `system_networks_check_mode` set to `facts` will skip the network
configuration if the interface is present in the Ansible facts.

This mode is faster than `files`, but configuration changes won't be applied.

### Restart mode

```yaml
system_networks_restart_handler: reboot
```

What applies an interface change once the configuration files are written:

- `reboot`, the default, and the only value that also applies whatever else
  the run changed;
- `restart network service` restarts the backend's service alone, for a host
  you would rather not reboot. Connectivity drops while it restarts;
- `skip` leaves the running configuration as it is, for you to apply the files
  when you choose.

Examples
--------

Static network configuration :

```yaml
- name: One static configured ethernet interface
  hosts: my-node
  vars:
    system_networks_interfaces:
      - name: eth0
        ip: 192.168.1.7
        gateway: 192.168.1.254
        type: Ethernet
        onboot: true
        bootproto: static
  roles:
    - role: gwerlas.system
```
