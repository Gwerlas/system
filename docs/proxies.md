Proxies
=======

Configure network proxies.

Variables
---------

By default, these variables are not defined, here is an example of
proxies configuration :

```yaml
system_http_proxy: http://squid.my_domain.tld:3128
system_https_proxy: "{{ system_http_proxy }}"
system_ftp_proxy:  "{{ system_http_proxy }}"
system_no_proxy: 127.0.0.1,localhost,.my_domain.tld
```

Proxies configuration environment variables will be set in `/etc/environment`,
because this file is used by pam, and not by the shell, we do embrace values
by double quotes, and the `system_no_proxy` value must be a comma-separated
list of domain extensions or IP without spaces.

The result is :

```sh
http_proxy=http://squid.my_domain.tld:3128
https_proxy=http://squid.my_domain.tld:3128
ftp_proxy=http://squid.my_domain.tld:3128
no_proxy=127.0.0.1,localhost,.my_domain.tld
HTTP_PROXY=http://squid.my_domain.tld:3128
HTTPS_PROXY=http://squid.my_domain.tld:3128
FTP_PROXY=http://squid.my_domain.tld:3128
NO_PROXY=127.0.0.1,localhost,.my_domain.tld
```
