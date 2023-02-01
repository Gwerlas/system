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

For network configuration, the `netaddr` python package is required.

Facts
-----

Defined facts of this role :

- `system_packages_computed`
- `system_portage_directory_initial`
- `system_sudo_version`

Tags
----

Because some values are dispatched in multiple tasks. You can quickly update some of them with tags :

- `proxies`
- `sudoers`
- `users`

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
* [users](docs/users.md)
* [zsh](docs/zsh.md)
* [ca](docs/ca.md)
* [network](docs/network.md)
* [time](docs/time.md)

Role Variables
--------------

Look at [`defaults/main.yml`](defaults/main.yml).

### Feature flipping

```yaml
system_manage_sudo: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_manage_hosts: false
system_manage_proxies: "{{ system_http_proxy is defined or system_https_proxy is defined or system_ftp_proxy is defined }}"
system_manage_networks: false
system_manage_timesync: "{{ 'container' not in ansible_virtualization_tech_guest }}"
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
    - role: gwerlas.system
      vars:
        system_packages_upgrade: true
```

Distribution update, 10 steps rolling update :

```yaml
---
- name: Rolling update
  hosts: all
  serial: 10%
  roles:
    - role: gwerlas.system
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
        tasks_from: packages
```

Use the legacy `ntp` package for time synchronisation, and a list of custom
NTP servers :

```yaml
---
- name: NTPd
  hosts: all
  roles:
    - name: gwerlas.system
      vars:
        system_time_backend: ntp
        system_time_servers:
          - 0.fr.pool.ntp.org
          - 1.fr.pool.ntp.org
          - 2.fr.pool.ntp.org
          - 3.fr.pool.ntp.org
```

License
-------

[BSD 3-Clause License](LICENSE).
