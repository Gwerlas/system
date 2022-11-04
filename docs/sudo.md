Sudo
====

Configure sudo rules.

Variables
---------

### Feature flipping

By default, sudo management is disabled for containers.

```yaml
system_manage_sudo: "{{ 'container' not in ansible_virtualization_tech_guest }}"
```

You can force enabling or disabling it defining the `system_manage_sudo` to `true` or `false`.

### Facts

The version of sudo is available through the `system_sudo_version` fact.

### Rules

```yaml
system_sudo_nopasswd: true
system_sudo_group: "{{ 'sudo' if ansible_os_family == 'Debian' else 'wheel' }}"
system_sudo_defaults: []
```

By default, `root` and the `system_sudo_group` group be able to sudo all commands without password.

If You want sudo asks password for `system_sudo_group`, set `system_sudo_nopasswd` to `false`.

You can set a lot of `Defaults` option (eg. "SUDOERS OPTIONS" section from the sudoers(5) man page).

For example, to reproduce the RedHat default behaviour :

```yaml
system_sudo_defaults:
  - "!visiblepw"
  - always_set_home
  - match_group_by_gid
  - always_query_group_plugin
  - env_reset
  - env_keep:
      - COLORS
      - DISPLAY
      - HOSTNAME
      - HISTSIZE
      - KDEDIR
      - LS_COLORS
      - MAIL
      - PS1
      - PS2
      - QTDIR
      - USERNAME
      - LANG
      - LC_ADDRESS
      - LC_CTYPE
      - LC_COLLATE
      - LC_IDENTIFICATION
      - LC_MEASUREMENT
      - LC_MESSAGES
      - LC_MONETARY
      - LC_NAME
      - LC_NUMERIC
      - LC_PAPER
      - LC_TELEPHONE
      - LC_TIME
      - LC_ALL
      - LANGUAGE
      - LINGUAS
      - _XKB_CHARSET
      - XAUTHORITY
  - secure_path: /sbin:/bin:/usr/sbin:/usr/bin
```
