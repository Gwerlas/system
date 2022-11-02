Users
=====

Users and groups management.

ZSH
---

A sample configuration is stored in `/etc/skel` and will be used
by each new users. They will be able to customize their ZSH settings.

Variables
---------

```yaml
system_users: []
system_users_groups: []
```

Users and groups are lists of dictionaries with the same structure documented respectively in the
[Ansible user module][] and [Ansible group module][].


The users' groups and the groups listed in `system_users_groups` will
be created if missing.

Example :

```yaml
system_users:
  - name: jane
    comment: System administrator
    group: "{{ 'adm' if ansible_os_family == 'Debian' else 'wheel' }}"
    groups:
      - sudo
      - users
    shell: /bin/zsh
  - name: john
    group: users

system_users_groups:
  - name: my_company
```

[Ansible user module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html
[Ansible group module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/group_module.html#ansible-collections-ansible-builtin-group-module
