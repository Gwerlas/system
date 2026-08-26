Remote access
=============

SSHd
----

### Feature flipping

`system_manage_sshd` accepts `auto` (default), `true` and `false`.

```yaml
system_manage_sshd: auto
```

In `auto` mode, sshd is managed outside of a container as soon as you give the
role one instruction : an entry in `system_sshd_config`. `true` and `false`
force it either way, container included.

### Configuration

The `system_sshd_config` dictionary accept (almost) all of the
[sshd_config(5)][] instructions.

> **Note**
>
> `Match` instruction isn't yet implemented in this role.

Example :

```yaml
system_sshd_config:
  PubkeyAuthentication: true
  X11Forwarding: false
  ListenAddress: 192.0.2.10
  MaxAuthTries: 2
  Ciphers:
    - aes256-ctr
    - aes192-ctr
  Subsystem: sftp /usr/lib/openssh/sftp-server
```

Values can be booleans, numbers, strings or lists. Booleans are rendered as
`yes` / `no`, and lists are rendered in one of two ways depending on the
option:

- the algorithm options — `AuthenticationMethods`, `CASignatureAlgorithms`,
  `Ciphers`, `HostbasedAcceptedKeyTypes`, `HostKeyAlgorithms`,
  `KexAlgorithms`, `MACs` and `PubkeyAcceptedKeyTypes` — are joined with
  commas on a single line, so the `Ciphers` above renders as
  `Ciphers aes256-ctr,aes192-ctr`;
- every other option is repeated once per item, so `AcceptEnv: [LANG, LC_*]`
  renders as two `AcceptEnv` lines.

> **Be careful**
>
> The whole `/etc/ssh/sshd_config` is rewritten from `system_sshd_config` : it
> is not merged with the file your distribution shipped. Anything you do not
> declare is gone.
>
> The role adds only two things of its own : `UsePAM yes`, without which a
> cloud-init user whose `/etc/shadow` password is locked is refused even by
> public key, and — on Debian like distros — the `Include
> /etc/ssh/sshd_config.d/*.conf` those distributions rely on. Forcing
> `system_manage_sshd` to `true` with an empty `system_sshd_config` therefore
> gives you a nearly empty configuration, not a set of sane defaults.

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

Two possible ways are available: `sync` or `copy`.

#### Sync back your keys

This method is simple, but You are not free to name your files as You want.

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

### Copy back your keys

This method is a bit more complexe but also more flexible :

```yaml
- name: Backup SSHd hosts keys
  hosts: all
  vars:
    ansible_ssh_common_args: >-
      -o StrictHostKeyChecking=no
      -o UserKnownHostsFile=/dev/null
    system_sshd_host_keys:
      ecdsa:
        src: ecdsa.key
      ecdsa_public:
        src: ecdsa.pub
      ed25519:
        content: "{{ lookup('ansible.builtin.file', 'ed25519.key') }}"
      ed25519_public:
        content: "{{ lookup('ansible.builtin.file', 'ed25519.pub') }}"
      rsa:
        src: rsa.key
      rsa_public:
        content: "{{ lookup('ansible.builtin.file', 'rsa.pub') }}"
  roles:
    - role: gwerlas.system
```

The keys of the `system_sshd_host_keys` must be :

- `ecdsa`
- `ecdsa_public`
- `ed25519`
- `ed25519_public`
- `rsa`
- `rsa_public`

And the attributes must be `content` or `src` as soon as they are forwarded to
the [ansible.builtin.copy][] Ansible module.

[ansible.builtin.copy]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html#attributes
