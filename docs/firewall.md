Firewall
========

Local firewall rules.

Variables
---------

Here are the defaults values :

```yaml
system_firewall_default_zone: public
system_firewall_public_interface: "{{ ansible_default_ipv4.interface }}"
system_firewall_rules: []
```

You can use one of [predefined zones](https://firewalld.org/documentation/zone/predefined-zones.html) as values.

The `system_firewall_default_zone` will be applied to the `system_firewall_public_interface`.

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
            - http
```

