Packages
========

Profile
-------

Currently for `server` nodes only. Desktops will be supported in future
developments.

Package manager cache
---------------------

For idempotence purpose, we only update package manager cache if missing.

Because there is a big risq of package installation failure if the cache is too old,
we update it if it is older than one week.

You can change the max age throw the `system_pkg_cache_max_age` variable.

**Be careful** because some distributions package managers (RedHat like for example)
could update their cache automatically or, at the opposit, could ignore some cache
update explicitly asked.

Packages update
---------------

The `system_package_update` set as `true` will update the system packages and reboot
the machine if needed.

If you have Waterfall or V-Cycle deployments, You should call it at first
deployment time or for whole system upgrades campains, then let it to `false`
at the other times to keep control on your infrastructure state.

For continuous deployments, You would like to set it permanently as `true`.

In case of Ansible role development, set it as `true` at preparation stage
only to keep idempotence control. Here an exemple of `molecule/default/prepare.yml` :

```yml
---
- name: Prepare
  hosts: all
  tasks:
    - name: Run gwerlas.system
      ansible.builtin.include_role:
        name: gwerlas.system
      vars:
        system_package_update: true
```

You can customize the system update reboot message throw the
`system_package_update_reboot_msg` variable.
