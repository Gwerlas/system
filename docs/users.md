Users
=====

Users and groups management.

Variables
---------

```yaml
system_users_admin_group: "{{ 'adm' if ansible_os_family == 'Debian' else 'wheel' }}"
system_users_groups: []
system_users: []
```

Users and groups
----------------

Users and groups are lists of dictionaries with the same structure documented respectively in the
[Ansible user module][] and [Ansible group module][].

The users' groups and the groups listed in `system_users_groups` will
be created if missing.

Example :

```yaml
system_users:
  - name: jane
    comment: System administrator
    group: "{{ system_users_admin_group }}"
    groups:
      - "{{ system_sudo_group }}"
      - users
    shell: /bin/zsh
  - name: john
    group: users

system_users_groups:
  - name: my_company
```

[Ansible user module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html
[Ansible group module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/group_module.html#ansible-collections-ansible-builtin-group-module

ZSH
---

If some users have `zsh` as `shell`, a sample configuration is stored
in `/etc/skel` and will be copied in each new users home directory.

The users will be able to customize their ZSH settings later.

See [ZSH Configuration](zsh.md) for more details.

SSH Keys
--------

Users' `authorized_keys` is a list of objects looking like the
[Ansible authorized_keys module][] except for the `user` field ofcourse.

Example :

```yaml
system_users:
  - name: jane
    authorized_keys:
      - key: ssh-rsa AAAA test
        state: absent
  - name: joe
    authorized_keys:
      - key: https://github.com/joe.keys
```

[Ansible authorized_keys module]: https://docs.ansible.com/ansible/latest/collections/ansible/posix/authorized_key_module.html
