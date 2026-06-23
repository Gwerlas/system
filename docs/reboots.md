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

Jump hosts (`ProxyJump` / bastion)
-----------------------------------

If some nodes are reached through a jump host (an SSH bastion declared with
`ProxyJump` / `ansible_ssh_common_args`), **never reboot that jump host in the
same batch as the nodes that depend on it**.

When every node reboots at once, the bastion reboots too. The reboot of a node
behind it works like this : Ansible sends `shutdown -r`, the SSH connection
drops, and Ansible assumes the reboot started. But if the bastion goes down
*first* (its own reboot), the connection drops **before** the `shutdown` reaches
the node : Ansible believes the reboot started while the node never actually
rebooted. It then waits for the boot time to change until `system_reboot_timeout`
expires, and the task fails with a timeout.

This is a race on the sub-second ordering between the bastion and each node, so
it hits a random subset of the nodes on every run — while the bastion itself,
which reboots over its own direct connection, always succeeds. Raising
`system_reboot_timeout` does **not** help : the affected nodes simply never
reboot.

The fix is orchestration : reboot the nodes while the bastion is still up, then
reboot the bastion on its own (over its direct connection). Put the bastion in a
dedicated group and split the reboot into two plays :

```yaml
- name: Reboot every node except the jump host
  hosts: all:!bastion
  tasks:
    - name: Reboot if needed
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: reboot

- name: Reboot the jump host last, on its own
  hosts: bastion
  tasks:
    - name: Reboot if needed
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: reboot
```

The `serial: 1` pattern shown above also avoids the race (only one host reboots
at a time, so the bastion is never down while a node reconnects), at the cost of
rebooting the whole fleet sequentially.

What triggers a reboot
----------------------

After a package operation, the role inspects the packages installed during
the current boot and asks for a reboot when any of these change :

- `sys-boot/grub`
- the active service manager (`sys-apps/systemd` or `sys-apps/openrc`)
- the kernel package (`sys-kernel/{{ system_portage_kernel }}`)
- `sys-libs/glibc`
- `sys-kernel/linux-firmware` — also rebuilds the dracut initramfs
  (`dracut --regenerate-all`) and regenerates `grub.cfg` first, so the
  bundled CPU microcode stays in sync with the new firmware and the boot
  entries don't reference a stale standalone microcode image.

Each trigger honours `system_reboot_handler`, so setting it to `skip` keeps
the role from rebooting even if any of these packages was just updated.
