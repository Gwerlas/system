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
* vagrant
* vagrant-libvirt plugin
* molecule
* molecule-plugins

If You are new with Molecule + Vagrant-libvirt, please read this [blog post][].

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

Test the `server` profile with hosts, users and groups settings customized,
ran in vagrant/libvirt VMs as `vagrant` user :

```sh
molecule test -s servers
```

Test stream distros in vagrant/libvirt VMs as `vagrant` user :

```sh
molecule test -s stream
```

Test each time synchronization service :

```sh
molecule test -s chrony
molecule test -s ntp
molecule test -s systemd-timesyncd
```

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Submit your changes
-------------------

Merge request in [Gitlab][].

<!-- Links section -->
[blog post]: https://www.tauceti.blog/posts/testing-ansible-roles-with-molecule-libvirt-vagrant-qemu-kvm/
[Gitlab]: https://gitlab.com/yoanncolin/ansible/roles/system/-/merge_requests
