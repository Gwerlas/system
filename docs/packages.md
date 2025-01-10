Packages <!-- omit in toc -->
========

Install system tools. Also for Gentoo configure the compilation profile.

Table of content :

- [Variables](#variables)
- [Facts](#facts)
- [Profile](#profile)
- [Packages managers](#packages-managers)
  - [Cache](#cache)
  - [APT](#apt)
    - [Sources list](#sources-list)
    - [Backports](#backports)
  - [Pacman](#pacman)
    - [Packages installation](#packages-installation)
    - [AUR (Archlinux User Repository)](#aur-archlinux-user-repository)
  - [RedHat like package managers](#redhat-like-package-managers)
  - [Portage](#portage)
    - [Cache directories](#cache-directories)
      - [Repositories](#repositories)
      - [Repositories of binaries](#repositories-of-binaries)
      - [PORTDIR](#portdir)
    - [System group](#system-group)
    - [Ansible dependencies](#ansible-dependencies)
    - [Compilation settings](#compilation-settings)
    - [Kernel](#kernel)
- [Packages upgrade](#packages-upgrade)
- [Unattended upgrade](#unattended-upgrade)
- [Static package lists](#static-package-lists)
  - [By key](#by-key)
  - [By name](#by-name)
- [Dynamic package list](#dynamic-package-list)
  - [User shells](#user-shells)
- [CA certificates](#ca-certificates)
- [Network types](#network-types)


Variables
---------

```yaml
system_packages_upgrade: false
system_packages_upgrade_unattended: false
system_packages_cache_age: 7

system_packages_add_by_key: []
system_packages_add_by_name: []
```

See [Packages upgrade][] and [Static package lists][] for more informations
about these two groups of variables.

[Packages upgrade]: #packages-upgrade
[Static package lists]: #static-package-lists

Facts
-----

The `system_packages` fact contains the list of packages expected
to be installed.

Profile
-------

Available profiles :

- `desktop`
- `desktop/gnome`
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

**Notice:** APT sources list management has completly been rewriten in v0.12.

```yaml
system_apt_conf_proxy_path: /etc/apt/apt.conf.d/01proxy
system_apt_sources_list: []
system_apt_prefer_backports: false
```

#### Sources list

If the `system_apt_sources_list` is empty, the APT configuration files will be
let unchanged.

The given list is converted to one-line-style entries of [sources.list(5)][].

[sources.list(5)]: https://manpages.debian.org/stretch/apt/sources.list.5.en.html

Here is an example of sources list using the official main server :

```yaml
system_apt_sources_list:
  - uri: http://deb.debian.org/debian
    suites:
      - "{{ ansible_distribution_release }}"
      - "{{ ansible_distribution_release }}-updates"
      - "{{ ansible_distribution_release }}-backports"
    components:
      - main
  - uri: http://deb.debian.org/debian-security
    suites:
      - "{{ ansible_distribution_release }}{{ '-security' if ansible_distribution_major_version >= '11' else '' }}/updates"
    components:
      - main
```

Of course, You can use your own mirror. To disable/change the proxy you can
use the `proxy` property like this :

```yaml
system_apt_sources_list:
  - uri: ftp://my-apt-mirror/debian
    suites:
      - "{{ ansible_distribution_release | lower }}"
      - "{{ ansible_distribution_release | lower }}-security"
    components:
      - main
      - contrib
    proxy: direct     # Do not use any proxy
  - uri: http://my-another-mirror/debian
    suites:
      - "{{ ansible_distribution_release | lower }}"
      - "{{ ansible_distribution_release | lower }}-security"
    components:
      - main
      - contrib
    proxy: http://proxy.my-company.tld:3128
```

For Debian bookworm, the generated `/etc/apt/sources.list` will be :

```
deb ftp://my-apt-mirror/debian bookworm main contrib
deb ftp://my-apt-mirror/debian bookworm-security main contrib
deb http://my-another-mirror/debian bookworm main contrib
deb http://my-another-mirror/debian bookworm-security main contrib
```

And the `/etc/apt/apt.conf.d/01proxy` will be :

```
Acquire::ftp::Proxy::my-apt-mirror DIRECT;
Acquire::http::Proxy::my-another-mirror "http://proxy.my-company.tld:3128";
```

You can change the name of the proxy configuration file through the
`system_apt_conf_proxy_path` variable. Ensure to set the full absolute
path, here is an example :

```yaml
system_apt_conf_proxy_path: /etc/apt/apt.conf.d/99proxy
```

If You specify a `name`, we will set the line in a seperate file in
`/etc/apt/sources.list.d`. For example :

```yaml
system_apt_sources_list:
  - name: my-mirror
    uri: ftp://my-apt-mirror/debian
    suites:
      - "{{ ansible_distribution_release | lower }}"
    components:
      - main
      - contrib
```

The generated file will be `/etc/apt/sources.list.d/my-mirror`.

#### Backports

The `system_apt_prefer_backports` variable configure APT pinning to prioritize backports.

The possible values are :
  - `true` : Prefer backports (the repo has to be set in your apt sources.list)
  - `false` : Do nothing (default)
  - `auto` : Prefer backports if present in sources.list

The entire distribution will be upgraded with backports.

> **Warning**
>
> If `systemd-timesynd` or `firewalld` is used in Debian Buster, we force APT
> pinning to use backports packages.

### Pacman

#### Packages installation

As describe in the Pacman documentation :

When installing packages in Arch, avoid refreshing the package list without
upgrading the system (for example, when a package is no longer found in the
official repositories). In practice, do not run pacman -Sy package_name
instead of pacman -Syu package_name, as this could lead to dependency issues.

https://wiki.archlinux.org/title/pacman#Installing_packages


Because using `-u` can break idempotence, we try to install packages without
this flag, but if it fails, we fallback to the `pacman -Syu` method.

#### AUR (Archlinux User Repository)

```yaml
system_pacman_aur: "{{ system_profile != 'server' }}"
```

We add the [Yay][] AUR helper for desktop nodes.

Setting the `system_pacman_aur` to `true` or `false`, You will force
enable / disable it.

[Yay]: https://github.com/Jguer/yay/blob/next/README.md

### RedHat like package managers

Require the Ansible collection `community.general` v8.2 or above.

```yaml
system_el_epel: false
system_el_epel_next: false
system_el_repos: []
```

`system_el_epel` and `system_el_epel_next` are an easy way to enable EPEL.

> **Warning**
>
> Do not set `system_el_epel*` variables to `true` and manage your repositories
> with `system_el_repos` at the same time, you may have breakages or, at least,
> idempotencies issues.
>
> In this case, just enable epel in the appropriate entry of `system_el_repos`.
>
> For RedHat 8 like distros, when `system_el_repos` is empty **AND** the
> time backend is `timesyncd`, EPEL repo will be activated to be able to
> install `systemd-timesynd`.

Each repository in `system_el_repos` represents a file in `/etc/yum.repos.d` and
must contains `name` and `repositories` properties inside.

For each repository item :

- The `id` parameter is used to define the title of the `[section]`.
  If it's missing, we remove variables and slugify the `name` of the repository.

- The `name` parameter looks like a little description, but is required.
  If it's missing, we use the `id` instead.

- If neither `id`, neither `name` are given, we generate them from the file name.

- Boolean values are converted to `0` and `1` as describe in [yum.conf(5)][].

For example :

```yaml
system_el_repos:
  - name: almalinux-crb
    repositories:
      - id: crb
        name: AlmaLinux $releasever - CRB
        baseurl: https://mirror.my-company.tld/almalinux/$releasever/CRB/Source/
        enabled: true
        gpgcheck: false
  - name: almalinux-baseos
    repositories:
      - id: baseos
        name: AlmaLinux $releasever - BaseOS
        baseurl: https://mirror.my-company.tld/almalinux/$releasever/BaseOS/$basearch/os/
        enabled: 1
        gpgcheck: 0
      - name: AlmaLinux $releasever - BaseOS - Debug
        baseurl: https://repo.almalinux.org/vault/$releasever/BaseOS/debug/$basearch/
        enabled: '0'
        gpgcheck: '1'
        gpgkey: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-$releasever
```

This two files will be created :

```sh
$ cat /etc/yum.repos.d/almalinux-crb.repo
[crb]
name=crb
baseurl=https://mirror.my-company.tld/almalinux/$releasever/CRB/Source/
enabled=1
gpgcheck=0

$ cat /etc/yum.repos.d/almalinux-baseos.repo
[baseos]
name=AlmaLinux $releasever - BaseOS
baseurl=https://mirror.my-company.tld/almalinux/$releasever/BaseOS/$basearch/os/
enabled=1
gpgcheck=0

[almalinux-baseos-debug]
name=AlmaLinux $releasever - BaseOS - Debug
baseurl=https://repo.almalinux.org/vault/$releasever/BaseOS/debug/$basearch/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-$releasever
```

Look at the chapter `[repository] options` in the [yum.conf(5)][] manual page for more
informations about available options their values and meanings.

[yum.conf(5)]: https://linux.die.net/man/5/yum.conf

> **Important**
>
> The`id` and the `name` parameters are very importants for each repositories,
> please filled both of them.
>
> The package manager can throw errors for some bad `id`. Do not use random values.

### Portage

Portage is the package manager of the Gentoo based distros.

#### Cache directories

```yaml
system_portage_repos_directory: /var/db/repos

system_portage_binrepos: []
system_portage_repos: []
```

You can change the location of your repositories through `system_portage_repos_directory`.

Each entries of `system_portage_repos` and `system_portage_binrepos` result in
a configuration file in `/etc/portage/repos.conf/` and
`/etc/portage/binrepos.conf/` respectively.

##### Repositories

The supported keys and values are the same as described in the [repos.conf][]
documentation using those defaults values per entry :

- `location`: `system_portage_repos_directory`/`repo.name`
- `sync-type`: `git`
- `sync-uri`: https://github.com/gentoo-mirror/`name`.git

Only the `name` is mandatory. For example :

```yaml
system_portage_repos:
  - name: guru
```

Will generate the `/etc/portage/repos.conf/guru.conf` file as is :

```ini
[guru]
location = /var/db/repos/guru
sync-type = git
sync-uri = https://github.com/gentoo-mirror/guru.git
```

[repos.conf]: https://wiki.gentoo.org/wiki//etc/portage/repos.conf

##### Repositories of binaries

The supported keys and values are the same as described in the [binrepos.conf][]
documentation. For example :

```yaml
system_portage_binrepos:
  - name: binhost
    priority: 9999
    sync-uri: https://mirror.bytemark.co.uk/gentoo/releases/amd64/binpackages/23.0/x86-64/
```

Will generate the `/etc/portage/binrepos.conf/binhost.conf` file as is :

```ini
[binhost]
priority = 9999
sync-uri = https://mirror.bytemark.co.uk/gentoo/releases/amd64/binpackages/23.0/x86-64/
```

[binrepos.conf]: https://wiki.gentoo.org/wiki//etc/portage/binrepos.conf

##### PORTDIR

```yaml
# /var/db/repos/gentoo by default for Gentoo
system_portage_directory: "{{ system_portage_repos_directory }}/{{ ansible_distribution | lower }}"
```

The goal of this role is to manage systems easily, respecting the spirit of
each distribution and the user's choices.

We had to make an exception with the `PORTDIR` setting of
`/etc/portage/make.conf` removing it.

If `PORTDIR` was previously set, we move the data to `system_portage_directory`
if their values are different.

For a while, this variable permitted to set another location to the
portage metadatas and took `/usr/portage` for default value.
Now, Portage can manage multiple repositories and give its configuration
in `/etc/portage/repos.conf/gentoo.conf`.

If `/etc/portage/repos.conf/gentoo.conf` doesn't exist, portage will
take its default configuration from `/usr/share/portage/config/repos.conf`.

Since the default value as changed as of 2019-04-29 and later, and
to prevent emerge failures, we replace both of the old and the new default
location by a symlink pointing to `system_portage_directory` (if the locations
are different ofcourse) to be sure to always have an up and ready to use
package manager.

See the [Default Gentoo ebuild repository location change][] chapter of the 
Portage documentation for more informations.

[Default Gentoo ebuild repository location change]: https://wiki.gentoo.org/wiki/Portage#Default_Gentoo_ebuild_repository_location_change

#### System group

If the ansible user is not `root`, he will be added to the `portage` system group.

The portage configuration files and directories are writeables for this group.

#### Ansible dependencies

As explained in the [portage module documentation][], the `gentoolkit` package is
a dependency to make it work.

So, we install it if it's missing.

[portage module documentation]: https://docs.ansible.com/ansible/latest/collections/community/general/portage_module.html

#### Compilation settings

```yaml
# Build from sources when possible
system_packages_build: auto
# https://wiki.gentoo.org/wiki/Safe_CFLAGS#Manual
system_packages_march: native
```

If You want to compile your nodes with [distcc][], change the `system_packages_march`
value, You can find help in the [Safe CFLAGS] manual.

[distcc]: https://wiki.gentoo.org/wiki/Distcc/fr
[Safe CFLAGS]: https://wiki.gentoo.org/wiki/Safe_CFLAGS#Manual

#### Kernel

Wich kernel to install :

```yaml
system_portage_kernel: auto
```

Supported values :

- `auto` : Get from the list of installed packages
- `gentoo-kernel`
- `gentoo-kernel-bin`
- `gentoo-sources` : Built with [Genkernel][]
- `vanilla-kernel`

See [distribution kernels][] and/or [Genkernel][] for more informations.

You also can view the complete list of available kernels (but not only)
on the [sys-kernel category][] web page.

[distribution kernels]: https://wiki.gentoo.org/wiki/Project:Distribution_Kernel
[Genkernel]: https://wiki.gentoo.org/wiki/Genkernel
[sys-kernel category]: https://packages.gentoo.org/categories/sys-kernel

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

Supported package managers at this time :

- `apt` (Debian like)

Static package lists
--------------------

### By key

To be multi-distro compatible, we maintain a dictionary of packages name
correspondance to be able to install some packages independently of the
distribution we use.

We based the key names on the commonly usage of package names.

Supported keys :
- `bond` : Packages to manage bonded networks
  (automatically added if at least a bond is found in `system_networks`)
- `bridge` : Packages to manage bridged networks
  (automatically added if at least a bridge is found in `system_networks`)
- `ca-certificates` : Trusted certificate authorities and the tool to manage
  them (automatically added when `system_ca_certificates` is not empty)
- `chrony` : Versatile implementation of the Network Time Protocol (NTP)
  (automatically added if `system_time_backend` is `chrony`)
- `gnome` : [Gnome][] desktop environment
- `lvm2`: Logical volumes manager
  (automatically added if `system_storages_vg` is not empty)
- `ntp` : Legacy NTPd server
  (automatically added if `system_time_backend` is `ntp`)
- `parted` : GNU tool to manipulates partition tables
  (automatically added if `system_manage_storages` is `true`)
- `systemd-timesyncd` : Systemd integrated NTP client
  (automatically added if `system_time_backend` is `systemd-timesyncd`)
- `unattended-upgrades` : Packages to maintain the system up to date
- `vlan` : Packages to manage vLAN networks
  (automatically added if at least a vLAN is found in `system_networks`)
- `zsh`: Packages to install ZSH with completions and syntax highlighting when
  available (automatically added if at least one user use it in `system_users`)

If a given key doesn't exist in the dictionary, the name will be used as a
package name. It could be a good idea too add your packages names in this list
even it is not in the list.

[Gnome]: https://www.gnome.org

### By name

You can install a list of packages through the `system_packages_add_by_name` variable.

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
