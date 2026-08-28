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

The cache refresh tasks carry `molecule-idempotence-notest`, so the second run
keeps the index the first one left. A mirror publishing mid-scenario would
otherwise move the versions the `state: latest` tasks see. That freeze is a
property of the test, and never a reason to raise `system_packages_cache_age`:
bending the production default is what let a stale index reach an install.

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
| System upgrade (`system_packages_upgrade`)      | no                     | `future`                        |
| `system_profile` resolution                     | yes, container jobs    | `containers-facts`              |
| Desktop profiles, once installed                | no                     | `desktops`, `gnome`             |

That gap is where the bugs come from. Three examples, all shipped through a
green pipeline: a Jinja syntax error in `sshd_config.j2` that broke every
managed host, `system_portage_kernel: auto` compiling a kernel for 45 minutes
instead of using the binhost, and the `eclean-kernel` handler exiting 1 on a
zstd initramfs.

So when a change touches one of the uncovered areas, run the matching scenario
on a workstation before merging, and say so in the merge request. Reviewing it
against a green pipeline alone is reviewing nothing.

Running those scenarios in CI was considered and turned down ([issue #5][]):
it would need either a self-hosted runner — a personal machine that has to be
up, and that would execute contributor code from forks — or a paid cloud runner
with nested virtualisation. Neither is worth it for this role today.

### When each job runs

`workflow:` only decides whether a pipeline exists — on a branch or a tag.
Each job then declares what it depends on:

| Job                | Runs when                                |
| ------------------ | ---------------------------------------- |
| `ansible-lint`     | any of the role's YAML changed           |
| `j2lint`           | a `templates/**/*.j2` changed            |
| `markdownlint`     | a `*.md` or the linter config changed    |
| the container jobs | the role's code or its scenarios changed |

Two consequences are worth knowing before you read a pipeline:

- everything is compared against `main`, and against the **branch as a whole**,
  not the latest push. A branch that touches the role's code runs the scenarios
  on each of its pushes, documentation-only commits included. Only a branch that
  never touches anything but documentation comes down to `markdownlint` alone;
- on `main` and on tags, every job runs unconditionally.

Why the rules are written the way they are — why `compare_to` is spelled out,
why `workflow:` keeps a path list of its own, why every job but `import` is
`interruptible` — is commented in `.gitlab-ci.yml`, next to the lines concerned.

### Pipelines on a fork

A merge request from a fork runs its pipeline in the fork, on the fork's own
repository and runner minutes: `workflow:` matches branches and tags, never
`merge_request_event`.

`compare_to: refs/heads/main` therefore resolves against the *fork's* `main`,
from the merge base. Branch off your own `main`, however far behind, and only
your own commits are compared; sync the branch with this project while that
`main` stays behind, and every job qualifies. Wasteful, never wrong.

A fork with no `main` at all is the case with no signal: the rules report
`rules:changes:compare_to is not a valid ref`, and `workflow:` creates no
pipeline while saying nothing. `compare_to` expands CI/CD variables, so
`$CI_DEFAULT_BRANCH` is the fix on hand if that ever bites.

libvirt connection and storage pool
-----------------------------------

Scenarios that drive libvirt via its API (e.g. `facts`) honour four environment
variables, with sensible defaults when unset:

| Variable               | Default              | Purpose                         |
| ---------------------- | -------------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system`     | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`            | name of the storage pool to use |
| `MOLECULE_MEMORY`      | the platform's value | GB of RAM per VM                |
| `MOLECULE_VCPUS`       | the platform's value | vCPUs per VM                    |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL`
is local to this project but follows the same naming convention. Both are
forwarded into the molecule container by the wrapper (any `LIBVIRT_*` env var
is passed through).

`MOLECULE_MEMORY` and `MOLECULE_VCPUS` override what the scenario asks for,
which is what you want when a run compiles rather than installs. They apply to
every platform of the run, so pair them with `-p`: a scenario like `default`
creates twelve VMs, and twelve times twelve gigabytes is not a number your
workstation has.

```sh
MOLECULE_MEMORY=16 MOLECULE_VCPUS=8 molecule test -s future -p gentoo
```

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

Target properties: `vars/` files and issue labels
------------------------------------------------

`tasks/facts.yml` reads a handful of properties off the target — package
manager, service manager, OS family, distribution, major version, release —
and loads `vars/<value>.yml` for each one it finds, from the least specific to
the most. The last file loaded wins.

So a value lives in the file named after the property it is *actually* true
of, and the narrowest one that still covers every target it applies to.
Something true of every pacman system belongs in `pacman.yml`, not copied into
`archlinux-like.yml`; something true of Gentoo's package manager belongs in
`portage.yml`, and something true of Gentoo hosts whatever their tooling in
`gentoo-like.yml`. Because the cascade runs from least to most specific,
refining a value at a narrower level is deliberate — `debian-like.yml` can set
a default that `ubuntu-jammy.yml` overrides. What to avoid is setting the same
value at two levels by accident: the wider one is then silently dead.

The axis is a property of the **target**, never of this repository's own
layout.

Issue labels follow the same rule, one step wider: an issue carries what it is
true *of*. For the role's behaviour that is a property of the managed host —
`pacman` for something in the pacman layer, `gentoo` for something true of
Gentoo hosts whatever their tooling. For the project's own machinery it is the
thing impacted, which is why `ci` and `molecule` exist. What an issue never
carries is the directory it happens to touch: there is deliberately no
`package-managers` label, because `tasks/package-managers/` is a property of
this repository and not of anything the role acts on. An issue true of every
target — `tasks/package-managers.yml` carrying no tag, say — carries no
dimension label at all, and that absence is the correct answer rather than an
oversight. On top of that, one label for the kind: `bug`, `feature` or
`tech-debt`.

Labels are created on demand and never in advance, so the list only ever
holds what some issue actually needed. Creating one takes project permissions
a contributor does not have, and no bot does it today: if none of the existing
labels fits, say so in the issue and a maintainer will add it.

Editing templates
-----------------

No CI job renders the role's templates: the container scenarios skip the tasks
that use them (`manage_sshd` resolves to false in a container, and so on), and
`ansible-lint` does not read `.j2` files. The `j2lint` job lints them, and only
runs when a template changes. To reproduce it locally:

```sh
pip install j2lint==1.3.0
j2lint templates/ --ignore jinja-statements-indentation
```

`jinja-statements-indentation` is ignored for the whole role.
`single-statement-per-line` is *not*: a template that has to build one
configuration line out of inline conditionals opts out for itself, with this
comment on its first line:

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

### Markdown conventions

`markdownlint` checks every `*.md`. The conventions this role follows — setext
headings for levels 1 and 2, dashes for bullets, 80 columns for prose with
tables and code blocks exempt — are recorded, with their rationale, in
`.markdownlint.yaml`. To run it locally:

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

### Where a rationale lives

A reason is written in exactly one place. From the narrowest home to the
widest:

| Home                     | What it holds                                          |
| ------------------------ | ------------------------------------------------------ |
| Code comment             | what this line does, and under which rule              |
| `CONTRIBUTING` / `docs/` | what the reader has to be able to predict or do        |
| Commit message           | what changes, and why now                              |
| Issue / merge request    | the derivation, the measurements, the paths not taken  |
| Upstream documentation   | the rule itself, whenever the rule is not ours         |

Two of those are easy to get wrong, and both make comments longer than they
need to be.

**Cite upstream, never re-derive it.** When the reason is a third-party tool's
behaviour — Portage, apt, systemd, dracut, sshd, Jinja — the rule already has a
home, and it is not this repository. Quote one sentence, give the URL, stop.
A reconstruction of your own goes stale without warning the day upstream
changes its mind, and it reads as an opinion of this role when it is in fact an
external constraint. Look the source up *before* writing the comment: done the
other way round, you produce a careful demonstration of something that fits in
one quotable line, and you miss whatever else that page says.

**A comment summarises, it does not narrate.** It says what the line does and
under which rule. The investigation that led there — when it was observed, what
was measured, which false trail was followed — belongs to the issue and the
commit message, where someone doing archaeology will go looking for it.
The test is mechanical: remove everything written in the past tense. What falls
out did not belong in a comment; what is left is the rule.

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

A change comes with its tests and its documentation, in the same commit. A new
variable, or a change in behaviour, is not finished until:

- a molecule scenario exercises it — an existing one where it fits, `servers`
  for anything sshd, `default` for the role's own defaults;
- the user-facing half is written in `README.md` or under `docs/`: what the
  variable does, its default, an example;
- the reasoning a future maintainer will need — an upstream constraint, a
  Portage quirk, why two tasks must run in that order — goes in a code comment
  or in this file, not in the user documentation.

Keeping the three together is what makes a commit reviewable on its own: a
change that arrives without its test looks finished when it is not, and one
that arrives without its reason forces the next reader to guess.

The issue is referenced from the commit body, and only from there. `Closes #14`
if the commit settles the whole ticket; a bare `#14` if it settles one of the
three things the ticket asks for, so the other two stay visible. Neither
`README.md` nor `docs/` ever carries an issue number — a user can do nothing
with it, and it goes stale the day the issue closes. The exception is a
decision a contributor may want to reopen, linked from this file the way
[issue #5][] is above.

Tagging a release
-----------------

A tag publishes. The `import` job pushes the role to Ansible Galaxy and runs
on a protected tag and nowhere else, so the number you pick is the only thing
telling users what upgrading will cost them.

What that number answers is not what the work *was*, it is what the contract
*does*. Intuition reaches for "we only fixed things, so it is a patch", and
that is the wrong test. The right one:

> Does someone who upgrades without editing a single variable get the same
> result as before?

**Yes** — a defect stops happening and nothing a user can name changed shape:
patch. **No** — a default's value or its type changed, a variable means
something new, a documented variable or profile appeared, output someone might
read moved: minor. A branch answers "no" as a whole, so it is a minor even
when every commit in it is a fix.

`system_manage_sshd` moving to `auto` in `0.21.0` is the case worth
remembering: no new feature, and it still turned a boolean into a truthy
string for anyone testing that variable from their own playbook.

The history already works this way, it was just never written down. Each patch
so far carries exactly one commit — `0.18.1` changed a default, `parted`'s
resize to `false`, and stayed a patch because it changed one thing nobody else
could reference. Minors carry batches, 48 commits in `0.19.0` and 19 in
`0.20.0`, and a batch nearly always holds a contract change.

While the role is at `0.x` there is no major: a breaking change rides in a
minor, and every contract change gets its line in the release notes. That line
is what a user has instead of a version number that would have warned them.

<!-- Links section -->
[Gitlab]: https://gitlab.com/yoanncolin/ansible/roles/system/-/merge_requests
[issue #5]: https://gitlab.com/yoanncolin/ansible/roles/system/-/issues/5
[j2lint]: https://github.com/aristanetworks/j2lint
[markdownlint-cli2]: https://github.com/DavidAnson/markdownlint-cli2
[platforms]: molecule/shared/platforms.yml
