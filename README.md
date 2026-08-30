Base system
===========

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/system/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/system/-/commits/main)

Linux systems base settings.

Running roles in containers is not common, but this use case is supported for
Ansible testing with Molecule. When it detects a container, the role leaves to
the container engine what belongs to it : host names, firewall, clock, sudo,
sshd and reboots are not managed. Everything else still applies — package
managers, packages, users, CA certificates.

GitLab project: [yoanncolin/ansible/roles/system](https://gitlab.com/yoanncolin/ansible/roles/system)

Requirements
------------

This role has been written to be run as a non root user, so Sudo has to be
installed and configured. It requires ansible-core 2.19 or above.

For network configuration, the [`netaddr` Python package][netaddr] is
required, You also need the [`ansible.utils`][ansible.utils] Ansible
collection.

For filesystems management, the [`jmespath` Python package][jmespath] is
required, You also need the [`community.general`][community.general] and
[`ansible.posix`][ansible.posix] Ansible collections.

[jmespath]: https://jmespath.org/
[netaddr]: https://netaddr.readthedocs.io/en/latest/
[ansible.posix]: https://galaxy.ansible.com/ansible/posix
[ansible.utils]: https://galaxy.ansible.com/ansible/utils
[community.general]: https://galaxy.ansible.com/community/general

Facts
-----

Defined facts of this role :

- `system_boot_mode`
- `system_kernel`
- `system_mounts`
- `system_needs_reboot`
- `system_packages`
- `system_services`
- `system_shells`
- `system_uptime`

Look at the [facts][] documentation for more details.

Tags
----

Some values are dispatched in multiple tasks, so You can quickly update them
with tags :

- `ca` - SSL certificates authorities
- `firewall`
- `hosts` - Update `/etc/hosts` file
- `networks`
- `package-managers`
- `packages`
- `proxies`
- `remote-access`
- `ssh`
- `storages`
- `sudoers`
- `time`
- `users`

Usage :

```sh
ansible-playbook -t tag1[,tag2[,...]] my_play.yml
```

Tasks
-----

System components are managed through separated tasks that could be called
independently.

Of course, all tasks are called in the `main.yml`. See each task documentation :

- [facts][]
- [proxies][]
- [hosts][]
- [packages][]
- [modules][]
- [networks][]
- [storages][]
- [sudo][]
- [users][]
- [zsh][]
- [ca][]
- [time][]
- [firewall][]
- [remote-access][]
- [reboots][]

<!-- Absolute links on purpose: this file is also rendered on the Galaxy
     role page, outside of any repository, where a relative path resolves
     to nothing. -->
[facts]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/facts.md
[proxies]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/proxies.md
[hosts]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/hosts.md
[packages]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/packages.md
[modules]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/modules.md
[networks]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/networks.md
[storages]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/storages.md
[sudo]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/sudo.md
[users]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/users.md
[zsh]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/zsh.md
[ca]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/ca.md
[time]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/time.md
[firewall]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/firewall.md
[remote-access]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/remote-access.md
[reboots]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/reboots.md

Role Variables
--------------

### Feature flipping

Look at [`defaults/main/feature-flipping.yml`][ff].

Enable/disable some features by setting them to `true`/`false`.

[ff]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/defaults/main/feature-flipping.yml

### Tasks sequence

Some tasks may depend on another one. For example, storage and network
management may require the installation of packages, but packages are fetched
through the network and stored on disk.

You can change the installation sequence for your specific situation
defining the `system_sequence` variable.

Here is the default sequence :

```yaml
system_sequence:
  - modules
  - proxies
  - hosts
  - sudo
  - package-managers
  - packages
  - networks
  - storages
  - users
  - ca
  - time
  - firewall
  - remote-access
```

Note that the `facts` task is implicitly called by the other tasks if needed.

### Common variables

Look at [`defaults/main/common.yml`][common].

[common]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/defaults/main/common.yml

```yaml
system_scripts_path: /usr/local/bin
system_profile: server
system_retries: 2
```

Some tasks of this role need to put scripts. They are stored in the
`system_scripts_path` directory.

The `system_profile` can impact the behaviour of some parts of the system,
for example the packages to install (or not). It is a `/` separated path,
each segment adding to the ones before it :

| Segment    | What it adds                                                              |
| ---------- | ------------------------------------------------------------------------- |
| `server`   | nothing of its own — the default                                          |
| `desktop`  | LibreOffice, Firefox and `usbutils`, plus the Yay AUR helper on ArchLinux |
| `gnome`    | the GNOME session, its utilities and the `gdm` service                    |
| `hardened` | a [hardened sshd configuration][hardened], replacing the distribution one |

Whatever the profile, every node gets `acl`, `sudo` and `rsync`. The usual
combinations :

```yaml
system_profile: server                  # the default
system_profile: server/hardened
system_profile: desktop
system_profile: desktop/gnome
system_profile: desktop/gnome/hardened
```

A segment naming none of the profiles above brings nothing. It is ignored,
and said so in the play output rather than dropped silently :

```text
TASK [gwerlas.system : Facts - Report unknown system_profile segments] *****
[WARNING]: [node] system_profile segment(s) gnom match no known profile and
are ignored (available: desktop, gnome, hardened, server)
ok: [node]
```

[hardened]: https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/docs/remote-access.md#the-hardened-profile

If You have many download failures due to network troubles, you can increase
the `system_retries` value.

Dependencies
------------

A reachable Linux system with Python installed.

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

Using just one task :

```yaml
---
- name: Package managers
  hosts: all
  tasks:
    - name: Just get the package manager upready
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: package-managers
```

License
-------

[BSD 3-Clause License](https://gitlab.com/yoanncolin/ansible/roles/system/-/blob/main/LICENSE).
