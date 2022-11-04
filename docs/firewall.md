Firewall
========

Local firewall rules.

Variables
---------

### Feature flipping

By defaults, firewalling is disabled for containers.

```yaml
system_manage_firewall: "{{ 'container' not in ansible_virtualization_tech_guest }}"
```

You can force enabling or disabling it defining the `system_manage_firewall` to `true` or `false`.

### Zones

Here are the defaults values :

```yaml
system_firewall_default_zone: public
```

You can use one of [predefined zones](https://firewalld.org/documentation/zone/predefined-zones.html) as value.
