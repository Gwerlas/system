Firewall
========

Local firewall rules.

Variables
---------

Here are the defaults values :

```yaml
system_firewall_default_zone: public
system_firewall_log: true
system_firewall_public_interface: "{{ ansible_default_ipv4.interface }}"
system_firewall_rules: []
```

You can use one of [predefined zones](https://firewalld.org/documentation/zone/predefined-zones.html) as values.

The `system_firewall_default_zone` will be applied to the `system_firewall_public_interface`.

The `system_firewall_log` will log denied packets (default true).

The `system_firewall_rules` is a list of dictionaries with the same structure
documented in the [Ansible firewalld module][].

[Ansible firewalld module]: https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html

For some arguments, we changed the default values as is :

- `immediate`: `true`
- `permanent`: `true`
- `state`: `enabled`
- `zone`: `{{ system_firewall_default_zone }}`

Example Playbook
----------------

Common usage :

```yaml
---
- name: My wonderful playbook
  hosts: all
  roles:
    - name: gwerlas.system
        vars:
          system_firewall_rules:
            - service: http
```

