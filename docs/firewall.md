Firewall
========

Local firewall rules.

Variables
---------

### Feature flipping

By default, firewall management is disabled in a container, where the chains
belong to the container engine.

```yaml
system_manage_firewall: "{{ not in_container }}"
```

You can force enabling or disabling it defining the `system_manage_firewall`
to `true` or `false`.

### Rules

Here are the defaults values :

```yaml
system_firewall_default_zone: public
system_firewall_log: false
system_firewall_public_interface: "{{ ansible_facts.default_ipv4.interface }}"

system_firewall_rules:
  - interface: "{{ system_firewall_public_interface }}"
    zone: "{{ system_firewall_default_zone }}"
    immediate: true
    permanent: true
    state: enabled
```

You can use one of [predefined zones][] as values.

The `system_firewall_default_zone` will be applied to the `system_firewall_public_interface`.

The `system_firewall_log` will log denied packets.

The `system_firewall_rules` is a list of dictionaries with the same structure
documented in the [Ansible firewalld module][].

> **Be careful**
>
> `system_firewall_rules` is not empty by default : its single entry is what
> binds `system_firewall_public_interface` to `system_firewall_default_zone`.
> Setting the variable replaces that entry instead of adding to it, so keep it
> in your own list unless you assign the interface to a zone yourself.

[Ansible firewalld module]: https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html

For some arguments, we changed the default values as is :

- `immediate`: `true`
- `permanent`: `true`
- `state`: `enabled`
- `zone`: `{{ system_firewall_default_zone }}`

Gentoo
------

On Gentoo, the role writes `/etc/kernel/config.d/firewalld.config` to make
sure nftables and conntrack stay enabled in the next dist-kernel build. The
fragment is merged on top of the upstream default config by `installkernel`,
so any later `emerge sys-kernel/gentoo-kernel` produces a kernel that still
supports firewalld.

Example Playbook
----------------

Common usage :

```yaml
---
- name: My wonderful playbook
  hosts: all
  roles:
    - role: gwerlas.system
      vars:
        system_firewall_rules:
          - interface: "{{ system_firewall_public_interface }}"
            zone: "{{ system_firewall_default_zone }}"
          - service: http
```

[predefined zones]: https://firewalld.org/documentation/zone/predefined-zones.html
