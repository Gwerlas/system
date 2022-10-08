Base system
===========

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/system/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/system/-/commits/main)

Linux systems base settings.

Running roles in containers is not common, but this use case is supported for
Ansible testing with Molecule. In this case, just the package manager cache
will be update if needed, the other system component will be not managed since
it is the reponsibility of the container engine.

GitLab project: [yoanncolin/ansible/roles/system](https://gitlab.com/yoanncolin/ansible/roles/system)

Requirements
------------

This role as been writen to be run as non root user, so Sudo has to be installed and configured.

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
system_manage_hosts_names: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_domainname: localdomain
system_hostname: "{{ inventory_hostname }}"
system_hostname_aliases: []
system_custom_hosts: []

system_pkg_cache_max_age: -1w
system_update: false
system_update_reboot_msg: Reboot initiated by Ansible after a distribution update

system_profile: server

system_install_zsh: false

system_firewall_managed: "{{ 'container' not in ansible_virtualization_tech_guest }}"
system_firewall_default_zone: public
```

### Hosts names configuration

By default, hosts names management is disabled for containers.

You can force enabling or disabling throw defining the `system_manage_hosts_names` to `true` or `false`.

You can customize the system hostname by setting the `system_hostname` variable. By default, the inventory hostname is used.

If You need to add hosts aliases to the loopback interfaces in `/etc/hosts`, set them in the `system_hostname_aliases` list. For exemple :

```yaml
system_hostname_aliases:
  - webserver
  - www
```

Set your domain name throw the variable `system_domainname`.

If your nodes need to resolve external custom hosts in `/etc/hosts`, You can set them in `system_custom_hosts` list of dict :

```yaml
system_custom_hosts:
  - ip: '10.0.0.7'
    names: ['host7']
```

### Package manager cache

For idempotence purpose, we only update package manager cache if missing.

Because there is a big risq of package installation failure if the cache is too old,
we update it if it is older than one week.

You can change the max age throw the `system_pkg_cache_max_age` variable.

**Be careful** because some distributions package managers (RedHat like for example)
could update their cache automatically or, at the opposit, could ignore some cache
update explicitly asked.

### Packages update

The `system_update` set as `true` will update the system packages and reboot
the machine if needed.

If you have Waterfall or V-Cycle deployments, You should call it at first
deployment time or for whole system upgrades campains, then let it to `false`
at the other times to keep control on your infrastructure state.

For continuous deployments, You would like to set it permanently as `true`.

In case of Ansible role development, set it as `true` at preparation stage
only to keep idempotence control. Here an exemple of `molecule/default/prepare.yml` :

```yml
---
- name: Prepare
  hosts: all
  tasks:
    - name: Run gwerlas.system
      ansible.builtin.include_role:
        name: gwerlas.system
      vars:
        system_update: true
```

You can customize the system update reboot message throw the
`system_update_reboot_msg` variable.

### Profile

Currently for `server` nodes only. Desktops will be supported in future
developments.

### ZSH

The `system_install_zsh` set as `true` will install ZSH and put a default user
configuration.

### Firewall

By defaults, firewalling is disabled for containers, and enabled in the
other cases.

You can force enabling or disabling throw defining the `system_firewall_managed`
to `true` or `false`.

Dependencies
------------

None.

Example Playbook
----------------

First deployment :

```yaml
---
- name: System preparation
  hosts: all
  roles:
    - name: gwerlas.system
      vars:
        system_update: true
```

Distribution update, rolling update by ~10% slices :

```yaml
---
- name: Rolling update
  hosts: all
  serial: (hostvars | length / 10) | round(0, 'ceil') | int
  roles:
    - name: gwerlas.system
      vars:
        system_update: true
```

Use just one task :

```yaml
---
- name: Firewalling
  hosts: all
  tasks:
    - name: Update the package manager cache
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: update
    - name: Firewalling
      ansible.builtin.import_role:
        name: gwerlas.system
        tasks_from: firewall
        vars:
          rules:
            - http
```

License
-------

[BSD 3-Clause License](LICENSE).
