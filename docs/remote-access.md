Remote access
=============

SSHd
----

### Configuration

The `system_sshd_config` dictionary accept (almost) all of the [sshd_config(5)][] instructions.

> **Note**
>
> `Match` instruction isn't yet implemented in this role.

Example :

```yaml
system_sshd_config:
  PubkeyAuthentication: true
  X11Forwarding: false
```

If You set `system_manage_sshd` to `true` without any `system_sshd_config`
instructions, we will filled our defaults.

[sshd_config(5)]: https://linux.die.net/man/5/sshd_config

### Backup your hosts keys

Here is an example of a playbook that backup your hosts keys :

```yaml
- name: Backup SSHd hosts keys
  hosts: all
  roles:
    # Configure the package manager and install rsync, at least
    - role: gwerlas.system
  tasks:
    - name: SSHd keys
      become: true
      ansible.posix.synchronize:
        src: /etc/ssh/ssh_host_*
        dest: my/local/backup/directory/{{ inventory_hostname }}/
        mode: pull
```

### Restore your hosts keys

Currently, we have implemented a synchronization of `ssh_host_*` files between
a directory on the remote host to the node.

This method is simple, but You are not free to name your files as You want.
A more flexible method will be implemented in the future.

Here is an example of a playbook that restore your hosts key pairs :

```yaml
- name: Backup SSHd hosts keys
  hosts: all
  vars:
    ansible_ssh_common_args: >-
      -o StrictHostKeyChecking=no
      -o UserKnownHostsFile=/dev/null
    system_sshd_host_keys:
      sync_from: my/local/backup/directory/{{ inventory_hostname }}/
  roles:
    - role: gwerlas.system
```
