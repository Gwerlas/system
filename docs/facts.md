Facts
=====

Define the role facts :

- `system_packages` : the packages expected to be installed, once the keys of
  `system_packages_add_by_key` have been resolved for the target distribution
- `system_services` : the services expected to be enabled, resolved the same way
- `system_shells` : the shells used by the users of `system_users`
- `system_mounts` : the filesystems to mount, derived from `system_storages_*`
- `system_kernel` : the running kernel version, without the distribution suffix
- `system_needs_reboot` : whether a reboot is pending

On a bare metal or virtualized node — the `not in_container` block — two more
are gathered :

- `system_boot_mode` : `efi` or `pc`
- `system_uptime` : the epoch of the last boot

`system_sudo_version` is *not* set here : it comes from the `sudo` task, which
reads it off the installed binary.

Usage
-----

The role facts are set though the `facts` task, You can get them without
changing the node :

```yaml
---
- name: Get facts
  hosts: all
  tasks:
    - name: System facts
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: facts
```

Dependencies
------------

Because some values depends on the Linux distribution, the Ansible facts must
be gathered.

But You can work around that defining the values by yourself if the node isn't
yet ready :

```yaml
---
- name: Get facts
  hosts: all
  gather_facts: false
  tasks:
    - name: System facts
      vars:
        ansible_facts:
          os_family: Debian
          distribution: Debian
          distribution_major_version: "11"
          distribution_release: bullseye
          service_mgr: systemd
          pkg_mgr: apt
          virtualization_tech_guest: []
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: facts
```

Be sure to set accurate values !
