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
