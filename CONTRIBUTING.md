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

```sh
molecule test
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
