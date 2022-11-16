Packages
========

Install system tools. Also for Gentoo configure the compilation profile.

Profile
-------

Available profiles :

- `desktop`
- `server`

Packages managers
-----------------

### Cache

For idempotence purpose, we only update package manager cache if missing.

Because there is a big risk of package installation failure if the cache is too old,
we update it if it is older than one week.

You can change the max age throw the `system_packages_cache_max_age` variable.

**Be careful** because some distributions package managers (RedHat like for example)
could update their cache automatically or, at the opposit, could ignore some cache
update explicitly asked.

### APT

You can customize the APT mirror like this :

```yaml
system_apt_default_mirror: ftp://ftp.fr.debian.org/debian/
```

Or completely customize the APT sources like this :

```yaml
system_apt_default_mirrors:
  - url: "ftp://my-apt-mirror"
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

### Portage

#### Cache directory

If your package manager is Portage (Gentoo based distros), You can change the
portage manifests directory (`PORTDIR`) with the `system_portage_directory` setting.

If the portage directory is changed, the old one will be removed. In this case, the
fact `system_portage_directory_initial` is set with the previous portage directory path.

#### System group

If the ansible user is not `root`, he will be added to the `portage` system group.

The portage configuration files and directories are writeable for this group.

#### Ansible dependencies

As explained in the [portage module documentation][], the `gentoolkit` package is
a dependency to make it work.

So, we install it if it's missing.

[portage module documentation]: https://docs.ansible.com/ansible/latest/collections/community/general/portage_module.html

Packages upgrade
---------------

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

Notes : Debian like distros only, at this day.
