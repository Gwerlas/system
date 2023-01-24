Network interfaces
==================

> ** Experimental **
>
> Work on EL and Debian based ditros for now.

Configure network interfaces.

Variables
---------

### Feature flipping

By default, networks should be managed by DHCP and/or your provisionner (foreman, cobbler, cloud-init, etc.).

```yaml
system_manage_networks: false
```

To enable network management set `system_manage_networks` to `true`.

### Network interfaces

```yaml
system_networks_restart_handler: reboot
system_networks_interfaces: []
system_networks_interfaces_prune: true
```

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
