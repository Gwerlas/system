Development guide
=================

| **Important**
|
| The GitHub repository exist only because Ansible Galaxy support only GitHub.
| Please, do your merge requests on [Gitlab][].

Requirements
------------

Install and configure :

- docker
- libvirt
- python3-jmespath
- molecule
- molecule-plugins
- ansible-lint
- [j2lint][] 1.3.0 — the Jinja linter the `j2lint` CI job runs
- [markdownlint-cli2][] — the Markdown linter the `markdownlint` job runs

`.claude/settings.json` ships a Claude Code hook that runs `ansible-lint` on
every edited YAML file and `j2lint` on every edited template, so a syntax error
surfaces at edit time rather than in the pipeline. Both are skipped when the
tool is missing, so the hook never blocks a contributor who has not installed
them.

Distributions that follow PEP 668 (Gentoo, recent Debian and Fedora) refuse
`pip install` into the system or user site. Use a dedicated virtualenv — the
hook looks for `j2lint` in `PATH` first, then falls back to this exact path:

```sh
python3 -m venv ~/.local/share/j2lint-venv
~/.local/share/j2lint-venv/bin/pip install j2lint==1.3.0
```

The container scenarios boot a real systemd in each guest, and every one of
them eats a handful of inotify instances *from your own user quota*. With the
kernel default of 128 and a desktop session already holding ~90, the last
container of a 12-platform run dies at startup (exit 255, no log). Raise the
limit before running them :

```sh
sudo sysctl -w fs.inotify.max_user_instances=1024
```

Some tests use a web proxy, if you don't have one, install
Squid locally with at least :

- localnet allowed
- 3128/tcp port granted to the libvirt zone

Run tests
---------

Scenarios come in two flavours: the container ones run on the
`gwerlas/ansible-guest-*` images (fast, but the role disables hosts, firewall,
time, sshd, sudo and reboot management when it detects a container), the others
boot a libvirt VM per platform.

Three scenarios run in containers, as the `ansible` user — the whole role with
its default values, the gathered facts, and the package managers configuration
alone :

```sh
molecule test -s containers
molecule test -s containers-facts
molecule test -s pkg-mgrs-only
```

Those three are the ones the CI runs, since they need no VM. `pkg-mgrs-only`
qualifies because it only imports the `package-managers` task file: no service
manager, no clock, no reboot, so none of the role's `not in_container` guards
skip anything it exercises.

They share a single `molecule.yml`, held by `molecule/containers/` and
symlinked from the two others — add a distribution there and the three
scenarios pick it up.

The driver preference is defined by `MOLECULE_CONTAINERS_BACKEND=podman,docker`
and you can easily switch between the two by setting this variable.

Test the role with its defaults values in a VM of each supported distro :

```sh
molecule test
```

Test the `server` and `desktop` profiles with hosts, users and groups settings
customized, ran in libvirt VMs as the `molecule` user :

```sh
molecule test -s servers
molecule test -s desktops
```

Test each time synchronization service :

```sh
molecule test -s chrony
molecule test -s ntp
molecule test -s timesync
```

What the pipeline does not cover
--------------------------------

Shared GitLab runners expose no `/dev/kvm`, and the project has no runner of
its own, so **no libvirt scenario ever runs in CI**. A green pipeline says the
role is sound on everything a container can exercise, and says nothing at all
about the rest:

| Area                                            | Covered by CI          | Tested by                       |
| ----------------------------------------------- | ---------------------- | ------------------------------- |
| Task syntax and idioms                          | yes, `ansible-lint`    | ansible-lint                    |
| Templates compile                               | yes, `j2lint`          | j2lint                          |
| Package managers, packages, users, CA, sudo     | yes, container jobs    | the three container scenarios   |
| Bare-metal facts (`not in_container` block)     | no                     | `facts`                         |
| sshd configuration and host keys                | no                     | `servers`                       |
| Storage, LVM, extra disks                       | no                     | `servers`, `default`            |
| Network interfaces and static routes            | no                     | `servers`                       |
| Reboot handling                                 | no                     | `reboot-only`                   |
| Clock and time synchronisation                  | no                     | `chrony`, `ntp`, `timesync`     |
| Portage kernel and its handlers                 | no                     | `default` on gentoo             |
| Desktop profiles                                | no                     | `desktops`, `gnome`             |

### When each job runs

`workflow:` only decides whether a pipeline exists — on a branch or a tag.
Each job then declares what it depends on:

| Job                | Runs when                                       |
| ------------------ | ----------------------------------------------- |
| `ansible-lint`     | any of the role's YAML changed                  |
| `j2lint`           | a `templates/**/*.j2` changed                   |
| `markdownlint`     | a `*.md` or the linter config changed           |
| the container jobs | the role's code or its scenarios changed        |

Everything is compared against `main` (`compare_to: refs/heads/main`), not
against the previous push. That matters: `changes:` with no base evaluates to
true, so on a freshly pushed branch a filter written without `compare_to` runs
everything it meant to skip.

The comparison covers the branch as a whole, not the latest commit. A merge
request that touches the role's code therefore runs the scenarios on each of
its pushes, documentation-only commits included — the branch as a whole still
changes the role. Only a branch that never touches anything but documentation
comes down to `ansible-lint` alone.

On `main` itself and on tags every job runs unconditionally — comparing `main`
to `main` matches nothing, and that is precisely when the full pipeline is
wanted.

`workflow:` keeps a path list of its own, for one reason: a pipeline in which
no job qualifies fails with "No jobs to run", so a branch that only touches
documentation must produce no pipeline at all rather than an empty one.

Every job is `interruptible`, so pushing again to a branch cancels the run it
supersedes instead of leaving both to compete for runners. The project setting
that auto-cancels redundant pipelines only reaps jobs that have not started
yet — a running job needs this flag, and one job without it keeps the whole
obsolete pipeline alive. The `import` job is the exception: publishing to
Galaxy must not be cut in half.

That gap is where the bugs come from. Three examples, all shipped through a
green pipeline: a Jinja syntax error in `sshd_config.j2` that broke every
managed host, `system_portage_kernel: auto` compiling a kernel for 45 minutes
instead of using the binhost, and the `eclean-kernel` handler exiting 1 on a
zstd initramfs.

So when a change touches one of the uncovered areas, run the matching scenario
on a workstation before merging, and say so in the merge request. Reviewing it
against a green pipeline alone is reviewing nothing.

Running those scenarios in CI was considered and turned down (see the issue
tracker): it would need either a self-hosted runner — a personal machine that
has to be up, and that would execute contributor code from forks — or a paid
cloud runner with nested virtualisation. Neither is worth it for this role
today.

libvirt connection and storage pool
-----------------------------------

Scenarios that drive libvirt via its API (e.g. `facts`) honour two environment
variables, with sensible defaults when unset:

| Variable               | Default          | Purpose                         |
| ---------------------- | ---------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system` | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`        | name of the storage pool to use |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL`
is local to this project but follows the same naming convention. Both are
forwarded into the molecule container by the wrapper (any `LIBVIRT_*` env var
is passed through).

Recommended setup if the system pool sits on a small partition: create a
dedicated pool on a larger filesystem and point molecule at it. For example:

```sh
install -d -m 2775 -g qemu $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-define-as molecule dir --target $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-autostart molecule
virsh -c qemu:///system pool-start molecule

export LIBVIRT_DEFAULT_POOL=molecule
molecule test -s facts
```

The directory must be reachable by the `qemu` user (group `qemu` + setgid
parent works, provided your user is in `qemu`).

`qemu:///session` is currently *not* supported by these scenarios: session
mode has no built-in `default` network, and `virsh net-dhcp-leases` would not
find any lease. If you want to view VMs in a GUI without switching to session
mode, point GNOME Boxes (>=41) at `qemu:///system` or use `virt-manager`,
which lists both URIs side by side.

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Adding a new distribution or version
------------------------------------

The list of officially supported platforms lives in [`molecule/shared/platforms.yml`][platforms].
It is the single source of truth for both Molecule (cloud image URL per platform)
and Galaxy (`galaxy_info.platforms` in `meta/main.yml`).

After editing `molecule/shared/platforms.yml`, run the sync script to refresh
`meta/main.yml`:

```sh
python3 scripts/sync-meta-platforms.py
```

Each scenario's `molecule.yml` then picks a subset of those platforms by name
(plus any `groups` / `memory` override); the cloud image URL is resolved at
runtime by `create.yml` via a `lookup` on `molecule/shared/platforms.yml`.
`molecule/shared/` also hosts the `create.yml` / `destroy.yml` playbooks that
each VM scenario symlinks; molecule ignores it as a scenario because it doesn't
carry a `molecule.yml`.

Container scenarios don't go through `platforms.yml`: their shared
`molecule/containers/molecule.yml` names a `gwerlas/ansible-guest-*` image and
tag directly, and the containers driver brings its own create / destroy
playbooks. Keep both lists in step when adding a distribution — a platform is
only really supported once it passes in a VM *and* in a container.

Editing templates
-----------------

No CI job renders the role's templates: the container scenarios skip the tasks
that use them (`system_manage_sshd` is false in a container, and so on), and
`ansible-lint` does not read `.j2` files. A template broken at the syntax level
would otherwise ship through a green pipeline — it already happened once, with
a duplicated `{% endif %}` in `templates/ssh/sshd_config.j2`.

The `j2lint` job lints them, and only runs when a template changes. To
reproduce it locally:

```sh
pip install j2lint==1.3.0
j2lint templates/ --ignore jinja-statements-indentation
```

`jinja-statements-indentation` is ignored for the whole role: it expects nested
`{% %}` to be indented, which would reshape every configuration template
without making any of them clearer.

`single-statement-per-line` is *not* ignored globally. A template that has to
build one configuration line out of inline conditionals opts out for itself,
with this comment on its first line:

```jinja
{# j2lint: disable=single-statement-per-line -#}
```

The `-#}` matters: without it the comment leaves a blank first line in the
rendered file. Prefer this per-file opt-out to a new global ignore, so the rule
keeps applying to the templates that don't need the exception.

Linting only proves a template *compiles*. Whether it renders the right thing
is covered by the libvirt scenarios (`servers` for sshd), which run on a
workstation, so review a template change by rendering it rather than by
trusting the pipeline.

Editing documentation
---------------------

`markdownlint` checks every `*.md`, with the conventions this role already
follows recorded in `.markdownlint.yaml`:

- headings underlined for levels 1 and 2, `#` beyond — setext cannot express
  level 3 and deeper, which the docs use heavily;
- dashes for list bullets;
- 80 columns for prose. Tables and code blocks are exempt: aligning a table's
  cells is worth more than fitting the width, and wrapping a command would
  break it.

To run it locally:

```sh
markdownlint-cli2 "**/*.md"
```

It fixes much of what it finds on its own with `--fix` — bullets, indentation,
blank lines, bare URLs. What it cannot fix is line length, which is on you.

A line whose overflow contains no space is not reported: a long URL or a
reference-style link definition has nothing to wrap on. That is also the way
out when a link makes a sentence overflow — move the URL to a `[name]:`
definition at the end of the file rather than splitting the link across two
lines.

Writing verify playbooks
------------------------

`with_fileglob` does not sort: it returns whatever order the filesystem gives,
which differs between a long-lived checkout and a fresh clone or a worktree.
Never index its results positionally — pick the entry you want by name, the way
`molecule/servers/verify.yml` matches each SSH host key fixture to its key type.
Otherwise the scenario passes on your machine and fails on everyone else's.

Submit your changes
-------------------

Merge request in [Gitlab][].

<!-- Links section -->
[Gitlab]: https://gitlab.com/yoanncolin/ansible/roles/system/-/merge_requests
[j2lint]: https://github.com/aristanetworks/j2lint
[markdownlint-cli2]: https://github.com/DavidAnson/markdownlint-cli2
[platforms]: molecule/shared/platforms.yml
