# Contributing

> **Not accepting contributions yet.** Thank you for your interest in Fylgja. Fylgja is not
> taking outside issues or pull requests yet; this page will say when that changes. This page
> describes how the repository itself works. A security concern is always welcome, as
> [fylgja-core's SECURITY.md](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/SECURITY.md) describes.

How to set up, test and change fylgja-examples, which holds the example orchestrator and the two
demonstrations of [fylgja-core](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/README.md). The design they follow lives there: the system in
[architecture.md](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/architecture.md), the rules every change keeps in the
[constitution](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/constitution.md), and the reasons in its [decision
log](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md). This repository's own decisions are in
[design/decisions.md](design/decisions.md), and what it read for itself in
[design/verified-facts.md](design/verified-facts.md). Read fylgja-core's
[verified-facts.md](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/verified-facts.md) for what has been verified against
containerlab, Infrahub, NetBox, Prefect and the network operating systems, with versions and
dates. [Integrating Fylgja](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/docs/integrating.md) walks through this example.

This repository installs the released packages `fylgja-core`, `fylgja-infrahub` and
`fylgja-netbox`, each pinned exactly at `VERSION`, from PyPI, and reads no path of a fylgja-core
checkout ([E-001](design/decisions.md#e-001)). The example orchestrator is under `orchestrator/`,
and the development Infrahub and NetBox it is run against are under `infrahub/` and `netbox/`.

## Setting up

You need Python 3.14 and uv 0.12.23. `make demo-dependencies` installs that uv, and the rest
the demonstrations need, where it is missing, and checks the system's Python, which it never
installs.

```sh
make demo-dependencies  # uv, Docker, containerlab and the host's preconditions; python3 checked
make venv               # .venv, synced from uv.lock
make lint               # ruff and mypy (strict)
make test               # the pure tier: no infrastructure
```

## How a change is made

1. **Decide.** A change that alters a decision is a new entry in
   [design/decisions.md](design/decisions.md) that supersedes the old one, or one of
   fylgja-core's that binds here. The log is append-only. Check the rejected alternatives before
   proposing one.
2. **Formats change with the code.** Each format has one current version, specified by its file
   in [`formats/`](formats/README.md). A change to a format is made there, in the same change as
   the code that reads or writes it.
3. **Verify against the running system** before code depends on how Infrahub, NetBox, Prefect,
   uv, containerlab or a network operating system behaves. Record the result, with its version
   and date, in [verified-facts.md](design/verified-facts.md).
4. **Pull request.** Conventional-commit messages whose body says *why*. The gates are
   `make lint`, `make test`, and `make linkcheck` where Markdown changed; CI runs them and
   `make wheelcheck` too.

## Tooling

| Tool | Version | Notes |
|---|---|---|
| Python | 3.14 | The system's `python3`, never one uv fetches |
| uv | 0.12.23 | Makes the environment `.venv` and the wheel check's builds and empty environments, and `infrahubctl`'s own; the root `pyproject.toml` requires exactly this version. Install exactly 0.12.23, by uv's own installer or the distribution's package, pinned to it |
| fylgja-core, fylgja-infrahub, fylgja-netbox | `VERSION` (1.0.0) | From PyPI, each pinned exactly in `orchestrator/pyproject.toml` and locked in `uv.lock`; `fylgja-core[server]` is also the `dev` extra's. Not `fylgja-nautobot`: the example has no Nautobot source |
| httpx | `>=0.27.0,<1` | The example's transport, at the core's range |
| Prefect | 3.9.2 | The example orchestrator's edge alone: the two deployments Infrahub's checks start, the second of which NetBox's webhook starts too ([D-085](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-085), [D-097](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-097)) |
| pytest, ruff, mypy | 9.2.0, 0.17.3, 2.4.0 | mypy in strict mode |
| containerlab, Docker | 0.81.0, the host's | The local driver of the demonstration's core; containerlab at the version the demonstrations were verified on |
| Infrahub, Docker Compose | 1.11.11, the host's | The development Infrahub (`make infrahub-up`): Infrahub's published Compose file for its version, fetched into `local/infrahub/` and never vendored, run by Docker's Compose plugin ([D-083](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-083)) |
| infrahub-sdk\[ctl\] | 1.23.2 | `infrahubctl`, which loads the schema library into the development Infrahub (`make infrahub-register`), in a venv of its own under `local/infrahub/` so that the SDK meets nothing else; no code of the tree imports it |
| NetBox, netbox-docker, netbox-branching | 4.7.5, 5.1.1, 1.2.3 | The development NetBox (`make netbox-up`): netbox-docker's release for its version, fetched into `local/netbox/` and never vendored, its image with one layer adding the branching plugin, built from `netbox/dev/`, run by Docker's Compose plugin ([D-096](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-096)) |

`make venv` syncs `.venv` from `uv.lock`, the uv workspace's lock at the root: the example
orchestrator, editable with every extra, and the three released distributions at the versions
the lock holds, from PyPI. A pin is moved in `orchestrator/pyproject.toml` and the lock made
again by `uv lock`, in one commit, with `VERSION` ([Moving to a release](#moving-to-a-release)).
uv's own version is written in the root `pyproject.toml`'s `required-version`, CI's `version`,
`AGENTS.md`, this file and `docs/demonstrations.md`, and moves in all of them together. A venv
inside the tree carries a `.gitignore` of `*`.

## Make targets

| Target | What it does |
|---|---|
| `make demo-dependencies` | What the demonstrations need of the host, installed where it is missing (`scripts/demo_dependencies.sh`), sudo used only for a change: git, `ss` and curl; uv at `pyproject.toml`'s `required-version`; Docker with its Compose plugin and containerlab, by containerlab's setup script, where the command is missing; the user added to `docker` and `clab_admins`; the AppArmor widening on Ubuntu. Python 3.14 and the node login in `local/.env` are checked and never installed or written. `DRY_RUN=1` prints each command that would change the host instead |
| `make venv` | The environment `.venv`, a locked `uv sync` of the workspace from `uv.lock`: the example orchestrator editable with every extra, and the three distributions from PyPI at the locked versions; a lock that disagrees with a `pyproject.toml` is refused. `CORE=<path of a fylgja-core checkout>` installs that checkout's three distributions editable over the locked ones, leaves `uv.lock` unchanged and says that the environment is no longer the lock's; `make venv` alone puts the lock back. CI never sets it |
| `make lint` | ruff over `scripts/`, `infrahub/` and `netbox/`, then ruff and mypy in strict mode over `orchestrator/`, then mypy again, apart, over `infrahub/`'s seed and tests and `netbox/`'s, since the directories of tests name modules alike |
| `make test` | The pure tier: no infrastructure. `infrahub/tests/`, `netbox/tests/` and `orchestrator/tests/`. Gates every pull request |
| `make linkcheck` | Every relative link and anchor in the tracked Markdown resolves; an absolute URL is not checked |
| `make wheelcheck` | Builds the example's wheel from `orchestrator/` and `formats/`, which carries the example's two formats and its Infrahub change source's queries, and installs it in an empty environment beside the three distributions at `VERSION` from PyPI, never built here: both change sources import, each with nothing of the other, and its command answers `--help` and `--version`. Needs the network, no Docker |
| `make infrahub-up` | The development Infrahub, the Compose project `fylgja-examples-infrahub` at `INFRAHUB_VERSION` (1.11.11), run by `scripts/infrahub_dev.py` against `local/`. It adds to `local/.env` each of its names ([`.env.example`](.env.example)) that the file does not hold, generated and never printed, and changes no line already there, since a token made again would not open the kept database; a name the file holds with no value is refused, exit 2 and before anything is fetched or started. Waits until `GET /api/info` answers the version |
| `make infrahub-down` | Stops the development Infrahub, each container given 60 s to exit by itself. Its containers, network and volumes and everything under `local/infrahub/` are kept, and `make infrahub-up` starts it again holding what it held. `PURGE=1`, and no other value, removes the containers, the network and the volumes, and `local/infrahub/seed.json` with them |
| `make infrahub-register` | The schema library, the group and this repository's registration on the development Infrahub's `main` (`infrahub/seed/register.py`), at `REF`, the branch checked out, and that branch's commit; an empty `REF`, a detached head, is refused in one line. The library under `infrahub/schema/dcim/` is loaded by `infrahubctl` where `main` holds none of its kinds. It then waits until each task worker holds the tree of the registered commit |
| `make infrahub-seed` | The fixture network on the development Infrahub's `main`, and the branch `SEED_BRANCH` (`third-link`) with its two staged edits, each regenerated, timed and marked, and with `PROPOSED_CHANGE=1` its proposed change (`infrahub/seed/seed.py`). Refused with nothing written where `main` holds no artifact definition `device-config` (run `make infrahub-register` first). It writes `local/infrahub/seed.json` |
| `make netbox-up` | The development NetBox, the Compose project `fylgja-examples-netbox` on the subnet 192.0.2.0/24: NetBox `NETBOX_VERSION` (4.7.5) on netbox-docker `NETBOX_DOCKER_VERSION` (5.1.1) with netbox-branching `NETBOX_BRANCHING_VERSION` (1.2.3), run by `scripts/netbox_dev.py` against `local/`. It adds to `local/.env` each of its names that the file does not hold, the secrets generated and never printed, and changes no line already there; a name held with no value is refused. Waits until `/api/status/` names both versions and a running worker, and provisions the superuser's token into `local/.env` where it holds none or NetBox refuses it |
| `make netbox-down` | Stops the development NetBox, each container given 60 s to exit by itself. Its containers, network and volumes and everything under `local/netbox/` are kept. `PURGE=1`, and no other value, removes the containers, the network and the volumes; `local/.env`, the release and the image stay, and the next `make netbox-up` provisions the superuser's token again |
| `make netbox-seed` | The fixture network on the development NetBox's `main` (`netbox/seed/seed.py`), each object found by its name or made, `main` read back and refused, naming each difference and deleting nothing, where it is not the fixture; then the accounts `fylgja-reader` and `fylgja-orchestrator` at their least grants and their tokens' lines in `local/.env` (`netbox/seed/account.py`), each kept where NetBox holds its token as that account's and made again where it does not |
| `make netbox-hook` | The trigger on the development NetBox (`netbox/seed/hook.py`, [D-097](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-097)): the tag `fylgja-rehearse`, limited to branches, the webhook `fylgja-rehearse` that starts `twin-rehearse/main` on the edge's Prefect, and the event rule that sends it when a branch carrying the tag is updated, each found by its name or made. The webhook names the deployment by its id, so it runs once the runner serves |
| `make netbox-change` | The seeded change on the development NetBox (`netbox/seed/change.py`): the branch `NETBOX_BRANCH` (`third-link`), deleted where it stands with every journal entry on it and made anew from `main`, its two steps written and each marked by the example's own `stage mark`, which needs the core running. `NETBOX_TAG=1`, and no other value, sets the tag `fylgja-rehearse` last, which asks for the rehearsal |
| `make orchestrator-env` | The example orchestrator's lines in `local/.env` (`scripts/edge_dev.py env`), each written only where the file lacks it or holds it empty, printed by its name and never its value: the basic auth the edge's Prefect, the task workers and NetBox's webhook share, the runner's token of the core's, its hash appended with the principal `orchestrator` to the token file `FYLGJA_TOKENS` names (refused with nothing written where that names no file), the scope, the reader documents and the records' directory; then, but with `SOURCE=netbox`, its Infrahub account and that account's token. The core is restarted after it, to read the new line |
| `make prefect-up` | The edge's Prefect (`scripts/edge_dev.py prefect-up`), `.venv`'s `prefect server start`, on port 4200 of the Docker bridge's gateway, or `PREFECT_BIND`; in a session of its own under `local/prefect/`, its basic auth given in its environment and never as an argument; waited for until `/api/health` answers. Refused, with nothing started or stopped, where anything else listens on port 4200 |
| `make prefect-down` | Ends the server `local/prefect/server.pid` names, only where that process is this project's Prefect server, and no other process |
| `make orchestrator-serve` | The runner of the change source `SOURCE`, `infrahub` where not given, or `netbox` ([D-097](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-097)), `.venv`'s `fylgja-orchestrator serve`, in the foreground until Ctrl-C, serving `stage-plan/main` and `twin-rehearse/main` to the edge's Prefect (`scripts/edge_dev.py serve --source`). It is given its own tokens of that source and none of any other. Load `local/.env` first |
| `make contract` | The contract tier (below) against the running, registered and seeded development Infrahub: `infrahub/tests/contract/`, then `orchestrator/tests/contract/`. Load `local/.env` first |
| `make contract-netbox` | The NetBox contract tier (below) against the running, seeded development NetBox: `netbox/tests/contract/`, then `orchestrator/tests/contract_netbox/`. Load `local/.env` after `make netbox-seed` |
| `make infrahub-demo` | A demonstration with the development Infrahub, with no step by hand (`scripts/demo.py up infrahub`, [D-104](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-104)): the host's preconditions are checked, what an earlier run left is ended, the development NetBox is stopped where it is up, the room is checked, then the steps of [Running the example orchestrator](#running-the-example-orchestrator) are taken in order through their own targets, the seed last with its proposed change, and the verdict is read from the rehearsal's document. Exit 0 for `passed` alone. See [The demonstrations](#the-demonstrations) |
| `make netbox-demo` | The same with the development NetBox (`scripts/demo.py up netbox`), the development Infrahub stopped where it is up: the steps of [With NetBox](#with-netbox), its last `make netbox-change NETBOX_TAG=1`, then the verdict read in the same way |
| `make demo-down` | Ends what a demonstration started (`scripts/demo.py down`): its runner, every twin its core holds, its core, the Prefect server it started and its source, whose volumes are kept, or removed with `PURGE=1` given on a make command line, and by no other value |

## Test tiers

| Tier | Needs | Runs |
|---|---|---|
| **Pure** | Nothing | `make test`, in CI on every push and pull request: under `infrahub/tests/`, what `infrahub/` gives Infrahub, read as files (the schema library, the registration, the Compose override, the seed's object files and stages against the fixture), the tracked tree's names and addresses and the development Infrahub's script over fakes of Compose; under `netbox/tests/` the same for NetBox; under `orchestrator/tests/` the example's own, with the core served in process by the installed `fylgja-core`: its pins held to `VERSION`, the plan and the rehearsal against their formats, the change sources over fakes, the scripts and the demonstrations over fakes of their targets, and the tree's refusal to read a path of fylgja-core |
| **Contract** | The development Infrahub, up, registered and seeded (`make infrahub-up`, `make infrahub-register`, `make infrahub-seed`), reached at `FYLGJA_INFRAHUB_ADDRESS` with the writer's token, `FYLGJA_INFRAHUB_WRITE_TOKEN`; for the example's, its account's token too, `FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN` (`make orchestrator-env`), and a Prefect server on loopback, which its tests start, with the development Prefect and runner down (`make prefect-down`) | On demand: `make contract`, with `local/.env` loaded; it sets `FYLGJA_INFRAHUB_SEED` and `FYLGJA_INFRAHUB_CTL` on its own command lines. Deselected from `make test` by the `contract` mark |
| **Contract (NetBox)** | The development NetBox, up and seeded (`make netbox-up`, `make netbox-seed`), reached at `FYLGJA_NETBOX_ADDRESS` with the superuser's token, `FYLGJA_NETBOX_WRITE_TOKEN`, and the two accounts' tokens; for the example's, nothing listening on port 4200 (`make prefect-down`) | On demand: `make contract-netbox`, with `local/.env` loaded after `make netbox-seed`. Deselected from `make test` by the `contract_netbox` mark |

A contract tier is run with the other source stopped (`make infrahub-down`, `make netbox-down`):
the two share the published ports. Development never needs Kubernetes.

## Test data

| Path | Holds |
|---|---|
| `testdata/blueprint/` | This repository's copy of the blueprints its seeds are held to, among them `three-node` and `three-node-probed`, and under `steps/` the blueprints of the seeded change's two steps. Free to change here: nothing in fylgja-core holds them ([E-001](design/decisions.md#e-001)) |
| `testdata/compiler/` | The facts the core's compiler gives each blueprint here, which the example's tests read |
| `infrahub/seed/` | The fixture network as object files `infrahubctl` loads into the development Infrahub: under `main/`, the three-node network less the link between `n1` and `n3`, and the probe `n1-loop` as a `FylgjaProbe`; under `stages/`, the seeded branch's two edits in order, that link and then the address `192.0.2.1/24` on its `n1` end; and `reader.yaml`, the reader document that maps the fixture's manufacturer and platform to the package `nokia_srlinux` and reads probes |
| `netbox/seed/` | The fixture network `make netbox-seed` puts on the development NetBox's `main`, as `main.yaml`; `template.j2`, the configuration template NetBox renders each device with; and `reader.yaml`, the reader document |
| `infrahub/schema/` | The schema library, the reader's probe kind `fylgja-probe.yml` (a copy that names its source and its commit) and the example's stage kind `fylgja-stage.yml` |
| `orchestrator/tests/fakes.py`, `boundary.py` | This repository's copies of fylgja-core's fakes and boundary list, each opening with the line that names its source and commit |

A fixture changes in a commit of its own, with the diff reviewed.

## Local environment

**uv** reads its own configuration (`~/.config/uv/uv.toml`, the `UV_*` variables). An index set
there is written into `uv.lock` by `uv lock`, and the tree's test refuses any source of a package
but PyPI's own simple index (the workspace member apart), so a lock is written
against PyPI alone. A candidate release's lock, from TestPyPI, amends that test on its own branch.

**Credentials** live in `local/.env` alone (git-ignored, mode `0600`), with the names in
[`.env.example`](.env.example).
- Load it with `set -a; . local/.env; set +a`. Fylgja reads the process environment, never a
  file.
- Never print, log or persist a token or a password.
- The node login, `FYLGJA_CREDENTIAL_SRLINUX_USERNAME` and `_PASSWORD`, and the core's own
  four settings are yours to write; every other name is made by a target.
- The core's four settings, for the core run by hand and for `make orchestrator-env`, which
  refuses with nothing written where `FYLGJA_TOKENS` is unset or names no file. Write these
  lines, or paths and an address of your own:
  ```sh
  FYLGJA_STORE=local/store
  FYLGJA_TOKENS=local/tokens
  FYLGJA_LISTEN=127.0.0.1:7650
  FYLGJA_API_ADDRESS=127.0.0.1:7650
  ```
  The token file must exist before `make orchestrator-env`. An empty one is valid, and the
  target appends the runner's line: `install -m 600 /dev/null local/tokens`. The rest of what
  these settings take is in
  [fylgja-core's docs/server.md](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/docs/server.md).
  The demonstrations need none of the four, since they use their own
  ([docs/demonstrations.md](docs/demonstrations.md)).

**The Infrahub contract tier** is made ready in this order, the four settings above written
first: `make infrahub-up`, then `local/.env` loaded, `make orchestrator-env` (it needs Infrahub up
and the token file), `local/.env` loaded again (the target writes into the file, and `make contract`
reads the shell), `make infrahub-register`, `make infrahub-seed`, `make prefect-down`, and
`make contract`. Its 11 orchestrator tests skip, without failing, while
`FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN` is unset.

**The contract tiers** read the reader's `FYLGJA_INFRAHUB_ADDRESS`, `FYLGJA_INFRAHUB_TOKEN` and,
where it is set, `FYLGJA_INFRAHUB_CA`; and `FYLGJA_INFRAHUB_WRITE_TOKEN`, the admin's, for their
own writer. `make contract` sets the other two on its command lines: `FYLGJA_INFRAHUB_SEED`,
`local/infrahub/seed.json`, and `FYLGJA_INFRAHUB_CTL`, the `infrahubctl` of `local/infrahub/.venv/`.

**The readers' commands**, `fylgja-infrahub` and `fylgja-netbox`, are installed by `make venv` in
`.venv/bin/`, and read their address and token from the environment, never a flag
([fylgja-core's Infrahub reader](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/readers/infrahub/README.md#the-command), [its NetBox
reader](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/readers/netbox/README.md#the-command)). Against the development source, seeded, a
blueprint is read into a file under `local/`:

```sh
set -a; . local/.env; set +a
.venv/bin/fylgja-infrahub schema-check --branch main
.venv/bin/fylgja-infrahub read --branch third-link --scope tag:fylgja \
  --reader infrahub/seed/reader.yaml --out local/third-link.json
.venv/bin/fylgja-netbox check
.venv/bin/fylgja-netbox read --scope tag:fylgja --reader netbox/seed/reader.yaml \
  --out local/main.json
```

**The names a target writes into `local/.env`,** generated where secret, never printed, and kept where already
there:
- `make infrahub-up` writes Compose's `INFRAHUB_INITIAL_ADMIN_TOKEN` (the admin's first API token, taken at Infrahub's
  first start), `INFRAHUB_INITIAL_AGENT_TOKEN` (the agent's, which the task workers use),
  `INFRAHUB_INITIAL_ADMIN_PASSWORD` (for the web interface), `INFRAHUB_SECURITY_SECRET_KEY` (the key Infrahub signs a
  login's tokens with) and `INFRAHUB_TELEMETRY_OPTOUT` (`true`), and `FYLGJA_INFRAHUB_ADDRESS`,
  `FYLGJA_INFRAHUB_WRITE_TOKEN` (the admin token's value) and `FYLGJA_INFRAHUB_TOKEN` (the reader's). A token made
  again would not open the kept database, so a line already there is never changed. `FYLGJA_INFRAHUB_CA` is never
  written: the CA bundle an `https://` address is verified against, the system's trust where unset.
- `make netbox-up` writes `FYLGJA_NETBOX_SUPERUSER_PASSWORD`, `FYLGJA_NETBOX_SECRET_KEY` and
  `FYLGJA_NETBOX_API_TOKEN_PEPPER` (Compose's: the superuser `admin`'s password, NetBox's secret key and the pepper of
  its tokens; a pepper made again would refuse every token a kept database holds), `FYLGJA_NETBOX_ADDRESS` and
  `FYLGJA_NETBOX_WRITE_TOKEN`. `make netbox-seed` writes `FYLGJA_NETBOX_TOKEN` and
  `FYLGJA_ORCHESTRATOR_NETBOX_TOKEN`. `FYLGJA_NETBOX_CA` is never written: the CA bundle an `https://` address is
  verified against; the development NetBox is served over http.
- `make orchestrator-env` writes `FYLGJA_ORCHESTRATOR_AUTH` (the basic auth `fylgja:<password>` the edge's Prefect, the
  task workers and NetBox's webhook share), `FYLGJA_ORCHESTRATOR_API_TOKEN` (the runner's token of the core's),
  `FYLGJA_ORCHESTRATOR_SCOPE` (the scope the stages are read under, `tag:fylgja`), `FYLGJA_ORCHESTRATOR_READER`
  (`infrahub/seed/reader.yaml`), `FYLGJA_ORCHESTRATOR_ROOT` (the directory the commands keep their records under,
  `local/orchestrator`), `FYLGJA_ORCHESTRATOR_NETBOX_READER` (`netbox/seed/reader.yaml`),
  `FYLGJA_ORCHESTRATOR_NETBOX_SCOPE` and, with Infrahub, `FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN`.
  `FYLGJA_ORCHESTRATOR_SOURCE` (`infrahub` where unset, or `netbox`) is no target's: `scripts/edge_dev.py`'s `serve` and
  `run` set it from their `--source`, whatever `local/.env` holds.

**The demonstrations** need Docker and containerlab, with the user in the `docker` and
`clab_admins` groups, and the SR Linux image (`ghcr.io/nokia/srlinux:24.7.1`, public).
On Ubuntu, SR Linux's `rsyslogd` needs an AppArmor widening
([fylgja-core's facts](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/verified-facts.md)). [docs/demonstrations.md](docs/demonstrations.md)
lists every precondition.

## The development Infrahub

One Infrahub at a stated version runs on the development host as the Compose project
`fylgja-examples-infrahub` ([D-083](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-083)), behind the make targets above.
It is brought up, given this repository and seeded in this order. `make infrahub-up` needs none
of `local/.env`'s names in the shell, and writes the names the others read into it, so the file is
loaded after it: before its first run the file lacks them, or does not exist.

```sh
make infrahub-up          # the project started, its secrets added to local/.env
set -a; . local/.env; set +a
make orchestrator-env     # needs the token file; adds the example's lines, its Infrahub token among them
set -a; . local/.env; set +a
make infrahub-register    # the schema library, the group, and this repository at REF
make infrahub-seed        # the fixture network on main, and the branch third-link with its two stages
make prefect-down         # the contract tier starts a Prefect of its own
make contract             # the contract tier against it
```

- Docker picks the subnet of its Compose network, a /16. Where that holds the lab pool a
  demonstration takes, set `FYLGJA_LAB_POOL` in `local/.env`
  ([docs/demonstrations.md](docs/demonstrations.md), "A lab pool no Docker network holds whole");
  no subnet is fixed here.
- fylgja-core's development Infrahub and NetBox take the same ports as these and are never
  stopped from here: stop them from fylgja-core's checkout. A demonstration here refuses only
  the source whose port it needs (8000 for Infrahub, 8800 for NetBox), so one source at a time
  across the two repositories is yours to keep.
- `make infrahub-down` stops it, keeping its containers, network and volumes and everything under
  `local/infrahub/`, so that `make infrahub-up` starts it again holding what it held.
  `make infrahub-down PURGE=1` removes the containers, the network, the volumes and
  `local/infrahub/seed.json`; `local/.env`, the fetched Compose file and `infrahubctl`'s venv
  stay, and the next start is an empty Infrahub, to register and seed again.
- Infrahub imports a later commit of this repository only when asked: `make infrahub-register`
  imports `REF`'s last commit where the registration reads another. A branch runs what was
  imported before it was made ([D-088](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-088)), so `make infrahub-seed`,
  which makes its branch anew, follows every `make infrahub-register`.
- It is stopped (`make infrahub-down`) while the development NetBox runs: the two share published
  ports, and it holds about 4.5 GiB of the host's memory.
- The Compose project is named `fylgja-examples-infrahub`, so that it never meets fylgja-core's
  development Infrahub's. The ports are the same, so a host runs one of them at a time: a
  demonstration checks its ports free before it starts and stops nothing of another repository's.

## The development NetBox

One NetBox at stated versions runs on the development host as the Compose project
`fylgja-examples-netbox` ([D-096](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-096)), behind the make targets above:
NetBox `NETBOX_VERSION` on netbox-docker `NETBOX_DOCKER_VERSION`, with the branching plugin at
`NETBOX_BRANCHING_VERSION`. It is brought up and seeded in this order. `make netbox-up` needs none
of `local/.env`'s names in the shell, and writes the names the others read into it, and
`make netbox-seed` writes the two accounts' tokens into it, so the file is loaded after each:

```sh
make netbox-up            # the project started, its secrets and the superuser's token in local/.env
set -a; . local/.env; set +a
make netbox-seed          # the fixture network on main, and the two accounts with their tokens' lines
set -a; . local/.env; set +a
make contract-netbox      # the NetBox contract tier against it
```

- The seed and the contract tier write with the superuser's token, `FYLGJA_NETBOX_WRITE_TOKEN`.
  The reader and the example each run under an account of their own, no superuser, granted the
  least read on the running instance for what each does (`GRANTS` in `netbox/seed/account.py`).
  `fylgja-reader`'s token, `FYLGJA_NETBOX_TOKEN`, has `view` of what a read lists and a render's
  `render_config` on devices: it reads and renders, on `main` and under a branch, and writes
  nothing. `fylgja-orchestrator`'s, `FYLGJA_ORCHESTRATOR_NETBOX_TOKEN`, has the same, `add` on
  journal entries, any object's, and `change` on branches, any member of a branch: the writes the
  example makes with them are a journal entry on a branch and that branch's tags.
- `make netbox-down` stops it, keeping its containers, network and volumes and everything under
  `local/netbox/`, so that `make netbox-up` starts it again holding what it held.
  `make netbox-down PURGE=1` removes the containers, the network and the volumes; `local/.env`,
  the fetched release and the image stay, and the next start is an empty NetBox, to seed again.
  The three tokens `local/.env` holds are then dead: the next `make netbox-up` provisions the
  superuser's again and replaces its line, and the next `make netbox-seed` makes the two accounts
  and their tokens again and replaces their lines, every other line kept.
- The project's network is the documentation range 192.0.2.0/24, named in
  `netbox/dev/compose.override.yml`, so that it never meets the local driver's default lab pool,
  from which each twin's lab takes its subnet, nor the subnet of fylgja-core's development
  NetBox. `make netbox-up` recreates a project network that stands with another subnet: it
  removes the project's containers and network, keeps the volumes, and starts it again.
- A first start on new volumes takes about twelve and a half minutes in fylgja-core's readings,
  most of it NetBox's migrations ([fylgja-core's facts](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/verified-facts.md), "NetBox
  4.7.5 with netbox-branching 1.2.3").
- It is stopped (`make netbox-down`) while the development Infrahub runs, and up for the
  acceptance run through its tag, beside that run's twin.
- An upgrade is [D-096](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-096)'s procedure, by the three make variables
  `NETBOX_VERSION`, `NETBOX_DOCKER_VERSION` and `NETBOX_BRANCHING_VERSION`: start the new versions
  on new volumes, seed them, run the contract tier, read again the recorded facts the code leans
  on, and record what was read in [verified-facts.md](design/verified-facts.md).

## Running the example orchestrator

The example orchestrator's edge ([D-085](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-085)) runs on the development host beside the
development Infrahub or the development NetBox: a Prefect server, the runner that serves it the two flows `stage-plan`
and `twin-rehearse`, and what starts them, Infrahub's task workers, where the example's checks start them, or NetBox's
worker, where its webhook starts `twin-rehearse` ([With NetBox](#with-netbox)). With Infrahub it is set up in this
order, the core running at `FYLGJA_API_ADDRESS` with the token file `FYLGJA_TOKENS` names:

```sh
make infrahub-up            # the development Infrahub
set -a; . local/.env; set +a
make orchestrator-env       # the example's lines in local/.env, and its Infrahub account and token
# restart the core, so that it reads the runner's line in its token file
set -a; . local/.env; set +a
make infrahub-up            # the task workers recreated, given the basic auth local/.env now holds
make infrahub-register      # this repository at REF, cloned on each new task worker
make infrahub-seed          # the branch made after the registration, so it runs this commit's checks
make prefect-up             # the edge's Prefect on port 4200 of the Docker bridge's gateway
make orchestrator-serve     # the runner, in a shell of its own with local/.env loaded, until Ctrl-C
```

The core is the installed release, started in a shell of its own with the packages its wheel carries and
`FYLGJA_PACKAGES` unset (fylgja-core's D-124, to be released with 1.1.0):

```sh
set -a; . local/.env; set +a; FYLGJA_DRIVER=containerlab FYLGJA_STORE=local/store .venv/bin/fylgja-core-server
```

`make infrahub-demo` takes these steps with none by hand, the core and the runner in the background and the seed last
with its proposed change ([The demonstrations](#the-demonstrations)).

Who holds which token:

- **The runner** holds a token of the core's under the principal `orchestrator`
  (`FYLGJA_ORCHESTRATOR_API_TOKEN`) and the Infrahub account `fylgja-orchestrator`'s
  (`FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN`), given to it as `FYLGJA_API_TOKEN` and
  `FYLGJA_INFRAHUB_TOKEN`, the names the edge reads, and the basic auth as Prefect's
  `PREFECT_API_AUTH_STRING`. It is never given the admin's token.
- **The Prefect server** holds the basic auth alone, as `PREFECT_SERVER_API_AUTH_STRING`.
- **The task workers**, and so the checks, hold `FYLGJA_ORCHESTRATOR_ADDRESS`,
  `host.docker.internal:4200`, the host's name `extra_hosts` points at the bridge's gateway, and
  `FYLGJA_ORCHESTRATOR_AUTH`; no token of the core's or of Infrahub's
  (`infrahub/dev/compose.override.yml`).
- **The seed and the tests' set-up** write as the admin, `FYLGJA_INFRAHUB_WRITE_TOKEN`.

Two more things hold:

- Port 4200 is the edge's alone: `make prefect-up` refuses where anything else listens on it, and
  stops nothing. `make prefect-down` ends the server it started and no other process. The
  runner is stopped with Ctrl-C.
- A recreated task worker holds no clone of the registration, and a check run on it fails, so
  `make infrahub-register` follows every `make infrahub-up` that recreates
  them: it imports until each holds the tree of the registered commit.

### With NetBox

With NetBox ([D-097](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-097)) the edge needs nothing of Infrahub's. It is set up in this order, the
core running at `FYLGJA_API_ADDRESS` with the token file `FYLGJA_TOKENS` names:

```sh
make netbox-up                         # the development NetBox
set -a; . local/.env; set +a
make netbox-seed                       # main the fixture, and the reader's and the example's accounts and tokens
set -a; . local/.env; set +a
make orchestrator-env SOURCE=netbox    # the example's lines in local/.env, and nothing of Infrahub's run
# restart the core, so that it reads the runner's line in its token file
set -a; . local/.env; set +a
make prefect-up                        # the edge's Prefect on port 4200 of the Docker bridge's gateway
make orchestrator-serve SOURCE=netbox  # the runner, in a shell of its own with local/.env loaded, until Ctrl-C
make netbox-hook                       # the tag, the event rule and the webhook to twin-rehearse/main
make netbox-change                     # the branch third-link made from main, each of its steps marked
```

`make netbox-change NETBOX_TAG=1` sets the tag `fylgja-rehearse` on the branch last, which asks for its rehearsal, as
setting the tag in NetBox does; the rehearsal's twin is made on the core's driver. The report
is one journal entry on the branch, its kind the verdict
([fylgja-core's integrating page](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/docs/integrating.md#the-example-with-netbox-end-to-end)). `make netbox-demo` takes
these steps with none by hand, the core and the runner in the background and the change's last with its tag
([The demonstrations](#the-demonstrations)).

Who holds which token there:

- **The runner** holds a token of the core's under the principal `orchestrator`
  (`FYLGJA_ORCHESTRATOR_API_TOKEN`) and the NetBox account `fylgja-orchestrator`'s
  (`FYLGJA_ORCHESTRATOR_NETBOX_TOKEN`), given to it as `FYLGJA_API_TOKEN` and `FYLGJA_NETBOX_TOKEN`, and the basic
  auth as Prefect's `PREFECT_API_AUTH_STRING`. It is never given the superuser's token, the reader's account's or
  anything of Infrahub's.
- **The Prefect server** holds the basic auth alone, as `PREFECT_SERVER_API_AUTH_STRING`.
- **NetBox's webhook** holds the basic auth's header line in its `additional_headers`, written by `make netbox-hook`.
  `main`'s changelog holds the webhook's rows with its `additional_headers` unmasked, and an account that may view
  that changelog, the reader's and the example's among them, reads Prefect's credential there
  ([fylgja-core's integrating page](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/docs/integrating.md#credentials)). The rows outlive the webhook, so a
  value once written stays readable until a purge of the instance removes its rows. The example accepts this as a
  known limit: it is a demonstration, whose secrets sit together on a development host. A deployment that shares its
  NetBox puts a receiver of its own between NetBox and Prefect, so that Prefect's credential never enters NetBox.
- **The seed, the trigger, the change's branch, steps and tag, and the tests' set-up** write as the superuser,
  `FYLGJA_NETBOX_WRITE_TOKEN`. The change's marks are the example's own command's, under the example's token.

Three more things hold:

- One Prefect serves one source's runner: both sources' flows are served under the same two names. A run, a check's
  or the tag's, goes to whichever runner serves the name; nothing refuses a runner of the other source serving it.
  Port 4200 is the edge's alone, as above.
- `make netbox-hook` names the deployment `twin-rehearse/main` by its id, which a runner or a server restarted under
  the same home keeps and a new home changes. So it is run once `make orchestrator-serve SOURCE=netbox` serves, and
  again after every new `local/prefect/`: a webhook naming an old id is answered 404 and starts nothing, which NetBox
  shows only as a failed background task.
- A command by hand needs the runner's own tokens, which only `scripts/edge_dev.py` reads from `local/.env`, and
  nothing of Prefect's. With `local/.env` loaded:

  ```sh
  python3 -I scripts/edge_dev.py run --source netbox --local local --main . -- stage list --branch third-link
  ```

  and so `stage plan`, `twin rehearse` or `stage mark`, each with `--branch`.

What the demonstration meets:

- **A request is the tag.** One setting is one rehearsal: the flow takes the tag off before it rehearses, and its own
  untagging starts nothing. NetBox never sends a lost request again: where Prefect is down when the tag is set, the
  request is gone and the branch keeps its tag, and the tag is taken off and set again to ask again. With one worker,
  as the development NetBox runs, a setting made while a sending waits on an address that does not answer waits
  behind it.
- **Where the tag cannot be taken off**, NetBox refusing or not answering, the rehearsal is not run, the tag stays and
  no report is filed: that run did start, and shows as failed in Prefect.
- **A mark's label is unique within its branch and never taken twice**, and NetBox reads no branch as it stood
  earlier, so a past step cannot be marked again. `make netbox-change` run again for a branch deletes that branch and
  builds it again, marked anew. A change is seeded and marked once for each core: a mark's blueprint is read from the
  core the rehearsal runs through, which holds it where it was given it ([D-100](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-100)). A
  mark read under another scope is rehearsed under its own (`mark.scope`), and one whose blueprint another core holds
  through that core (`mark.unheld`). Every other remedy is a deletion in NetBox by a person who may delete journal
  entries, which the example's account may not.
- **`stage.main.gained`**, a warning on the first stage, counts what `main` gained since the branch's last sync, or
  its creation, leaving out journal entries, the branch object's own rows and the trigger's own webhook and event
  rule.

## The demonstrations

`make infrahub-demo` and `make netbox-demo` each take one source's runbook above with no step by hand, on a host that
meets their preconditions, and `make demo-down` ends what they started ([D-104](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-104)).
[docs/demonstrations.md](docs/demonstrations.md) is their page for a user: the host's preconditions, each named as the
script checks it and held to the script's own constants, the targets, the order of the steps, where the report is
read, what a run writes and leaves, and what each refusal says.

Each is `scripts/demo.py`, the standard library alone, run from the checkout the target runs in with its `local/`, as
every target's is. It is a second statement of each runbook's order, held to the blocks above by a test, and decides
nothing of a rehearsal's. The runbooks stay as the account of each step, for whoever must take a run apart.

What the page does not say, because only a contributor needs it:

- The items of the page's order are numbered there alone; the script numbers only the runbook's steps, each said
  before it is run as `step <n> of <m>: <its words>`.
- The checks no stop can cure are judged before anything is ended or stopped, so that nothing is stopped for a run
  that could never start; the memory and the ports after, since an earlier run and the other source each hold some of
  them. What an earlier run left is ended by its runner and its core by their recorded pids, each only where the pid
  still reads as that process, and every twin the demonstration's store may hold is destroyed through a core of its
  own, one started for the purpose where none is up.
- The core is started once, where each runbook says to restart it: `make orchestrator-env` has then written the
  runner's token, and the script lists the client's and the runner's in its own token file before the start. The core
  is the installed `fylgja-core-server` on the local driver, and the runner is started by the words `make
  orchestrator-serve` runs, each in a session of its own in the background, its pid recorded and its log under
  `local/demo/`, and each waited for until it answers: the core its version, the runner both deployments `READY`.
  Infrahub's seed is taken once and last, with `PROPOSED_CHANGE=1`, where its runbook seeds before Prefect is up: a
  proposed change opened before the runner serves fails its check. NetBox's change is its runbook's last step, with
  the tag. `make infrahub-up` is asked up to three times and `make infrahub-register` twice, as `STEPS` has them.
- The change's flow run is the one whose id Prefect did not list before the last step and whose branch is the
  change's; its document is read as Infrahub's check reads it.
- Every file the script writes under `local/demo/` is made at mode `0600` whatever the process's umask, and one there
  already at another mode is made `0600` when it is written again: the pid files, `source`, `unsettled`, the logs,
  `tokens`, `rehearsal.json` and `lock`. `store/` is the core's own.
- `unsettled` is written before a core is started over the store and removed only once a core of the demonstration's
  own has listed no twin, so that a run or a `down` that could not read the store never passes for one that found it
  empty.
- The core is given `local/demo/tokens` and `local/demo/store`, the local driver and the listen address, and no
  certificate, key, Lease or `FYLGJA_PACKAGES`: it loads the packages its wheel carries
  (fylgja-core's D-124, to be released with 1.1.0). Every step is given the same token file and address and no
  `FYLGJA_API_CA`.
- A make target is given no variable but its own: its environment holds none of make's own names and no name the
  `Makefile` assigns by `?=`, and its variables are those of its command line alone, so `make netbox-demo PURGE=1`,
  or a `PURGE=1` in the shell or in `local/.env`, removes no volume, the other source's stop saying `PURGE=` on its
  command line.
- `make demo-down` runs the source's `down` with `PURGE=1` only where `PURGE=1` is on that make command line, one a
  make above hands down in `MAKEFLAGS` counting as a command line's; a second `make demo-down` with nothing recorded
  running makes one `docker ps` read and runs nothing else, and with `PURGE=1` always runs the source's `down`, which
  is why `source` is kept.
- The exit statuses, as the script has them: 0, 1, 2 and 130, and through make 0 or 2, the script's status in make's
  `Error <status>` line. The page says them in prose and promises none.
- The facts behind the preconditions are in [fylgja-core's facts](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/verified-facts.md), "Ubuntu hosts" (the
  groups and the AppArmor widening) and "Infrahub 1.11.11" (the ports Compose publishes). The lab pool's variable is
  [D-103](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-103).

## The acceptance run

An acceptance run is a release's own gate ([D-117](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-117), fylgja-core's D-124, to be released with 1.1.0):
the maintainer watches a change rehearsed on a twin from where its change source starts the rehearsal, and reads the
report where that source files it, with the core on the local driver. Each written here has every command in order, how
each one's end is read and what the maintainer is asked to do:

- [Through Infrahub's check](#through-infrahubs-check): a proposed change of the branch seeded in the development
  Infrahub, rehearsed through Infrahub's own check `fylgja-twin`, its report read in the proposed change's thread.
- [Through NetBox's tag](#through-netboxs-tag): a branch built in the development NetBox in steps, each marked, then
  given its tag, rehearsed through NetBox's own webhook and Prefect, its report read on the branch's journal.

No two of them run at once: each is a live run of its own, one at a time on the host. The same rules hold for both:

- **Where.** Every command runs from the repository's root, at the head of the branch under test, with `make venv` run
  there. The registration reads a branch of this repository's `.git` by its name: `make infrahub-register` takes it as
  `REF`, by default the branch checked out, and the Infrahub run's proposed change is of the branch `make
  infrahub-seed` makes, not of `REF`. A clone at a tag is a detached head, which the Infrahub demonstration refuses
  ([D-111](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-111)): a run from a tag clones it and then `git switch -c` a branch.
- **Alone.** While it runs nothing else live runs on the host: no other twin, no contract tier, and not the other
  source. The Infrahub run is made with the development NetBox down (`make netbox-down`); the NetBox run, with the
  development Infrahub down (`make infrahub-down`), since its task workers start the deployments by name, which the
  runner of the source `netbox` serves here.
- **By pid.** A process is stopped by its pid, never by its name: another core may run on the host, on the default
  port among them, and a pattern of `pkill -f` ends the shell that sends it.
- **Credentials.** `set -a; . local/.env; set +a` in the same command as what needs it. No token or password is put on
  a command line, printed or written.
- **Output.** Each run's output goes under `local/acceptance/<run>/`. What is read holds a site's values: before any of
  it is committed, each address and host's name in it is replaced by a placeholder, and a search of each file for the
  value of each token and password in `local/.env` finds none.

### Through Infrahub's check

**Bring it up**, in the order [Running the example orchestrator](#running-the-example-orchestrator) gives, `local/.env`
loaded for each step but the first:

1. `make infrahub-up`. Its end: exit 0, once `GET /api/info` answers `1.11.11`, said as
   `infrahub_dev: Infrahub 1.11.11 answered at …`.
   It reads Compose's `INFRAHUB_*` from `local/.env`, writing those it lacks, and `FYLGJA_ORCHESTRATOR_AUTH`, which
   Compose gives the task workers.
2. Once on a host, after the first `make infrahub-up`: `make orchestrator-env`, which prints names alone; then the
   core, stopped by its pid where it runs and started again (step 6), so that it reads the runner's line in its token
   file; then `make infrahub-up` again, so that the task workers are recreated with the basic auth. After any
   `make infrahub-down PURGE=1`, `make orchestrator-env` again, since the example's Infrahub token died with the
   purged instance and the target replaces its line.
3. `make infrahub-register`, given `REF=<the branch under test>` where that is not the branch checked out, after every
   `make infrahub-up` that recreates a task worker. Its end: exit 0, with `register: fylgja reads <the branch> at
   <commit>, in-sync and online, …` and then `register: each of the 2 task workers holds the tree of fylgja at
   <commit>, …`. At 300 s it refuses, naming a worker that lacks the tree and ending `run make infrahub-register
   again`, and it is run again.
   It reads `FYLGJA_INFRAHUB_ADDRESS` and the writer's token, `FYLGJA_INFRAHUB_WRITE_TOKEN`.
4. `make infrahub-seed`, with no flag, always after the registration, since a branch runs the checks imported before it
   was made ([D-088](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-088)). Its end: exit 0, with `seed: wrote …/local/infrahub/seed.json`,
   which names the branch `third-link`, its marks `third-link` and `n1-address`, and a `proposed_change` of null.
   It reads `FYLGJA_INFRAHUB_ADDRESS`, `FYLGJA_INFRAHUB_WRITE_TOKEN` and the reader's `FYLGJA_INFRAHUB_TOKEN`.
5. `make prefect-up`. Its end: exit 0, with `edge_dev: the development Prefect answers at <the bridge's gateway>:4200,
   pid <pid>, …`, or `… is up already, pid <pid>`. It reads `FYLGJA_ORCHESTRATOR_AUTH`.
6. The core, in a shell of its own, its store, `local/store`, made at its first start and kept:

   ```sh
   set -a; . local/.env; set +a; FYLGJA_DRIVER=containerlab FYLGJA_STORE=local/store .venv/bin/fylgja-core-server
   ```

   Its end: `FYLGJA_LISTEN`'s address listened on by that process's pid (`ss -Hltnp`), and `GET /v1/version`
   answering there, which takes no token. `FYLGJA_API_ADDRESS`, where the CLI and the runner reach it, is
   `local/.env`'s, equal to `FYLGJA_LISTEN`. The core reads `FYLGJA_LISTEN`, `FYLGJA_TOKENS` and the SR Linux login,
   `FYLGJA_CREDENTIAL_SRLINUX_USERNAME` and `_PASSWORD`, from `local/.env`.
7. `make orchestrator-serve`, in a shell of its own. Its end: `fylgja-orchestrator: serving stage-plan/main,
   twin-rehearse/main at http://<the bridge's gateway>:4200/api`, and both deployments `READY` some seconds on. It reads the
   runner's own tokens, `FYLGJA_ORCHESTRATOR_API_TOKEN` and `FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN`, which it hands the runner
   as `FYLGJA_API_TOKEN` and `FYLGJA_INFRAHUB_TOKEN`; `FYLGJA_ORCHESTRATOR_AUTH`; `FYLGJA_ORCHESTRATOR_SCOPE`, `_READER` and
   `_ROOT`; and `FYLGJA_API_ADDRESS` and `FYLGJA_INFRAHUB_ADDRESS`, as loaded.

`make infrahub-demo` takes these steps itself and reads the verdict, and is the run's dry run: it ends at the proposed
change's rehearsal.

**The maintainer's act**, asked once the steps have passed: in Infrahub's UI at the development host's loopback, port
8000, reached from another machine by a forward of that port over SSH, the maintainer creates a proposed change from the
seeded branch into `main`, not as a draft, and does nothing else: no re-run of a check, no edit, no merge. The request
names the branch, `seed.json`'s `branch`, and says how to sign in: with their own credential, or as the admin with the
password `local/.env`'s `INFRAHUB_INITIAL_ADMIN_PASSWORD` holds, read from the file by them and never shown. What
follows is unasked: both checks' validators, `Check: fylgja-step` and `Check: fylgja-twin`; `fylgja-twin` concluding
when the rehearsal ends; and the report as a thread, labelled `Fylgja rehearsal`, of two comments, the summary and then
the detail. A proposed change made as a draft, or anything done to it beyond its creation, is not the run: the seed is
made again, and the maintainer asked again.

**Read the run**, read-only, once `fylgja-twin` has concluded, into the run's directory. Infrahub is read with the
writer's or the runner's token and Prefect with `FYLGJA_ORCHESTRATOR_AUTH`, each from the environment inside the
process that sends the request:

- the proposed change's creation time as Infrahub answers it, its edge's `node_metadata { created_at }`, never a clock
  of the reader's;
- by `proposed_change__ids`, the `CoreArtifactValidator` and the two `CoreUserValidator`s, each with its `state`,
  `conclusion`, `started_at` and `completed_at`: the `fylgja-twin` validator is expected within 120 s of the creation,
  both checks concluding `success`. Where 120 s pass with none, the run is waited for and read, never started again;
- each task worker's log over the run (`docker logs`), and whether a check met a worker lacking the commit's tree
  (`NodeNotFoundError`);
- the thread: `CoreChangeThread` by `change__ids`, its label, and its `CoreThreadComment`s in the order of their edges'
  `node_metadata { created_at }`, each comment's `text` saved byte for byte to a file of its own;
- the rehearsal document: the deployment's id by `GET /api/deployments/name/twin-rehearse/main`, its runs by `POST
  /api/flow_runs/filter` on that id, the one begun after the creation with its state and times, then that run's
  document by `POST /api/artifacts/filter` on the run's id and the type `fylgja-document`, keyed
  `fylgja-twin-rehearse-<run id>`: its `status`, `took_s` and `twin`, each stage's `result`, and its findings;
- `fylgja-core twin list`.

Whether the run is the one the criterion names is read from the document's `status` and its stages' `result`s, never
from the check's colour.

**Clean up**, read-only but for what each step names:

- `fylgja-core twin list` empty. A rehearsal asks its twin's deletion and reads it until it is gone, for 120 s, and
  names one still there in its report (`rehearsal.twin.left`). So the twin the document names, `rh-…`, is read with
  `fylgja-core twin show <twin>` until it answers that the twin is not found, and one that stays is destroyed by
  `fylgja-core twin destroy <twin>`.
- A dry run's proposed change is removed with its branch and its marks by `make infrahub-seed`, which deletes the
  branch's open proposed change and its marks before it makes the branch anew.
- A maintainer's proposed change is left open and unmerged until what was read of its run has passed review, then
  closed: `CoreProposedChangeUpdate` with `state` `closed`, sent with the writer's token. None is ever merged: a merge
  moves `main` under the fixture.
- When the work is done: the runner stopped by its pid, and the core by its pid, the listener of `FYLGJA_LISTEN`; then
  `make prefect-down` and `make infrahub-down`.

### Through NetBox's tag

**Bring it up**, in the order [With NetBox](#with-netbox) gives, `local/.env` loaded for each step but the first:

1. `make netbox-up`. It needs none of `local/.env`'s names in the shell: it adds to the file those of its own it
   lacks. Its end: exit 0, once `/api/status/` names both versions and a running worker, said as `netbox_dev: NetBox
   4.7.5 with netbox_branching 1.2.3 answers at http://127.0.0.1:8800, <n> worker(s) running`; without a running
   worker it fails, since then no branch is ever ready. It writes the superuser's token, `FYLGJA_NETBOX_WRITE_TOKEN`,
   where the file holds none or NetBox refuses it. It needs none of `local/.env`'s names in the shell.
2. `make netbox-seed`. Its end: exit 0, with a line for each object of the fixture, `made` or `found` and its path,
   then a line for each account, grant or token it made, set or replaced. Where `main` is not the fixture it says each
   difference and exits 1, deleting nothing. It reads `FYLGJA_NETBOX_ADDRESS` and the superuser's
   `FYLGJA_NETBOX_WRITE_TOKEN`, and writes the two accounts' token lines, so `local/.env` is loaded again
   after it.
3. The core on the local driver, in a shell of its own, started as the run through Infrahub's check starts it.
4. `make orchestrator-env SOURCE=netbox`, which runs nothing of Infrahub's and needs no Infrahub. Its end: exit 0,
   printing names alone; it reads `FYLGJA_TOKENS` only where it adds `FYLGJA_ORCHESTRATOR_API_TOKEN`; where it added that, it lists the token's hash under the
   principal `orchestrator` in the token file `FYLGJA_TOKENS` names and says to restart the core: the core is then
   stopped by its pid and started again by step 3, and `local/.env` loaded again.
5. `make prefect-up`. Its end: exit 0, with `edge_dev: the development Prefect answers at <the bridge's
   gateway>:4200, pid <pid>, …`, or `… is up already, pid <pid>`. Where anything else listens on port 4200 it refuses,
   starting and stopping nothing. It reads `FYLGJA_ORCHESTRATOR_AUTH`.
6. `make orchestrator-serve SOURCE=netbox`, in a shell of its own, `local/.env` loaded in the same command. Its end:
   `fylgja-orchestrator: serving stage-plan/main, twin-rehearse/main at http://<the bridge's gateway>:4200/api`, and
   both deployments `READY` some seconds on. It reads the runner's own tokens, `FYLGJA_ORCHESTRATOR_API_TOKEN` and
   `FYLGJA_ORCHESTRATOR_NETBOX_TOKEN`, which it hands the runner as `FYLGJA_API_TOKEN` and `FYLGJA_NETBOX_TOKEN`;
   `FYLGJA_ORCHESTRATOR_NETBOX_READER` and `_NETBOX_SCOPE`, handed on as `FYLGJA_ORCHESTRATOR_READER` and `_SCOPE`;
   `FYLGJA_ORCHESTRATOR_ROOT` and `FYLGJA_ORCHESTRATOR_AUTH`; and `FYLGJA_API_ADDRESS` and `FYLGJA_NETBOX_ADDRESS`, as
   loaded. A name it needs not set is one line naming it and the target that writes it, exit 2.
7. `make netbox-hook`, once the runner serves, since the webhook names the deployment `twin-rehearse/main` by the id
   Prefect answers for it. It reads `FYLGJA_NETBOX_ADDRESS`, the superuser's `FYLGJA_NETBOX_WRITE_TOKEN` and
   `FYLGJA_ORCHESTRATOR_AUTH`. Its end: exit 0, with a line for each part of the trigger it made or wrote again, or `hook:
   the tag, the webhook and the event rule fylgja-rehearse stand; nothing made or changed`. The trigger stays
   installed from one run to the next.

After `make netbox-down PURGE=1`, which cannot be undone and is the maintainer's word alone, never a step of a run, the
three NetBox tokens `local/.env` holds are dead. The bring-up is then: `make netbox-up`; `local/.env` loaded again;
`make netbox-seed`; `local/.env` loaded again; `make netbox-hook`, with Prefect up, since the new instance holds no
trigger; and the runner stopped by its pid and started again by step 6, since it holds the example's token of the
purged instance.

**The change and its tag.** In one command after `set -a; . local/.env; set +a`:

```sh
make netbox-change NETBOX_BRANCH=third-link-local NETBOX_TAG=1
```

It deletes the branch of that name where one stands, every journal entry on it with it, and makes it anew from `main`;
writes the cable between `n1` and `n3` under the branch's header and marks it `third-link`, then the address on `n1`'s
end and marks it `n1-address`, each mark the example's own `stage mark` through `scripts/edge_dev.py run --source
netbox`, its blueprint given to the core at `FYLGJA_API_ADDRESS`; and sets the tag `fylgja-rehearse` on the branch as
its last act, which asks for the rehearsal. Its end: exit 0, the last line `change: the tag asks for its rehearsal,
which takes it off; …`. A mark refused stops it, exit 1, with no tag set and the branch left as it stands for reading; a
branch of that name that is neither `ready`, `new` nor `provisioning` is refused by its status, nothing deleted.

Without `NETBOX_TAG=1` the same command builds and marks the branch and sets no tag, and the tag is set by hand: in
NetBox's pages, signed in as the superuser, `admin`, with the password `local/.env`'s `FYLGJA_NETBOX_SUPERUSER_PASSWORD`
holds, read from the file by the person and never shown, the branch is opened from the branching plugin's list of
branches, edited once, the tag `fylgja-rehearse` added to its tags, and saved. NetBox publishes its pages on the
development host's loopback alone, at `http://127.0.0.1:8800/`: they are reached from a browser on that host itself, or
through a forward of port 8800.

**What follows**, unasked, each read-only:

- within 60 s of the tag, one flow run of `twin-rehearse/main`, its parameters `{"branch": "third-link-local"}`;
- the tag gone from the branch, taken off by the run itself once it has read the branch and before the rehearsal
  starts;
- mid-run, one `rh-` twin in `fylgja-core twin list`;
- at the end, a third journal entry on the branch, by the account `fylgja-orchestrator`, its kind the rehearsal's
  status ([D-097](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-097)): `success` for `passed`, `danger` for `failed`, and `warning` for
  `not_rehearsed` and `stopped`. It is the report: the summary under its heading, which for a pass begins `## Rehearsal
  passed`, with a table and lists, then the detail. Then `fylgja-core twin list` is empty.

The maintainer reads the report where it is filed: the branch's page in NetBox, its Journal tab, which lists the newest
entry first, so that the report stands above the two marks, each entry's kind shown as a badge, `Success` for a pass and
`Info` for a mark. They are asked to say, in their own words, that they read it there; that the two marks, `Fylgja
stage: third-link` and `Fylgja stage: n1-address`, stand beside it; its heading and its kind as the tab shows them; and
whether its table rendered as a table and its lists as lists, not as text.

**Read the run**, read-only, once the report's entry is written, or 60 s after the tag where no run was made, into the
run's directory. NetBox is read with the superuser's token and Prefect with `FYLGJA_ORCHESTRATOR_AUTH`, each from the
environment inside the process that sends the request. Nothing of a webhook's row of `main`'s changelog is saved: those
rows hold its header unmasked.

- the times NetBox gives the tag's setting and its removal, and by whom: the branch object's rows of `main`'s
  changelog, `core/object-changes/`, the tag set by `admin` and taken off by `fylgja-orchestrator`, and no other row
  between;
- the deployment's flow runs created since the tag: its id by `GET /api/deployments/name/twin-rehearse/main`, its runs
  by `POST /api/flow_runs/filter` on that id, each with its `created`, its parameters, its state and times: one since
  the tag, and no more;
- that run's document by `POST /api/artifacts/filter` on the run's id and the type `fylgja-document`, keyed
  `fylgja-twin-rehearse-<run id>`: its `status`, `took_s` and `twin`, each stage's `result`, and its findings;
- the branch's journal entries in order, each with its `kind` and its author, and its `comments` saved byte for byte
  to a file of its own;
- the log of each running `netbox-worker` container since the tag (`docker logs --since <the tag's time>`), the
  runner's output over the run, and `local/prefect/server.log` over the run;
- `fylgja-core twin list`.

Whether the run is the one the criterion names is read from the document's `status` and its stages' `result`s, never
from the entry's colour.

**When no report comes**, read 60 s after the tag from the branch's tags and journal and the deployment's flow runs
since the tag, as **Read the run** reads them. A run still `RUNNING` is a rehearsal under way, and is left to end.

- *The branch keeps its tag, and no flow run was made*: the request never reached Prefect, and NetBox never sends it
  again. Prefect down or not answering when the tag was set loses the request; a webhook naming a deployment id Prefect
  no longer has, after a new `local/prefect/`, is answered 404, and `make netbox-hook` is run again; no `netbox-worker`
  running, a rule disabled or changed, or a header that is not `FYLGJA_ORCHESTRATOR_AUTH`'s each makes no run. The
  worker logs each sending, with Prefect's words or the address it failed at, and NetBox lists a failed one among its
  queues' failed tasks (`/core/background-queues/0/failed/`). The cause is removed, and the tag set again.
- *A flow run was made and the tag stays, with no entry*: the run started and was refused before it took the tag off,
  and shows as failed in Prefect, in the refusal's words: its settings or its reader document refused; no branch of the
  name, one made anew under it, or one not `ready`; the branch's read or the tag's removal refused or unanswered by
  NetBox, as by a runner that holds the example's token of a purged instance; or a runner of the source `infrahub`
  serving, which reads Infrahub and not NetBox. The run's state and message, and its log lines (`POST /api/logs/filter`
  on its id), say which. The tag is taken off first, since an edit of the branch while it carries the tag asks again;
  then the cause is removed, and the tag set again.
- *A flow run stays `SCHEDULED`, the tag on the branch*: no runner took it. The run is deleted (`DELETE
  /api/flow_runs/<id>`, with `FYLGJA_ORCHESTRATOR_AUTH`) before a runner is started, so that none rehearses it late;
  the tag is taken off, and set again once the runner serves.
- *The tag is gone and no entry was written*: the rehearsal started and was stopped, cancelled, past the flow's time
  limit, or its runner ended under it. Prefect says why: the run's state and message, its log lines and the runner's
  output. A twin `rh-…` it left is read with `fylgja-core twin show <twin>` until it answers that the twin is not
  found, or destroyed by `fylgja-core twin destroy <twin>`. Then the tag is set again.

The tag is set again by `make netbox-change NETBOX_TAG=1`, which deletes the branch and builds it again, marks and tag
with it; or by a person in NetBox, who takes the tag off where it stands, which sends nothing, and sets it again, which
asks again. In a run the maintainer watches, each of these ends the run short of the criterion: the cause is removed,
and the run is made again from `make netbox-change`, watched from the build.

**Clean up**, read-only but for what each step names:

- `fylgja-core twin list` empty, a twin left read and destroyed as the run through Infrahub's check says.
- The branches are left as they stand, unmerged and untagged; the next `make netbox-change` of a name replaces its
  branch, its marks and its report.
- A failed sending a run left is listed on `/core/background-queues/0/failed/` and removed by `POST
  /api/core/background-tasks/<id>/delete/` with the superuser's token.
- When the work is done: the runner stopped by its pid, and the core by its pid, the listener of `FYLGJA_LISTEN`; then
  `make prefect-down` and `make netbox-down`.

## Moving to a release

This repository pins one release of fylgja-core's packages, exactly, because its tests reach past what the core
promises ([E-001](design/decisions.md#e-001), fylgja-core's D-124, to be released with 1.1.0). Moving to a new release is one
commit, with the tiers and both demonstrations made again:

1. Move the three pins in `orchestrator/pyproject.toml` (`fylgja-core==`, `fylgja-infrahub==`, `fylgja-netbox==`, and
   `fylgja-core[server]==` in the `dev` extra) and `VERSION` together, to the release or, for its acceptance run, to
   its candidate as installed from TestPyPI, where the candidate's lock and install are as plan 3's
   reading records them. `orchestrator/tests/test_pins.py` fails where one moved without the other.
2. Run `uv lock`, so that `uv.lock` holds the three distributions at that version from PyPI alone (a release; a candidate's lock is as
   step 1 says), and commit it with
   the pins.
3. Run `make lint`, `make test`, `make linkcheck` and `make wheelcheck`, then the contract tiers one at a time
   (`make contract`, `make contract-netbox`).
4. Make both demonstrations again from a fresh clone on a branch of its own, `make infrahub-demo` and `make
   netbox-demo`, each exiting 0, and record in [verified-facts.md](design/verified-facts.md) anything they read that
   differs from what is recorded.
5. After the release, `main` takes the release's pins and `VERSION`; its pure tier runs and both demonstrations are
   made again on the released packages; that commit is tagged `vX.Y.Z`. Pages of fylgja-core link here at that tag,
   made just after the release, and never at `main`.

A change that needs a change of fylgja-core is built against a checkout of it: `make venv CORE=<path of the checkout>`
installs that checkout's three distributions editable over the locked environment, leaves `uv.lock` unchanged, and says
that the environment is no longer the lock's. CI never sets `CORE`, and the change waits for a release before it merges
here.

## Conventions

- **A copy says where it is from.** A file copied from fylgja-core opens with the line that names its path there and the
  commit it was copied at, which `orchestrator/tests/test_no_core_paths.py` holds.
- **No path of fylgja-core is read.** A test or script reads what the installed distributions carry
  (`fylgja_core.packages.shipped()`, `fylgja_core.schemas`) or this repository's own copy.
- **Links into fylgja-core are at a tag,** `https://github.com/happypathnetworking/fylgja/blob/v1.0.0/<path>`, and the
  path exists there; never at `main`.
- **Fixtures change in a commit of their own,** with the diff reviewed.
- **A new rule goes in [`orchestrator/rules.md`](orchestrator/rules.md)** in the same change as the code that files it.
- **The tree holds no host name, address or value of a site.** Tests and fixtures use the documentation ranges
  (192.0.2.0/24, 198.51.100.0/24) and reserved names (`*.example`).
- **No credential in any output**: not in a blueprint, bundle, finding, answer or log line.
