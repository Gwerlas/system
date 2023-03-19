Packages
========

Install system tools. Also for Gentoo configure the compilation profile.

Variables
---------

```yaml
system_packages_upgrade: false
system_packages_upgrade_unattended: false
system_packages_cache_age: 7
system_packages: []
```

Facts
-----

The `system_packages_computed` fact contains the list of packages expected
to be installed.

Profile
-------

Available profiles :

- `desktop`
- `server` (default)

Packages managers
-----------------

### Cache

For idempotence purpose, we only update package manager cache if missing.

Because there is a big risk of package installation failure if the cache is too old,
we update it if it is older than one week.

You can change the max age throw the `system_packages_cache_max_age` variable.

**Be careful** some distributions package managers (RedHat like for example)
could update their cache automatically or, at the opposit, could ignore some cache
update explicitly asked.

### APT

You can customize the APT mirror like this :

```yaml
system_apt_mirror: ftp://ftp.fr.debian.org/debian/
```

Or completely customize the APT sources like this :

```yaml
system_apt_mirrors:
  - url: ftp://my-apt-mirror
    branches:
      - debian
      - debian-security
    sections:
      - main
      - contrib
```

The generated `/etc/apt/sources.list` will be :

```
deb ftp://my-apt-mirror debian main contrib
deb ftp://my-apt-mirror debian-security main contrib
```

### AUR (Archlinux User Repository)

If your package manager is Pacman (ArchLinux based distros), we add the [Yay][]
AUR helper for desktop nodes.

You can force enable / disable setting the `system_archlinux_user_repository` to
`true` or `false`.

[Yay]: https://github.com/Jguer/yay/blob/next/README.md

### EPEL (Extra Packages for Enterprise Linux)

The Extra Packages for Enterprise Linux are enabled by default.

You can disable it by setting the `system_el_use_epel` variable to `false`.

> **Warning**
>
> If You disable EPEL repositories, some features, like bridging or time
> synchronization won't work since `bridge-utils` and `systemd-timesync`
> packages are in.

### Portage

#### Cache directory

If your package manager is Portage (Gentoo based distros), You can change the
portage manifests directory (`PORTDIR`) with the `system_portage_directory` setting.

#### System group

If the ansible user is not `root`, he will be added to the `portage` system group.

The portage configuration files and directories are writeables for this group.

#### Ansible dependencies

As explained in the [portage module documentation][], the `gentoolkit` package is
a dependency to make it work.

So, we install it if it's missing.

[portage module documentation]: https://docs.ansible.com/ansible/latest/collections/community/general/portage_module.html

Packages upgrade
----------------

The `system_packages_upgrade` set to `true` will upgrade the system packages and reboot
the machine if needed.

If you have Waterfall or V-Cycle deployments, You should call it at first
deployment time or for whole system upgrades campains, then let it to `false`
at the other times to keep control on your infrastructure state.

For continuous deployments, You would like to set it permanently to `true`.

In case of Ansible role development, set it to `true` at preparation stage
only to keep idempotence control. Here an exemple of `molecule/default/prepare.yml` :

```yml
---
- name: Prepare
  hosts: all
  tasks:
    - name: Run gwerlas.system
      ansible.builtin.include_role:
        name: gwerlas.system
        tasks_from: packages
      vars:
        system_packages_upgrade: true
```

Unattended upgrade
------------------

The `system_packages_upgrade_unattended` set to `true` will plan your node to be
silently upgraded every nights.

This feature is experimental, it is not yet possible to configure the service
through this role, You have to do it yourself.

Supported distros at this time :

- Debian like
- RedHat like version 8 or upper

Static package list
-------------------

You can install a list of packages through the `system_packages` variable.

This list won't be computed, so You have to give the real package name for the
target Linux distribution.

Dynamic package list
--------------------

Some packages will be dynamically enabled depending of the given data.

### User shells

The user shells will be automatically added to the package list.

The example will automatically add `zsh` to the list of packages to install on the node :

```yaml
---
- name: My Zsh user
  hosts: all
  tasks:
    - name: Include gwerlas.system
      ansible.builtin.include_role:
        name: gwerlas.system
        tasks_from: users
      vars:
        system_users:
          - name: jane
            shell: /bin/zsh

```

## CA certificates

The CA package will be automatically added to the package list
if at least one CA certificate file is given in the
`system_ca_certificates` variable.

## Network types

If you manage your networks interfaces with this role, we try to install the
required packages to the system.
