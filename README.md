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

For network configuration, the [`netaddr` Python package][netaddr] is
required, You also need the [`ansible.utils`][ansible.utils] Ansible module.

For filesystems management, the [`jmespath` Python package][jmespath] is
required, You also need the [`community.general`][community.general] and
[`ansible.posix`][ansible.posix] Ansible modules.

[jmespath]: https://jmespath.org/
[netaddr]: https://netaddr.readthedocs.io/en/latest/
[ansible.posix]: https://galaxy.ansible.com/ansible/posix
[ansible.utils]: https://galaxy.ansible.com/ansible/utils
[community.general]: https://galaxy.ansible.com/community/general

Facts
-----

Defined facts of this role :

- `system_packages`
- `system_shells`
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

System composents are managed through separated tasks that could be called
independently.

Of course, all tasks are called in the `main.yml`. See each task documentation :

* [proxies](docs/proxies.md)
* [hosts](docs/hosts.md)
* [packages](docs/packages.md)
* [networks](docs/networks.md)
* [storages](docs/storages.md)
* [sudo](docs/sudo.md)
* [users](docs/users.md)
* [zsh](docs/zsh.md)
* [ca](docs/ca.md)
* [time](docs/time.md)
* [firewall](docs/firewall.md)
* [reboot](docs/reboot.md)

Role Variables
--------------

### Feature flipping

Look at [`defaults/main/feature-flipping.yml`](defaults/main/feature-flipping.yml).

Enable/disable some features by setting them to `true`/`false`.

### Shared variables

Look at [`defaults/main/shared.yml`](defaults/main/shared.yml).

```yaml
system_bin_path: /usr/local/bin
system_profile: server
system_retries: 2
```

Some distributions does not provide command line to easily know if a reboot is
required, or if the packages cache is outdated. So we put scripts to do it.

You can change those scripts location through the `system_bin_path`.

The `system_profile` can impact the behaviour of some parts of the system,
for example the packages to install (or not).

If You have some network troubles during installation, you can increase the
`system_retries` value.

Dependencies
------------

None.

Example Playbook
----------------

First deployment or distribution upgrade, 10 steps rolling update :

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
- name: System packages
  hosts: all
  tasks:
    - name: Update the package manager cache
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: packages
```

License
-------

[BSD 3-Clause License](LICENSE).
