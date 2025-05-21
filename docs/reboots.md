Reboots
=======

Variables
---------

```yaml
system_reboot_handler: reboot
system_reboot_timeout: 600
```

Scripts for the detection
-------------------------

Some distributions does not provide command line to easily know if a reboot is
required, or if the packages cache is outdated. So we put scripts to do the detection.

You can change those scripts location through the `system_scripts_path`.

Reboot mode
-----------

For some reasons, You may want to change the `system_reboot_handler`.

Possible choice :

- `skip`
- `reboot` (default)

Be careful, the reboot himself is a handler, depending of your way to call the
role, it won't be triggered until a `flush_handlers` or the end of the Playbook.

Please refer to the [Handlers in roles][] documentation for more informations.

Example :

```yaml
- name: Upgrade all nodes at a time without rebooting
  hosts: all
  vars:
    system_packages_upgrade: true
    system_reboot_handler: skip
  tasks:
    - name: Upgrade system
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: packages

- name: Reboot nodes one by one
  hosts: all
  serial: 1
  tasks:
    - name: Reboot if needed
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: reboot
```

Just show if a reboot is needed :

```yaml
- name: Just show if a reboot is needed
  hosts: all
  vars:
    system_reboot_handler: skip
  tasks:
    - name: Dry run
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: reboot

    - name: Show the fact value
      ansible.builtin.debug:
        var: system_needs_reboot
```

[Handlers in roles]: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html#handlers-in-roles

Timeout
-------

Set `system_reboot_timeout` to the maximum seconds to wait for reboot and respond.

See the [`timeout` parameter of the Ansible `reboot` module][] documentation for more informations.

[`timeout` parameter of the Ansible `reboot` module]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/reboot_module.html#parameter-reboot_timeout
