Development guide
=================

Requirements
------------

Install and configure :

* docker
* libvirt
* vagrant
* vagrant-libvirt plugin
* molecule
* molecule-docker
* molecule-vagrant

If You are new with Molecule + Vagrant-libvirt, please read this [blog post][].

[blog post]: https://www.tauceti.blog/posts/testing-ansible-roles-with-molecule-libvirt-vagrant-qemu-kvm/

Run tests
---------

Quick tests of the role without any options, ran in docker containers as `ansible` user :

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

Merge request in Gitlab.
