CA certificates
===============

Configure the CA certificates.

Tag
---

You can quickly update the CA certificates with the Ansible tag `ca` :

```sh
ansible-playbook -t ca my_play.yml
```

Variables
---------

CA certificate files that will be copied to the nodes :

```yaml
system_ca_certificates: []
```
