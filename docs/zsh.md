ZSH Configuration
=================

ZSH configuration files placed in `/etc/skel`.

By default, we keep the distribution defaults.

Proposed files
--------------

You can use all or part of the files offered by this role :

```yaml
system_zsh_files:
  - .zshrc
  - .zsh/history
  - .zsh/prompt
  - .zsh/prompt_git
```

Use your own files
------------------

To use your own configuration files or templates, put them in the `files/.zsh/`
directory at the root of your playbook / role and add them to the list.

### Raw files

Ensure that your `.zshrc` parse the files of `~/.zsh`, or use that of this role :

```yaml
system_zsh_files:
  - .zshrc
  - .zsh/my-company-customs
```

>  **Be careful**
>
> If you create a `files/.zshrc` in your parent role / playbook and expect that
> Ansible will use it, you are wrong.
>
> See [Resolving local relative paths][] for more details.
>
> As a workaround, You can use a [template](#templates).

[Resolving local relative paths]: https://docs.ansible.com/ansible/latest/playbook_guide/playbook_pathing.html

### Templates

In the same way, You can use templates :

```yaml
system_zsh_templates:
  - .zshrc
  - .zsh/my-company-customs
```

Be sure to append the `.j2` extension to your files name, and to store them in
your `templates/.zsh` directory.
