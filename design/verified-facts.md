# Verified facts

What this repository was built on is what fylgja-core's facts record at v1.0.0:
`https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/verified-facts.md`. The
section below is what this repository read for itself, over released packages.

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

Read on 2026-11-20 on the development host (the contract tiers late on 2026-11-19 UTC, by the
logs' own timestamps), in a fresh `git clone --branch phase-12/1-examples` of this repository
at `f8cacda`, with no `fylgja-core` checkout on any path its commands took; the clone's
`local/.env` was written by the maintainer for the node login and by the commands themselves
for the rest (the controller wrote four settings of the core's, below). Each run was made once.
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
- **The Infrahub demonstration's first try was refused at the host check, after Infrahub came
  up.** Its host checks passed, step 1 started Infrahub, which answered 143 s after Compose's
  start returned, and the demonstration then printed that the lab pool, which is the default
  172.20.0.0/16, had no /24 that neither a Docker network nor another twin held: Docker had
  given the Compose network `fylgja-examples-infrahub_default` the whole of it. The
  demonstration printed "set FYLGJA_LAB_POOL in local/.env, then run make infrahub-demo
  again", left Infrahub up, and `make` exited 2. The maintainer then set `FYLGJA_LAB_POOL` in
  the clone's `local/.env` (a site value, not recorded here). (`4-infrahub-demo.log`)
- **The Infrahub demonstration passed.** The rerun printed "the host's checks passed" and ran
  its 8 steps (Infrahub answered 0 s after Compose's start returned, the Infrahub already
  being up from the first try; `make infrahub-register` printed `fylgja` at `f8cacda`,
  in-sync and online, 76 s on); the flow run `8c2cc48f-5dc3-4a41-93e4-cdb0de315d83` of
  `twin-rehearse/main` went SCHEDULED, PENDING, RUNNING, COMPLETED, and the demonstration
  printed "the rehearsal passed: 4 stages, 148.2 s". The controller's record has the rerun
  exit 0 in 696 s. The report is in Infrahub, the proposed change "Rehearse third-link" of
  the branch `third-link`, its thread "Fylgja rehearsal"; the maintainer read it there and said
  it is correct. `make demo-down PURGE=1` ended the runner, the core and Prefect and removed
  the Compose project with its volumes. (`5-infrahub-demo.log`, `6-demo-down.log`)
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
