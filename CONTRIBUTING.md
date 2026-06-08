Development guide
=================

| **Important**
|
| The GitHub repository exist only because Ansible Galaxy support only GitHub.
| Please, do your merge requests on [Gitlab][].

Requirements
------------

Install and configure :

* docker
* libvirt
* python3-jmespath
* molecule
* molecule-plugins

Some tests use a web proxy, if you don't have one, install
Squid locally with at least :

- localnet allowed
- 3128/tcp port granted to the libvirt zone

Run tests
---------

Quick tests of the role without any options, ran in containers as `ansible` user :

```sh
molecule test -s containers
```

The driver preference is defined by `MOLECULE_CONTAINERS_BACKEND=podman,docker` and you can easily switch between the two by setting this variable.

Test the role with its defaults values in a VM of each supported distro :

```sh
molecule test
```

Test the `server` and `desktop` profiles with hosts, users and groups settings
customized, ran in libvirt VMs as the `molecule` user :

```sh
molecule test -s servers
molecule test -s desktops
```

Test each time synchronization service :

```sh
molecule test -s chrony
molecule test -s ntp
molecule test -s timesync
```

libvirt connection and storage pool
-----------------------------------

Scenarios that drive libvirt via its API (e.g. `facts`) honour two environment
variables, with sensible defaults when unset:

| Variable               | Default          | Purpose                         |
| ---------------------- | ---------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system` | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`        | name of the storage pool to use |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL`
is local to this project but follows the same naming convention. Both are
forwarded into the molecule container by the wrapper (any `LIBVIRT_*` env var
is passed through).

Recommended setup if the system pool sits on a small partition: create a
dedicated pool on a larger filesystem and point molecule at it. For example:

```sh
install -d -m 2775 -g qemu $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-define-as molecule dir --target $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-autostart molecule
virsh -c qemu:///system pool-start molecule

export LIBVIRT_DEFAULT_POOL=molecule
molecule test -s facts
```

The directory must be reachable by the `qemu` user (group `qemu` + setgid
parent works, provided your user is in `qemu`).

`qemu:///session` is currently *not* supported by these scenarios: session
mode has no built-in `default` network, and `virsh net-dhcp-leases` would not
find any lease. If you want to view VMs in a GUI without switching to session
mode, point GNOME Boxes (>=41) at `qemu:///system` or use `virt-manager`,
which lists both URIs side by side.

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Adding a new distribution or version
------------------------------------

The list of officially supported platforms lives in [`molecule/shared/platforms.yml`][platforms].
It is the single source of truth for both Molecule (cloud image URL per platform)
and Galaxy (`galaxy_info.platforms` in `meta/main.yml`).

After editing `molecule/shared/platforms.yml`, run the sync script to refresh
`meta/main.yml`:

```sh
python3 scripts/sync-meta-platforms.py
```

Each scenario's `molecule.yml` then picks a subset of those platforms by name
(plus any `groups` / `memory` override); the cloud image URL is resolved at
runtime by `create.yml` via a `lookup` on `molecule/shared/platforms.yml`.
`molecule/shared/` also hosts the `create.yml` / `destroy.yml` playbooks that
each scenario symlinks; molecule ignores it as a scenario because it doesn't
carry a `molecule.yml`.

Submit your changes
-------------------

Merge request in [Gitlab][].

<!-- Links section -->
[Gitlab]: https://gitlab.com/yoanncolin/ansible/roles/system/-/merge_requests
[platforms]: molecule/shared/platforms.yml
