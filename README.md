Base system
===========

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/system/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/system/-/commits/main)

Linux systems base settings.

Running roles in containers is not common, but this use case is supported for
Ansible testing with Molecule. In this case, just the package manager cache
will be configured and updated if needed, the other system component will be
not managed since it is the reponsibility of the container engine.

GitLab project: [yoanncolin/ansible/roles/system](https://gitlab.com/yoanncolin/ansible/roles/system)

Requirements
------------

This role as been writen to be run as non root user, so Sudo has to be installed and configured.

Tasks
-----

System composents are managed throw separated tasks that could be called independently.

Of course, all tasks are ran throw the `main.yml`. See each task documentation :

* [hosts-names](docs/hosts-names.md)
* [packages](docs/packages.md)
* [reboot](docs/reboot.md)
* [zsh](docs/zsh.md)
* [firewall](docs/firewall.md)

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
system_manage_hosts_names: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_domainname: localdomain
system_hostname: "{{ inventory_hostname }}"
system_hostname_aliases: []
system_custom_hosts: []

system_update: false
system_update_reboot_msg: Reboot initiated by Ansible after a distribution update

system_profile: server

system_archlinux_user_repository: "{{ system_profile != 'server' }}"
system_portage_directory: /var/db/repos/gentoo

system_install_zsh: false

system_firewall_managed: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_firewall_default_zone: public

system_ca_certificates: []
```

Dependencies
------------

None.

Example Playbook
----------------

First deployment :

```yaml
---
- name: System preparation
  hosts: all
  roles:
    - name: gwerlas.system
      vars:
        system_update: true
```

Distribution update, rolling update by ~10% slices :

```yaml
---
- name: Rolling update
  hosts: all
  serial: (hostvars | length / 10) | round(0, 'ceil') | int
  roles:
    - name: gwerlas.system
      vars:
        system_update: true
```

Use just one task :

```yaml
---
- name: Firewalling
  hosts: all
  tasks:
    - name: Update the package manager cache
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: update
    - name: Firewalling
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: firewall
        vars:
          rules:
            - http
```

License
-------

[BSD 3-Clause License](LICENSE).
