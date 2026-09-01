Network interfaces
==================

> **Experimental**
>
> A backend is named after the configuration format it writes, and the role
> follows the one the host already runs. Implemented so far: `eni`
> (`/etc/network/interfaces.d`), `keyfile`
> (`/etc/NetworkManager/system-connections`), `sysconfig`
> (`/etc/sysconfig/network-scripts`), `netplan` (`/etc/netplan`), `networkd`
> (`/etc/systemd/network`) and `netifrc` (`/etc/conf.d/net`, which has its own
> task file rather than a template).
>
> A host configured through none of them is reported and left alone, rather
> than guessed at. Name the backend with `system_network_backend` to manage it
> anyway.

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
system_network_backend: auto
system_networks_check_mode: files
system_networks_restart_handler: reboot
system_networks_interfaces: []
system_networks_disable_ipv6: false
```

The role configures the interfaces you declare and leaves every other
configuration file alone, whoever wrote it.

The one exception is `eni`, which writes one file per interface under
`/etc/network/interfaces.d` — a directory ifupdown reads only if
`/etc/network/interfaces` includes it. So the role adds that include to your
`/etc/network/interfaces`, and the loopback declaration if the file has to be
created, and touches nothing else in it.

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

Migrating from 0.20 and earlier
-------------------------------

### `system_networks_interfaces_prune` is gone

The role used to delete, by default, every interface configuration file it had
not written — including the one your image's provisioner had put there. It no
longer does, and there is no way to ask it to: an inventory still carrying the
variable stops the run with a message rather than quietly changing behaviour.

What you get now is what `system_networks_interfaces_prune: false` used to
give. If you relied on the sweep, remove the unwanted files yourself, once,
with `ansible.builtin.file`.

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
