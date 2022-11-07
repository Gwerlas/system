Time
====

System clock management.

Variables
---------

### Feature flipping

By default, time management is disabled for containers.

```yaml
system_manage_time: "{{ 'container' not in ansible_virtualization_tech_guest }}"
```

You can force enabling or disabling it defining the `system_manage_time` to `true` or `false`.
