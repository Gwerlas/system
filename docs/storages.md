Storages
========

Create partitions and volumes, format and mount them.

Variables
---------

### Feature flipping

```yaml
system_manage_storages: |
  {{
    (
      system_storages_partitions +
      system_storages_vg +
      system_storages_lvol
    ) | length > 0
  }}
```

To enable or disable storage management set `system_manage_storages` to `true`
or `false`.

### Partitions

List of partitions to manage :

```yaml
system_storages_partitions: []
```

It is a list of dictionaries with the same structure documented in the
[Ansible parted module][] plus the [additional values](#additional-values) for
the mounted directory.

[Ansible parted module]: https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html#

For some arguments, we changed the default values as is :

- `fs_type`: `ext4`
- `number`: `1`
- `resize`: `true`
- `state`: `present`

### Logical Volume Manager (LVM)

List of resources to manage :

```yaml
system_storages_vg: []
system_storages_lvol: []
```

The volume groups and logical volumes are lists of dictionaries with the same
structure documented respectively in the [Ansible lvg module][] and
[Ansible lvol module][].

You can add the [additional values](#additional-values) for the mounted
directory of logical volumes.

[Ansible lvg module]: https://docs.ansible.com/ansible/latest/collections/community/general/lvg_module.html
[Ansible lvol module]: https://docs.ansible.com/ansible/latest/collections/community/general/lvol_module.html

For some arguments, we changed the VG default values as is :

- `pvresize`: `true`
- `state`: `present`

And for the logical volumes :

- `resizefs`: `true`
- `shrink`: `false` to avoid idempotency failure
- `size`: `100%FREE`
- `state`: `present`

### Additional values

The storage You want to be mounted must have the `mount` argument to be filled.

You can add the optionals arguments `owner`, `group` and `mode` for the mount
directory, as described in the [Ansible file module][].

[Ansible file module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html

Examples
--------

Create a logical volume on two disks and mount it in `/var/backups`.

```yaml
system_storages_partitions:
  - device: /dev/sdb
    flags:
      - lvm
  - device: /dev/sdc
    flags:
      - lvm

system_storages_vg:
  - vg: datastore

system_storages_lvol:
  - vg: datastore
    lv: backups
    pvs: /dev/sdb,/dev/sdc
    mount: /var/backups
```

Create and use two partitions in a block device :

```yaml
system_storages_partitions:
  - device: /dev/vdb
    number: 1
    part_end: 5GiB
    mount: /var/backups
  - device: /dev/vdb
    number: 2
    part_start: 5GiB
    mount: /home
```
