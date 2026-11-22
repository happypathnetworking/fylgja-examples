# Verified facts

What this repository was built on is what fylgja-core's facts record at v1.1.0:
`https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/verified-facts.md`. The
section below is what this repository read for itself, over released packages.
A section this file lacks that a file here cites is fylgja-core's, at the tag above.

## uv 0.12.23 over released packages

Read on 2026-11-19 on the development host, with Python 3.14.4 and uv 0.12.23, in a scratch
project under `local/reading/` (removed after; made as the task's brief states, its files not
kept): a root `pyproject.toml` holding `[tool.uv]`
(`required-version = "==0.12.23"`, `python-downloads = "never"`,
`python-preference = "only-system"`) and `[tool.uv.workspace] members = ["orchestrator"]`, a
`VERSION` of `1.0.0`, a copy of this repository's `formats/`, and a copy of `orchestrator/`
whose `pyproject.toml` pins `fylgja-core==1.0.0`, `fylgja-infrahub==1.0.0` and
`fylgja-netbox==1.0.0`, with `fylgja-core[server]==1.0.0` first in its `dev` extra. Each reading
was run once, against PyPI, with uv's wheel cache warm, so the seconds are a warm cache's.
Each command's output is kept in `local/task-2-readings/`.
*(2026-11-19)*

- **One member locks against PyPI.** `uv lock` exited 0 and resolved 128 packages in 2.83 s.
  The lock holds `fylgja-core`, `fylgja-infrahub` and `fylgja-netbox` at 1.0.0, each with
  `source = { registry = ... }` naming PyPI's simple index, and `fylgja-orchestrator` with
  `source = { editable = "orchestrator" }`. The `dev` extra's `fylgja-core[server]==1.0.0`
  resolved: the lock lists it as a requirement of the orchestrator's `dev` extra and holds
  `fylgja-core`'s `server` extra. (`1-lock.txt`, `1-uv.lock`)
- **The member's build reads `formats/` at the root.** The first `uv sync --locked
  --all-packages --all-extras --python python3` exited 1 with the scratch root holding no
  `formats/`: the orchestrator's build names `plan-1.schema.json` and `rehearsal-1.schema.json`
  as missing "under .../formats: the wheel is built from the repository, orchestrator/ beside
  formats/". With `formats/` copied in, the same command exited 0 in 2.35 s and installed the
  environment into `.venv` (`UV_PROJECT_ENVIRONMENT` set to it). (`1-sync-first-attempt-no-formats.txt`,
  `1-sync.txt`)
- **The environment holds the released packages.** `fylgja-core --version` printed
  `fylgja-core 1.0.0 (commit 33f8a8ba8a06defc4af728de7a1f5558317d070e)`.
  `packages.shipped()` returned two directories, `site-packages/fylgja_core/shipped/psp` and
  `site-packages/fylgja_core/shipped/probes`. `uv pip list` showed `fylgja-core`,
  `fylgja-infrahub` and `fylgja-netbox` at 1.0.0 from the index, and `fylgja-orchestrator`
  1.0.0 editable from the member. (`1-verify.txt`)
- **A checkout's members install over the locked environment, and uv says nothing of the
  pins.** In a `git clone --local` of fylgja-core at `e7cdc0c` (`main`, `VERSION` 1.0.1),
  `uv pip install --python .venv/bin/python -e <clone>/core -e <clone>/readers/infrahub
  -e <clone>/readers/netbox` exited 0 in 2.68 s ("Resolved 16 packages"), replaced the three
  1.0.0 packages with 1.0.1 editable installs, and printed no refusal or warning about
  `fylgja-orchestrator`'s `==1.0.0`. The same command with `--no-deps` exited 0 in 2.43 s
  ("Resolved 3 packages") with the same replacement and the same silence. After each,
  `fylgja-core --version` printed `fylgja-core 1.0.1 (commit
  e7cdc0c968d481fd1f8446c344b6e0b4c4d37eeb)` and `git status --porcelain uv.lock` printed
  nothing. Only `uv pip check` reported it, exit 1, "Found 3 incompatibilities": the
  orchestrator requires each of the three `==1.0.0`, but 1.0.1 is installed. (`2a-editable.txt`,
  `2a-after.txt`, `2b-nodeps.txt`, `2b-after.txt`)
- **`uv sync --locked` puts the locked versions back.** After each install above, `uv sync
  --locked --all-packages --all-extras --python python3` exited 0 in 0.10 s and 0.08 s,
  uninstalled the three editable 1.0.1 packages and installed 1.0.0 from the lock;
  `fylgja-core --version` printed 1.0.0 and commit `33f8a8ba8a06defc4af728de7a1f5558317d070e`
  again. `git status --porcelain uv.lock` printed nothing after each install;
  `uv.lock`'s SHA-256 was read after the second resync alone, `0fcf7444...a9fa`, the value
  `1-lock.sha` holds for the lock `uv lock` wrote.
  (`2a-resync.txt`, `2a-after-resync.txt`, `2b-resync.txt`, `2b-after-resync.txt`)

## The contract tiers and both demonstrations from a fresh clone, on fylgja-core 1.0.0 from PyPI

Read on 2026-11-20 on the development host (the logs' own timestamps are 2026-11-20 UTC, the
contract tiers from 00:25), in a fresh `git clone --branch phase-12/1-examples` of this repository
at `f8cacda`, with no `fylgja-core` checkout on any path its commands took; the clone's
`local/.env` was written by the commands themselves, by the controller (four settings of the
core's, below) and, by the controller's record, by the maintainer for the node login at the
start. Two things were run more than once and every run is read below: the Infrahub contract
tier twice (the first run skipped the orchestrator's tests) and the Infrahub demonstration
three times (refused on port 8000 before any step, refused at the lab pool, then passed);
every other run was made once.
Its output is kept in the plan's workspace under `task-8-logs/`, cited by file name below.
Seconds are as the logs print them; a figure marked as a derivation is worked out from others.
*(2026-11-20)*

- **The gates pass in a clone.** `make venv` ran `uv sync --locked --all-packages --all-extras
  --python python3` on CPython 3.14.4, resolved 129 packages, built `fylgja-orchestrator`
  (1.71 s to prepare) and installed 126 packages in 80 ms, among them `fylgja-core==1.0.0`,
  `fylgja-infrahub==1.0.0`, `fylgja-netbox==1.0.0`, `prefect==3.9.2`, `ruff==0.17.3` and
  `mypy==2.4.0`. `make lint` printed "All checks passed!" for ruff twice and mypy "no issues"
  in 72, 17 and 21 source files. `make test` printed 150 passed, 7 deselected in 4.53 s
  (`infrahub`); 202 passed, 14 deselected in 5.03 s (`netbox`); 860 passed, 23 deselected in
  124.44 s (`orchestrator`). `make linkcheck` printed "10 files, 43 relative links checked,
  74 external skipped, 0 broken". `make wheelcheck` printed that
  `fylgja_orchestrator-1.0.0-py3-none-any.whl` is marked `Private :: Do Not Upload`, carries
  no licence file, carries the example's 2 formats and its 6 GraphQL documents, and, beside
  the three 1.0.0 packages from the index alone, passes each check it lists. (`1-venv.log`,
  `1-lint.log`, `1-test.log`, `1-linkcheck.log`, `1-wheelcheck.log`)
- **The Infrahub contract tier passes, once the orchestrator's settings are there.** The
  first `make contract` ran the `infrahub` tests, 7 passed in 244.46 s, and skipped all 11 of
  the `orchestrator`'s, each "the contract tier needs FYLGJA_ORCHESTRATOR_INFRAHUB_TOKEN set",
  in 0.16 s. After `make orchestrator-env` (which added the orchestrator's settings and the
  account's token to `local/.env`, and said to restart the core) the second `make contract`
  printed 7 passed in 187.88 s (`infrahub`) and 11 passed in 710.85 s (`orchestrator`), no
  skip. Infrahub 1.11.11 answered 155 s after Compose's start returned; `make
  infrahub-register` printed that `fylgja` read `phase-12/1-examples` at `f8cacda`, in-sync and
  online, 77 s on, and that each of the 2 task workers held the tree 1 s on. The tier's
  cancel test printed that a rehearsal cancelled at the check's deadline read CANCELLED 3.23 s
  after the cancel was sent, and the core listed its twin no more 2.01 s after that.
  (`2-infrahub-up.log`, `2-infrahub-register.log`, `2-infrahub-seed.log`,
  `2-contract-first.log`, `2-orchestrator-env.log`, `2-contract.log`)
- **The core's settings were written by the controller.** The clone's `local/.env` lacked the
  core's `FYLGJA_STORE`, `FYLGJA_TOKENS`, `FYLGJA_LISTEN` and `FYLGJA_API_ADDRESS`, which
  `make orchestrator-env` needs and no target writes; the controller wrote them (paths under
  the clone's `local/`, a loopback address and port, no credential) and an empty token file
  of mode 0600. The progress record says so; no log shows the writing.
- **The NetBox contract tier passes, with one skip.** NetBox 4.7.5 with `netbox_branching`
  1.2.3 answered at the loopback address; the first start of Compose exited 1, and `netbox_dev`
  printed "netbox healthy 749 s after its start" and asked Compose once more. `make
  contract-netbox` printed 14 passed in 156.33 s (`netbox`) and 11 passed, 1 skipped in
  369.65 s (`orchestrator`). The skip is `tests/contract_netbox/test_source_contract.py:490`:
  "no webhook fylgja-rehearse is installed: run make netbox-hook, with the development
  Prefect up". Both sources were removed with `PURGE=1` afterwards, each printing that its
  Compose project was removed with its volumes. (`2-netbox-up.log`, `2-netbox-seed.log`,
  `2-contract-netbox.log`, `2-infrahub-down.log`, `2-netbox-down.log`)
- **A port another process holds is refused before any step.** `fylgja-core`'s development
  Infrahub (1.11.11) was up from its main checkout, 66 s after Compose's start returned, its 8
  containers started. `make infrahub-demo` in the clone printed "demo: port 8000 is listened
  on at 127.0.0.1 by a process the demonstration did not start, and infrahub needs it" and
  "demo: nothing the demonstration starts is left up", and `make` exited 2; the log prints no
  step line. The log shows nothing of `fylgja-core`'s stopped; that its 8 containers were
  still up afterwards is the controller's reading, not kept in a log. `fylgja-core`'s
  `make infrahub-down` then stopped its containers, "its containers, network and volumes are
  kept". (`3-core-infrahub-up.log`, `3-examples-infrahub-demo.log`,
  `3-core-infrahub-down.log`)
- **The Infrahub demonstration's second invocation was refused at the lab-pool check, after Infrahub
  came up.** Its host checks passed, step 1 started Infrahub, which answered 143 s after Compose's
  start returned, and the demonstration then printed that the pool 172.20.0.0/16 had no /24 that
  neither a Docker network nor another twin held, and listed `fylgja-examples-infrahub_default`
  (172.20.0.0/16) as the Docker network holding part of it. By the controller's record the pool
  was the default, no `FYLGJA_LAB_POOL` being set before. The demonstration printed "set
  FYLGJA_LAB_POOL in local/.env, then run make infrahub-demo again", left Infrahub up, and `make`
  exited 2. The maintainer then set `FYLGJA_LAB_POOL` in the clone's `local/.env` (a site value,
  not recorded here). (`4-infrahub-demo.log`)
- **The Infrahub demonstration passed.** The third invocation, after the two refusals, printed
  "the host's checks passed" and ran its 8 steps (Infrahub answered 0 s after Compose's start
  returned; the second invocation's log says it left Infrahub up, `4-infrahub-demo.log`; `make
  infrahub-register` printed `fylgja` at `f8cacda`, in-sync and online, 76 s on); the flow run
  `8c2cc48f-5dc3-4a41-93e4-cdb0de315d83` of `twin-rehearse/main` went SCHEDULED, PENDING, RUNNING,
  COMPLETED, and the demonstration printed "the rehearsal passed: 4 stages, 148.2 s". The
  controller's record has this invocation exit 0 in 696 s. The report is in Infrahub, the proposed
  change "Rehearse third-link" of the branch `third-link`, its thread "Fylgja rehearsal"; the
  maintainer read it there and said it is correct. `make demo-down PURGE=1` ended the runner, the
  core and Prefect and removed the Compose project with its volumes. (`5-infrahub-demo.log`,
  `6-demo-down.log`)
- **The NetBox demonstration passed.** After the host checks passed, step 1 printed the first
  start exiting 1 on the health wait, "netbox healthy 774 s after its start" and a second ask
  of Compose, then "NetBox 4.7.5 with netbox_branching 1.2.3 answers", 1 worker running.
  `make netbox-hook` made the webhook `fylgja-rehearse` for the deployment of
  `twin-rehearse/main`; `make netbox-change` set the tag on the branch `third-link`; the flow
  run `14bd7e68-6cdc-4ed8-8dc1-7cf4246b9915` went RUNNING, COMPLETED, and the demonstration
  printed "the rehearsal passed: 4 stages, 119.4 s". The controller's record has the run exit
  0 in 996 s. The report is the newest Journal entry of the branch `third-link` in NetBox; the
  maintainer read it there and said it is correct. `make demo-down PURGE=1` ended the runner,
  the core and Prefect and removed NetBox's Compose project with its volumes.
  (`7-netbox-demo.log`, `8-demo-down.log`)
- **Derivation: where the time went.** NetBox's 774 s to healthy is 78 percent of the
  demonstration's 996 s (derived from the two figures; the controller's record gives the
  996 s); the rehearsal itself took 119.4 s of it.

## The lock over TestPyPI, and both demonstrations from a fresh clone, on fylgja-core 1.1.0rc1

Read on 2026-11-21 on the development host (CPython 3.14.4, which the clone's
`make venv` printed; uv 0.12.23 is the version the repository's `required-version` pins, and
neither version is in a lock record, so both are the controller's account for the lock). The lock
was read at 19:04 UTC in a worktree of this repository whose `pyproject.toml` held, beside the
workspace table, an explicit index `testpypi` at `https://test.pypi.org/simple` and a
`[tool.uv.sources]` table naming it for `fylgja-core`, `fylgja-infrahub` and `fylgja-netbox`,
and whose `orchestrator/pyproject.toml` pinned those three at `==1.1.0rc1` (the commit
`a27e199`, made at 19:09, holds both). The demonstrations were run in a fresh clone of this
repository at `a27e199`, on the branch `rc1-acceptance`, outside every worktree, from 22:31
to 23:11 UTC; the clone's `FYLGJA_LAB_POOL` was set to a /16 apart from the core's default,
which lies where Docker allocates the next Compose network, and its node login was written by
the maintainer. The records are the plan's acceptance directory in fylgja-core's
main checkout, `local/phase-12/acceptance/`, `lock/` and `demo/`, cited by file name. The
seconds are as the logs print them; a wall figure is read from a wrapper's saved output
(`demo/*.wrapper.out`). *(2026-11-21)*

- **`uv lock` resolves with TestPyPI as an explicit index.** It printed `Resolved 129
  packages in 5.16s` and `Updated fylgja-core v1.0.0 -> v1.1.0rc1` for each of the three
  (`lock/uv-lock.out`). The lock names `fylgja-core`, `fylgja-infrahub` and `fylgja-netbox`
  at 1.1.0rc1 with `source = { registry = "https://test.pypi.org/simple" }`, each wheel's URL on
  `test-files.pythonhosted.org`; counting the lock's `source` tables read 125 from
  PyPI's simple index, 3 from `https://test.pypi.org/simple` and 1 editable
  (`fylgja-orchestrator`, `orchestrator`) (`lock/lock-sources.txt`). `httpx` 0.28.1 and
  `prefect` 3.9.2 stay on PyPI's simple index, as `httpx`'s block names it
  (`lock/lock-httpx.txt`). The lock's
  hashes for the three wheels equal TestPyPI's simple pages' (`96efd86d…`, `08bc134b…`,
  `ae4b7fca…`: `lock/uv-lock.diff`, `lock/simple-fylgja-*.json`), and the orchestrator's
  `requires-dist` carries `index = "https://test.pypi.org/simple"` on four entries, those of
  the three distributions (`fylgja-core` twice, once with its `server` extra), and on no other.
  The diff against the lock before
  it changes 26 lines (`lock/uv-lock.diff`).
- **The Infrahub demonstration passed.** In the clone, `make infrahub-demo` exited 0
  (`demo/infrahub-demo.wrapper.out`: `infrahub-demo ok 1056s`). The clone's venv held
  `fylgja-core==1.1.0rc1`,
  `fylgja-infrahub==1.1.0rc1`, `fylgja-netbox==1.1.0rc1` and `fylgja-orchestrator==1.1.0rc1`
  (`infrahub-demo.log`, lines 42 to 45). Infrahub 1.11.11 answered 158 s after Compose's
  start returned; `make infrahub-register REF=rc1-acceptance` printed that `fylgja` read
  `rc1-acceptance` at `a27e199`, in-sync and online, 76 s on. The seed made the proposed change
  `18ea30dd-37cd-7e8e-3b92-c516bd3dbfd7`, "Rehearse third-link", of the branch `third-link` into
  `main`; the flow run `00db6a25-2502-4294-828c-4f65587ab678` of `twin-rehearse/main` went
  PENDING, RUNNING, COMPLETED, and the demonstration printed "the rehearsal passed: 4 stages,
  154.1 s, flow run 00db6a25-2502-4294-828c-4f65587ab678" (`infrahub-demo.log`). The report is
  in Infrahub, the proposed change's thread "Fylgja rehearsal"; no saved file records the
  reading, and the controller's ledger quotes the maintainer's word after it: "I read the
  rehearsal thread, go ahead". `make demo-down PURGE=1` ended the runner, the core and Prefect and
  printed that the Compose project `fylgja-examples-infrahub` was removed with its volumes
  (`demo-down-1.log`).
- **The NetBox demonstration passed, after a first start that exited 1.** `make netbox-demo`
  exited 0
  (`demo/netbox-demo.wrapper.out`: `netbox-demo ok 972s`). NetBox 4.7.5 with
  `netbox_branching` 1.2.3 was built from `netbox-docker` 5.1.1. The first start of Compose printed
  `dependency failed to start: container fylgja-examples-netbox-netbox-1 is unhealthy`, and
  `netbox_dev` printed "the first start of fylgja-examples-netbox exited 1; waiting for Docker to
  call netbox healthy", then "netbox healthy 745 s after its start", asked Compose once more
  (which started the worker, `Container fylgja-examples-netbox-netbox-worker-1 Started`) and
  printed "NetBox 4.7.5 with netbox_branching 1.2.3 answers", 1 worker running. The core's own
  development Infrahub and NetBox had been purged at 22:31 (`purge/infrahub-down.log` and
  `purge/netbox-down.log` print each of the core's two Compose projects
  removed with its volumes); this run's project, `fylgja-examples-netbox`, is another, and
  what NetBox did in the 745 s was not read. `make netbox-hook` made the webhook `fylgja-rehearse`;
  `make netbox-change` set its tag on the branch `third-link`; the flow run
  `8aab684e-2fef-42e8-973a-5159eaa8e5c9` went SCHEDULED, PENDING, RUNNING, COMPLETED, and the
  demonstration printed "the rehearsal passed: 4 stages, 112.6 s, flow run
  8aab684e-2fef-42e8-973a-5159eaa8e5c9" (`netbox-demo.log`). The report is the newest Journal
  entry of the branch `third-link` in NetBox; no saved file records the reading, and the
  controller's ledger quotes the maintainer's word after it: "I read the journal, go ahead".
  `make demo-down PURGE=1` printed that `fylgja-examples-netbox` was removed with its volumes
  (`demo-down-2.log`).
- **Derivation: the NetBox first start.** 745 s is 77 percent of the demonstration's 972 s
  wall (derived from the two figures); the rehearsal itself took
  112.6 s of it.

- **This repository's contract tiers pass from the clone on the candidate** (read on 2026-11-22,
  01:23 to 02:13 UTC, in the same clone switched to `rc1-acceptance` at `a27e199`; the records are
  `examples-contracts/rc1/` of fylgja-core's acceptance directory, each target's log and
  `wrapper.out`, which holds the wall seconds). Infrahub came up first and NetBox after, each
  purged afterwards: each log prints its Compose project removed with its volumes
  (`infrahub-down.log`, `netbox-down.log`).
  `make contract` (`contract.log`; wrapper `contract ok 964s`): `infrahub/tests/contract/` 7
  passed in 237.58 s, then `orchestrator/tests/contract/` 11 passed in 722.09 s, no skip. The
  setup of `test_seed_contract.py`'s first test printed
  `seed: third-link: its BranchCreate failed (POST
  /graphql/main answered HTTP 200 with errors: None (http_status 500)); reading for the branch`
  and then `seed: third-link is listed, 19 s after its BranchCreate was sent`, and the tests
  passed. `make contract-netbox` (`contract-netbox.log`; wrapper `contract-netbox ok 528s`):
  `netbox/tests/contract/` 14 passed in 159.32 s, then `orchestrator/tests/contract_netbox/` 11
  passed and 1 skipped in 365.52 s. The skip is
  `tests/contract_netbox/test_source_contract.py:491`, and its own message is "no webhook
  fylgja-rehearse is installed: run make netbox-hook, with the development Prefect up". The
  wrapper ran `prefect-down-2` before this target (`prefect-down-2.log`: the development
  Prefect "is not running: no pid file"), and `make netbox-hook` needs Prefect up; the tier's
  order is thus the controller's account of why no webhook was installed, and the log holds only
  the message. The setup steps' wall seconds are in `wrapper.out`: `infrahub-up` 214 s,
  `infrahub-register` 141 s, `infrahub-seed` 288 s, `netbox-up` 754 s (its log: the first start
  exited 1, "netbox healthy 732 s after its start"), `netbox-seed` 32 s; the wrapper ended
  `all rc=0`.

## Both demonstrations from a fresh clone on the released fylgja-core 1.1.0

Read on 2026-11-22 on the development host, in a fresh clone of this repository at `1e2dfb6`
(the commit of the release, the one `main` and the tag `v1.1.0` name), on the branch
`release-acceptance`. That the clone lies outside every worktree is the controller's account. The
records are the plan's acceptance directory in fylgja-core's main checkout,
`local/phase-12/acceptance/release/`, cited by file name, and the clone's own `local/demo/`.
`make venv` is a `--locked` sync and passed (`venv.log`); that it installed the packages from
PyPI's release is the controller's account, and the log shows the versions alone. Infrahub's
demonstration ran first and NetBox's after it. The seconds are as the logs print them,
and a wall figure is read from a wrapper's saved output (`*.wrapper.out`); a figure marked as a
derivation is worked out from others. *(2026-11-22)*

- **`make venv` installed the released packages.** The clone's `make venv` ran `uv sync
  --locked --all-packages --all-extras` with CPython 3.14.4, resolved 129 packages and installed
  126, among them `fylgja-core==1.1.0`, `fylgja-infrahub==1.1.0` and `fylgja-netbox==1.1.0`, and
  `fylgja-orchestrator==1.1.0` from the clone's `orchestrator` directory (`venv.log`, lines 1
  to 4 and 40 to 43). That the three were read from `importlib.metadata` in the clone's `.venv`
  is the controller's account; `venv.log` shows the install lines alone.
- **The Infrahub demonstration passed.** `make infrahub-demo` exited 0
  (`infrahub-demo.wrapper.out`: `infrahub-demo ok 1032s`). Infrahub 1.11.11 answered 155 s after
  Compose's start returned (`infrahub-demo.log`, line 75). `make infrahub-register
  REF=release-acceptance` printed that `fylgja` reads `release-acceptance` at `1e2dfb6`,
  in-sync and online, 103 s on, and that each of the 2 task workers holds the tree at `1e2dfb6`
  (`infrahub-demo.log`, lines 129 and 130). The seed made the proposed change
  `18ea7c66-c302-1436-2fea-c516286c1943`, "Rehearse third-link", of the branch `third-link`
  into `main`; the flow run `ceed374e-d4d7-4026-8bf8-9c6bf64cece0` of `twin-rehearse/main` went
  SCHEDULED, PENDING, RUNNING, COMPLETED, and the demonstration printed "the rehearsal passed: 4
  stages, 157.2 s, flow run ceed374e-d4d7-4026-8bf8-9c6bf64cece0" (`infrahub-demo.log`, lines
  157 to 163). The report is in Infrahub, the proposed change's thread "Fylgja rehearsal"; no
  saved file records the reading, and the controller's ledger quotes the maintainer's word after
  it: "i read the report". `make demo-down PURGE=1` printed that the Compose project
  `fylgja-examples-infrahub` was removed with its volumes (`demo-down-1.log`, line 51).
- **The NetBox demonstration passed, after a first start that exited 1.** `make netbox-demo`
  exited 0 (`netbox-demo.wrapper.out`: `netbox-demo ok 948s`). NetBox 4.7.5 with
  `netbox_branching` 1.2.3 was built from `netbox-docker` 5.1.1 (`netbox-demo.log`, line 4). The
  first start of Compose printed `dependency failed to start: container
  fylgja-examples-netbox-netbox-1 is unhealthy`, and `netbox_dev` printed "the first start of
  fylgja-examples-netbox exited 1; waiting for Docker to call netbox healthy", then "netbox
  healthy 733 s after its start", and "NetBox 4.7.5 with netbox_branching 1.2.3 answers", 1
  worker running (`netbox-demo.log`, lines 92 to 105); what NetBox did in the 733 s was not
  read. `make netbox-hook` made the webhook `fylgja-rehearse`; `make netbox-change` set its tag
  on the branch `third-link`; the flow run `e6898b12-b681-4a1b-bad8-8fc203f07289` went PENDING,
  RUNNING, COMPLETED, and the demonstration printed "the rehearsal passed: 4 stages, 113.4 s,
  flow run e6898b12-b681-4a1b-bad8-8fc203f07289" (`netbox-demo.log`, lines 168 to 185). The
  clone's `local/demo/rehearsal.json`, last written by this run, has status `passed`, 4 stages
  and `took_s` 113.44; the stage results are `created`, `passed`, `passed` and `skipped`
  (`local/demo/rehearsal.json` of the clone). The report is the newest Journal entry of the
  branch `third-link` in NetBox; no saved file records the reading, and the controller's ledger
  quotes the maintainer's word after it: "I read the journal, go ahead". `make demo-down
  PURGE=1` printed that `fylgja-examples-netbox` was removed with its volumes
  (`demo-down-2.log`, line 41).
- **Derivation: the NetBox first start.** 733 s is 77 percent of the demonstration's 948 s
  wall (derived from the two figures); the rehearsal itself took 113.4 s of it.
- **Derivation: against the candidate's section above.** The Infrahub demonstration's wall
  was 1032 s against the candidate's 1056 s, and NetBox's 948 s against 972 s; the rehearsals
  took 157.2 s against 154.1 s and 113.4 s against 112.6 s, and NetBox's first start became
  healthy 733 s after its start against 745 s. Each is the difference of two figures read in
  two runs on one host, and says nothing of why they differ.
- **The CI run is the controller's account.** fylgja-examples' CI run 45083481957 passed on
  `1e2dfb6`, its job `lint-and-test`; no file of the acceptance directory holds it.

## fylgja-core's `nornir-ospf` branch, read in its tree

These readings were made on fylgja-core's branch `nornir-ospf`, in its own tree, from
2026-11-16 to 2026-11-17, and are carried here as they were when the branch was cut again in this
repository: the paths they name (`core/.venv`, `testdata/blueprint/three-node.json`,
`orchestrator/tests/nornir/answers/`) are that tree's, and the versions are those of that day.
Under fylgja-core the first was a subsection of "SR Linux 24.7.1", and the second a section of its
own. Nothing below was read again here.

### SR Linux 24.7.1: OSPF point-to-point on /31s, the state read, and scrapli over asyncssh (private branch)

Read on 2026-11-16 on a twin of `testdata/blueprint/three-node.json` on the local driver, SR Linux
24.7.1, configured by hand through `sr_cli` in a private candidate, one node at a time.

- **A /31 and a point-to-point OSPF interface are accepted as written**, on `n1` with `10.0.0.0`
  and on `n2` with `10.0.0.1`, the `.0` host address and a router-id of `10.0.0.0` among them. The
  lines, beside the fixture's own `subinterface 0` and `network-instance default interface
  ethernet-1/1.0`:

  ```
  set / interface ethernet-1/1 subinterface 0 ipv4 admin-state enable
  set / interface ethernet-1/1 subinterface 0 ipv4 address 10.0.0.0/31
  set / network-instance default protocols ospf instance main admin-state enable
  set / network-instance default protocols ospf instance main version ospf-v2
  set / network-instance default protocols ospf instance main router-id 10.0.0.0
  set / network-instance default protocols ospf instance main area 0.0.0.0 interface ethernet-1/1.0 interface-type point-to-point
  ```

- **The adjacency was `full` on both ends at the first read**, taken within seconds of the second
  node's commit; how long it takes to form was not measured beyond that.
- **The adjacency read** is `info from state network-instance default protocols ospf instance main
  area * interface * neighbor * adjacency-state | as json`. Its answer nests `network-instance[]`,
  `protocols.ospf.instance[]`, `area[]`, `interface[]` keyed `interface-name` (the subinterface,
  `ethernet-1/1.0`), `neighbor[]` with `router-id` and `adjacency-state`
  (`orchestrator/tests/nornir/answers/full.json`).
- **That read cannot tell a node with no OSPF from one with no neighbour**: both answer `{\n}`,
  exit 0 (`n3` before any OSPF, and `n3` with an instance on a port whose far end ran none;
  `no-neighbour.json`). The instance's presence is a read of its own, `info from state
  network-instance default protocols ospf instance main oper-state | as json`: `oper-state`
  `enable` where it runs (`oper.json`), `{\n}` where there is none (`absent.json`).
- **scrapli's asyncssh transport does not reach the prompt as shipped** (scrapli 2026.2.20,
  scrapli_community 2025.1.30): it opens its session with a terminal type and no size
  (`scrapli/transport/plugins/asyncssh/transport.py`, `open_session(term_type="xterm")`), the CLI
  then asks the terminal for its cursor position (`ESC[999;999H ESC[6n`) and prints no prompt
  until it is answered, and the open fails after `timeout_ops` with `ScrapliTimeout: timed out
  getting prompt`. Writing the answer `ESC[80;256R` to the channel in an `on_open` of the
  connection's own, before the platform's `default_async_on_open`, opened it in 4.1 s, and every
  read after answered.
- **Through Nornir's asyncio runner**, with that `on_open` in the `scrapli` connection options'
  `extras`, `send_commands` of the two reads against the three nodes took 4.6 s with the
  connections opening and 0.18 s on the kept connections; each host's
  `result[host][0].scrapli_response` is a list, one response a command, its `.result` the JSON
  text, and `result[host][0].result` the two texts joined by a blank line.

### Nornir 3.7.0a1 and nornir_scrapli 1.6.0a1 (private branch)

Read from the packages installed in the worktree's `core/.venv` on 2026-11-16 (nornir 3.7.0a1,
nornir_scrapli 1.6.0a1, scrapli 2026.2.20, scrapli_community 2025.1.30, asyncssh 2.24.1), each from
the file named, and the starred ones by a run of a twelve-line script on the asyncio runner.

- **`AInitNornir`** is `from nornir import AInitNornir`, `async def`, with `InitNornir`'s
  arguments, and returns the same `Nornir` (`nornir/init_nornir.py`). *
- **The asyncio runner** is the runner plugin `asyncio`, class
  `nornir.plugins.runners.AsyncioRunner`, selected as
  `runner={"plugin": "asyncio", "options": {...}}`. Its options are `num_workers` (default 20, the
  hosts in flight at once, a semaphore), `per_host_timeout` and `timeout`, the last two seconds
  or `None` (`nornir/plugins/runners/__init__.py`). *
- **A run** is `await nr.arun(task=<an async def taking a Task>, **kwargs)`, an
  `AggregatedResult`; `on_good` is True and `on_failed` False by default. A synchronous task
  raises `SyncTaskOnAsyncRunError` (`nornir/core/__init__.py`). *
- **A host past `per_host_timeout`** has `result[host].failed` True and
  `result[host][0].exception` a `TaskTimeoutError`, and is added to `nr.data.failed_hosts`, so the
  next `arun` skips it unless given `on_failed=True`. A poll that reads again must pass it. *
- **A capability inventory plugin** is a class constructed with `inventory.options` as keyword
  arguments, with `get_capabilities()` returning a `frozenset`, `frozenset({"asyncio"})` for one
  with `async def aload(self) -> Inventory` alone. It is registered in code by
  `CapabilityInventoryPluginRegister.register(name, cls)`
  (`nornir/core/plugins/inventory.py`, `register.py`); registering a name twice with the same
  class is a no-op, and another class under the same name raises `PluginAlreadyRegistered`
  (`PluginRegister.register`, read 2026-11-16). `Inventory`, `Hosts`, `Groups`, `Defaults`, `Host` and `ConnectionOptions`
  are `nornir.core.inventory`'s, and a `Host`'s repr is `Host: <name>`. *
- **Closing** is `await nr.aclose_connections(on_good=True, on_failed=False)`, itself an `arun`;
  hosts that timed out need `on_failed=True` (`nornir/core/__init__.py`).
- **The runner's `timeout` bounds one `arun`, not a poll**: past it, each host not finished is
  recorded with a `TaskTimeoutError` and the run returns; nothing is raised to the caller
  (`nornir/core/run.py`, `_run_timeout_error`; read 2026-11-16). A poll of several rounds keeps
  its own clock.
- **nornir_scrapli's async task** is `from nornir_scrapli.async_tasks import send_command`,
  `async def send_command(task, command, strip_prompt=True, failed_when_contains=None,
  timeout_ops=None) -> Result`. It opens the connection `scrapli`, registered by the package's
  entry point in `nornir.plugins.capability_connections`
  (`nornir_scrapli/async_tasks/core.py`, its `entry_points.txt`).
- **The connection's `aopen`** builds `AsyncScrapli(**parameters, platform=...)` from the host's
  hostname, username, password and port, with `transport` defaulting to `asyncssh` and the
  connection options' `extras` laid over it, `auth_strict_key` and `timeout_ops` among them
  (`nornir_scrapli/connection.py`).
- **SR Linux's scrapli platform** is `nokia_srlinux`, in `scrapli_community`
  (`scrapli_community/nokia/srlinux/`), which nornir_scrapli's `asyncio` extra installed; it
  needs no pin of its own.

#### The OSPF check on the seeded change (read 2026-11-17)

Read on this host's development Infrahub 1.11.11, the core serving locally on the containerlab
driver, SR Linux 24.7.1, by `fylgja-orchestrator twin rehearse --branch third-link --json` with
the runner's tokens, the seed's proposed change open; times are seconds of the command's own
clock, taken by stamping its progress lines.

- **The seeded change passes, every adjacency FULL at the first read.** Stages `created`,
  `passed`, `passed`, `skipped` (branch point, `third-link`, `n1-address`, head unchanged), exit
  0, `already_failing` empty: `ospf: 4 of 4 link ends full` on the baseline's two links, then `6
  of 6` after each step. Each check was one round, 4.8 s on the baseline and 5.1 s and 5.2 s
  after the steps, each round opening the three connections anew; the check began 0.1 s after
  verify held, and verify itself 2.5 s after the create's push (settle) and 2.5 s after each
  step's. The whole rehearsal took 166 s.
- **The first run under the check failed the seeded change at `n1-address`, rightly.** Infrahub's
  object loader sets a port's addresses to the list nested under it: the stage nested one
  address under `n1:ethernet-1/2`, which then held `192.0.2.1/24` and no longer its `/31`
  (rendered configuration read back by the reader at the stage's time), so n1's end of n1-n3 left
  n3's subnet. The check read `5 of 6` for four rounds and `4 of 6` from about 30 s after verify,
  as the dead interval passed, and failed both ends with "no neighbour" when its 120 s ran out.
  The stage now lists the port's `/31` with the address it adds.
- **A link without an address fails both ends.** A throwaway third stage, never committed,
  deleted `10.0.0.0/31` on the branch (by GraphQL: the loader cannot remove a peer). Verify held
  (19 hold, 0 fail: layer 1), and the check failed the stage, the rehearsal `failed` at stage 4
  of 5, exit 1, with `ospf.adjacency.not_full` on `n1:ethernet-1/1` and `n2:ethernet-1/1`, both
  "no neighbour", the cause `The OSPF check found 2 failures at stage 4, n1-unaddressed, ...`.
  Losing the address also moved n1's router-id from `10.0.0.0` to `10.0.0.4`, the template's
  lowest routed address, and the n1-n3 adjacency reset with it: `2 of 6` for eight rounds, `3 of
  6` at 41 s and `4 of 6` from 46 s into the check, which then ran to its budget, 125 s in all.
- **A `head` refused for the event log's count, once.** One rehearsal begun seconds after a seed
  ended refused its head stage with `read.incomplete` (`Infrahub counted 4 in InfrahubEvent ...
  and answered 11`), as recorded under Infrahub 1.11.11; the same rehearsal run again passed.

## The OSPF rehearsal from a fresh clone, on fylgja-core 1.1.0rc1

Read on 2026-11-21 (the logs' own timestamps are 2026-11-21 UTC from 23:32 to 23:56, the
second `demo-down` at 00:28 on 2026-11-22) on the development host, in the fresh clone,
outside every worktree, that the candidate's demonstrations were run in, switched to the
branch `nornir-acceptance` at this branch's commit `229f9f4` (rebased onto 1.1.0 as
`2cf49a8`), with the clone's own `local/.env`. The clone's `fylgja-core`, `fylgja-infrahub`
and `fylgja-netbox` were 1.1.0rc1 from TestPyPI. The records are fylgja-core's main checkout,
`local/phase-12/acceptance/demo/`, cited by file name. The seconds are as the logs print them;
a wall figure is read from a wrapper's saved output (`*.wrapper.out`). *(2026-11-21)*

- **The first run failed at step 7, the runner importing a module its venv lacked.**
  `make infrahub-demo`
  ran its steps 1 to 6 (Infrahub 1.11.11 answered 153 s after Compose's start returned in step 1;
  `make infrahub-register REF=nornir-acceptance` printed that `fylgja` read `nornir-acceptance`
  at `229f9f4`, in-sync and online, 96 s on; Prefect answered), then printed "step 7, the
  runner: the runner exited before it served" and `make` exited 1 (`nornir-infrahub-demo.log`;
  `nornir-infrahub-demo.wrapper.out` printed `nornir infrahub-demo FAIL 412s`). The runner's
  log ends:
  `File ".../orchestrator/src/fylgja_orchestrator/nornir/ospf.py", line 22, in <module>`,
  `from nornir import AInitNornir`, `ModuleNotFoundError: No module named 'nornir'`
  (`nornir-runner-first.log`). `make demo-down PURGE=1` ended it (`nornir-demo-down-0.log`).
  `make venv` on this branch's lock then resolved 140 packages and
  installed 12: `asyncssh` 2.24.1, `lxml` 6.1.3, `nornir` 3.7.0a1, `nornir-scrapli` 1.6.0a1,
  `nornir-utils` 0.3.0, `ntc-templates` 9.3.0, `scrapli` 2026.2.20, `scrapli-cfg` 2025.1.30,
  `scrapli-community` 2025.1.30, `scrapli-netconf` 2026.1.12, `textfsm` 2.1.1, and
  `fylgja-orchestrator` 1.1.0rc1 again from the clone's `orchestrator/` (`nornir-venv.log`).
  The two logs show that the venv lacked `nornir` until that `make venv`. The rest of the cause is
  the controller's reading, not a record: that the clone's `.venv` had been made on the
  candidate branch's lock (which lists no Nornir; counting `name = "nornir"` in the two locks
  gave 0 on the candidate and 5 on this branch), that the switch to this branch was made without
  `make venv`, and that the demonstration does not remake a venv that exists.
- **The rerun passed.** `make infrahub-demo` exited 0
  (`nornir-infrahub-demo-2.wrapper.out`: `nornir infrahub-demo ok 948s`) and printed "the
  rehearsal passed: 4 stages, 179.4 s, flow run
  387b2b8f-27f5-438e-80e5-74945eea4077" (`nornir-infrahub-demo-2.log`). The proposed change was
  `18ea347d-f9fd-94eb-2b62-c5121c36306f`; `fylgja` read `nornir-acceptance` at `229f9f4`, 75 s
  on. The demonstration printed its document as `local/demo/rehearsal.json` of the clone
  (`nornir-infrahub-demo-2.log`, last lines), saved as `nornir-rehearsal.json`.
- **The OSPF lines of the runner's log** (`nornir-runner.log`, 23:53:17 to 23:56:19), for the
  flow run `clever-armadillo`, which is `387b2b8f-27f5-438e-80e5-74945eea4077`:

  ```
  23:55:32.032 | ospf: stage 1, branch-point, checking within 120s
  23:55:37.472 | ospf: 4 of 4 link ends full
  23:55:51.638 | ospf: stage 2, third-link, checking within 120s
  23:55:56.563 | ospf: 6 of 6 link ends full
  23:56:08.060 | ospf: stage 3, n1-address, checking within 120s
  23:56:13.105 | ospf: 6 of 6 link ends full
  23:56:13.150 | skip: stage 4, head: unchanged
  ```

  Beside them, the log's `settle: verify ok, 2.43449s of 180s` after stage 1, `verify: stage 2,
  third-link: 19 hold, 0 fail` and `verify: stage 3, n1-address: 19 hold, 0 fail`; the twin
  `rh-347d78d1-fcff53dc` was destroyed ("gone") and the report posted; the flow run finished in
  state Completed. Each stage's check was passed in under 6 s of its 120 s (a derivation: 5.4 s,
  4.9 s and 5.0 s, from the timestamps above).
- **The thread was read.** No saved file records the reading; the controller's ledger quotes
  the maintainer's word after the rehearsal's thread in Infrahub: "I've read it". `make
  demo-down PURGE=1` then ended the runner, the core and Prefect and removed
  `fylgja-examples-infrahub` with its volumes (`nornir-demo-down.log`, at 00:28).

- **This repository's contract tiers fail on this branch, in two tests** (read on 2026-11-22,
  02:13 to 02:56 UTC, in the same clone switched to `nornir-acceptance` at `229f9f4`; the records
  are `examples-contracts/nornir/` of fylgja-core's acceptance directory, each target's log and
  `wrapper.out`, which ended `all rc=1`). Infrahub and NetBox were each brought up for their tier
  and purged after (`infrahub-down.log`, `netbox-down.log`).
  - **`make contract`** (`contract.log`; wrapper `contract FAIL 952s`): `infrahub/tests/contract/` 7
    passed in 245.26 s; then `orchestrator/tests/contract/` printed `1 failed, 10 passed in
    704.15s`. The failure is
    `tests/contract/test_prefect_contract.py::test_twin_rehearse_runs_to_its_document_and_posts_its_thread`,
    at `assert rehearsed["status"] == "passed"` (line 333): `AssertionError: assert 'failed' ==
    'passed'`. The log's line from the rehearsal: `fylgja-twin concluded False in 45.4 s:
    Rehearsal failed at stage 2 of 4: third-link`, then `The OSPF check found 3 failures at
    stage 2, third-link, the first n1: n1's OSPF state could not be read: the check could not
    run: KeyError: 'FYLGJA_CREDENTIAL_SRLINUX_USERNAME is not set' (ospf.node.unread). Stage 1
    passed. Stages 3 and 4 were not reached.` The tier's cancel test, in the same run, printed
    `fylgja-twin concluded False: this check's own deadline, 420 s after it began, passed: the
    run was asked to cancel`.
  - **`make contract-netbox`** (`contract-netbox.log`; wrapper `contract-netbox FAIL 151s`):
    `netbox/tests/contract/` printed `1 failed, 13 passed in 150.02s`, and the target stopped
    there (the log holds no run of the orchestrator's NetBox tier). The failure is
    `tests/contract/test_seed_contract.py::test_the_changes_two_steps_each_move_a_configuration`
    at `assert linked[name].split("\n")[1:] == wanted[name][1:], name` (line 140):
    `AssertionError: n1`, `assert ['# platform ... enable', ...] == ['# platform ...0.0.0.0',
    ...]`, `At index 3 diff: 'set / interface ethernet-1/1 description "to n2 ethernet-1/1"' !=
    'set / network-instance default protocols ospf instance main admin-state enable'`, `Right
    contains 5 more items, first extra item: 'set / interface ethernet-1/2 subinterface 0 ipv4
    admin-state enable'`. The expected configuration holds an OSPF line at index 3 where the
    rendered one does not, and 5 lines more.
  - **What the controller read**, beside the failures: `netbox/seed/main.yaml` of this branch
    is byte-identical to `netbox/seed/main.yaml` of fylgja-core's `archive/nornir-ospf` (the same
    sha256, read again for this entry by the fix wave's implementer, not the controller), and
    fylgja-core's `archive/nornir-ospf`'s diff from `e7cdc0c` changes no NetBox configuration
    template (the controller's reading of the diff).
  - **The controller's ruling, not a reading:** these two failures are this branch's own
    defects, carried from `nornir-ospf` as it was, and are left for a later fix. The runs show
    that the two tests fail on this branch at `229f9f4`, and no more.
