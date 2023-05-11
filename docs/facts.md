Facts
=====

Define the role facts :

- `system_packages`
- `system_shells`
- `system_sudo_version`

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
        ansible_os_family: Debian
        ansible_distribution: Debian
        ansible_distribution_major_version: "11"
        ansible_distribution_release: bullseye
        ansible_service_mgr: systemd
        ansible_pkg_mgr: apt
        ansible_virtualization_tech_guest: []
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: facts
```

Be sure to set accurate values !
