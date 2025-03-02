Remote access
=============

SSHd
----

SSH remote access is disabled by default unless you add some [sshd_config(5)][]
arguments to the `system_sshd_config` dictionary.

> **Note**
>
> `Match` instruction isn't yet implemented in this role.

You can allow your users to connect remotely with SSH defining
`system_manage_sshd` to `true`.

[sshd_config(5)]: https://linux.die.net/man/5/sshd_config
