Development guide
=================

Requirements
------------

Install and configure :

* libvirt
* vagrant
* vagrant-libvirt plugin
* molecule
* molecule-vagrant

Run tests
---------

Quick tests of the role without any options, in docker containers,
run as `ansible` user :

```sh
molecule test
```

Test the server profile with the most of settings customized,
in vagrant/libvirt VMs, run as `vagrant` user :

```sh
molecule test -s servers
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
