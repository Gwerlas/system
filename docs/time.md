Time
====

Time and date management.

Variables
---------

### Feature flipping

By default, time synchronisation management is disabled for containers.

```yaml
system_manage_time: "{{ not in_container }}"
```

You can force enabling or disabling it defining the `system_manage_time` to `true` or `false`.

### Time backend

When no `system_time_backend` is given, we use systemd to configure the time
synchronisation if the distribution support it, else we install and configure
chrony.

Available backends :

- `systemd-timesyncd` (default)
- `chrony` (default when systemd-timesyncd is not supported)
- `ntp` (deprecated)

### Custom time servers

```yaml
system_time_servers: []
```

For example :

```yaml
system_time_servers:
  - 0.fr.pool.ntp.org
  - 1.fr.pool.ntp.org
  - 2.fr.pool.ntp.org
  - 3.fr.pool.ntp.org
```

### NTPd only

Note that NTPd is not more proposed in RedHat like distros since the version 8.

If You want to use it :

```yaml
system_time_ntpd_driftfile: /var/lib/ntp/drift
system_time_ntpd_includefile: /etc/ntp/crypto/pw

# Key file containing the keys and key identifiers used when operating
# with symmetric key cryptography.
system_time_ntpd_keys: /etc/ntp/keys

# Permit time synchronization with our time source, but do not
# permit the source to query or modify the service on this system.
system_time_ntpd_restrict_defaults:
  - nomodify
  - notrap
  - nopeer
  - noquery

# Permit all access over the loopback interface.  This could
# be tightened as well, but to do so would effect some of
# the administrative functions.
system_time_ntpd_restricts:
  - ip: '127.0.0.1'
  - ip: '::1'

system_time_ntpd_fudges: []

# Specify the key identifiers which are trusted.
# system_time_ntpd_trustedkey: [4, 8, 42]

# Specify the key identifier to use with the ntpdc utility.
# system_time_ntpd_requestkey: 8

# Specify the key identifier to use with the ntpq utility.
# system_time_ntpd_controlkey: 8

# Enable writing of statistics records.
# system_time_ntpd_statistics: ['clockstats', 'cryptostats', 'loopstats', 'peerstats']

# Disable the monitoring facility to prevent amplification attacks using ntpdc
# monlist command when default restrict does not include the noquery flag. See
# CVE-2013-5211 for more details.
# Note: Monitoring will not be disabled with the limited restriction flag.
system_time_ntpd_disable:
  - monitor
```

### Timesync on RedHat like

Systemd's systemd-timesyncd is not supported by RedHat.

To use timesyncd on EL8 or newer, You'll need to [install EPEL][].

[install EPEL]: packages.md#epel-extra-packages-for-enterprise-linux

Examples
--------

Use the legacy `ntp` package for time synchronisation, and a list of custom
NTP servers :

```yaml
---
- name: NTPd
  hosts: all
  roles:
    - name: gwerlas.system
      vars:
        system_time_backend: ntp
        system_time_servers:
          - 0.fr.pool.ntp.org
          - 1.fr.pool.ntp.org
          - 2.fr.pool.ntp.org
          - 3.fr.pool.ntp.org
```
