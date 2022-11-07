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

Facts
-----

Defined facts of this role :

- `system_portage_directory_initial`
- `system_sudo_version`

Tags
----

Because some values are dispatched in multiple tasks. You can quickly update some of them with tags :

- `proxies`
- `sudoers`

Usage :

```sh
ansible-playbook -t tag1[,tag2[,...]] my_play.yml
```

Tasks
-----

System composents are managed throw separated tasks that could be called independently.

Of course, all tasks are ran throw the `main.yml`. See each task documentation :

* [sudo](docs/sudo.md)
* [hosts](docs/hosts.md)
* [proxies](docs/proxies.md)
* [packages](docs/packages.md)
* [reboot](docs/reboot.md)
* [time](docs/time.md)
* [users](docs/users.md)
* [firewall](docs/firewall.md)

Role Variables
--------------

Look at [`defaults/main.yml`](defaults/main.yml).

### Feature flipping

```yaml
system_manage_sudo: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_manage_hosts: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_manage_proxies: "{{ system_http_proxy is defined or system_https_proxy is defined or system_ftp_proxy is defined }}"
system_manage_time: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_manage_firewall: "{{ 'container' not in ansible_virtualization_tech_guest }}"
```

Enable/disable some features by setting them to `true`/`false`.

### Shared variables

```yaml
system_bin_path: /usr/local/bin
system_profile: server
system_retries: 2
```

Some distributions does not provide command line to easily know if a reboot is
required, or if the packages cache is outdated. So we put scripts to do it.

You can change those scripts location throw the `system_bin_path`.

The `system_profile` can impact the behaviour of some parts of the system,
for example the packages to install (or not).

If You have some network troubles during installation, you can increase the
`system_retries` value.

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
        system_packages_upgrade: true
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
        system_packages_upgrade: true
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
