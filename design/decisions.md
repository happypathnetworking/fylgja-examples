# Decision log

This is the decision log of fylgja-examples: the decisions that are this repository's own. Each
entry states a decision in force, with its context, the options considered, the decision and its
consequences. **The options considered are the point.** Check them before proposing a rejected
alternative.

- **Append-only.** A changed decision is a new entry that supersedes the old one, and a number
  is never reused. The old entry keeps its text, and its status line names the entry that
  superseded it, the date, and the part, when only a part.
- **Ids are `E-NNN`,** from E-001, so that they never collide with fylgja-core's `D-NNN`. Cite an
  entry by its id and link it by its anchor: `decisions.md#e-nnn`.
- **fylgja-core's entries about the example bind here** until an entry here supersedes one. They
  are named in [AGENTS.md](../AGENTS.md). An entry here supersedes one of fylgja-core's in a
  status line that names it, with its id and the part, as `Supersedes fylgja-core's D-104 in
  one part`; the entry there keeps its text and is read with that line.
- **A reading of a running system** is not an entry: it goes to
  [verified-facts.md](verified-facts.md), with its version and date.

## Index

| ID | Decision |
|---|---|
| [E-001](#e-001) | The example orchestrator and the demonstrations are a repository of their own, on the released packages |

<a id="e-001"></a>
### E-001 — The example orchestrator and the demonstrations are a repository of their own, on the released packages

**Status:** Accepted 2026-11-19. Follows fylgja-core's D-126 to D-128 (to be released
with 1.1.0), which settled it there; this entry says what it is here and takes the ids from here
on.

#### Context

The example orchestrator was a member of fylgja-core's workspace, and the demonstrations ran
from its tree. An experiment in the example, a library pinned at an alpha and a network given
addresses, moved the lock the core is released from and the fixtures its tests hold. The core and
the readers are released together at one version; the example is a client of them, and is held to
the standard of an example.

#### Options considered

- **The example in the core's repository, as it was.** Not taken: its pins entered the core's
  lock, and its fixtures were the core's.
- **A checkout of the core beside it, as a path source.** Not taken: every tier would need that
  checkout, and a demonstration would show the core's `main` and not a release.
- **Ranges of the core's versions within the major.** Not taken: the example's tests serve the
  core in process through modules no page of the core gives, and would break on a release that
  kept its promise.
- **The released packages, pinned exactly, in a lock of its own.** Chosen.

#### Decision

- **This repository is `happypathnetworking/fylgja-examples`,** Apache-2.0. It holds the example
  orchestrator and its tests, the example's two formats, the scripts and make targets that run
  the demonstrations, copies of the seeds and fixtures its tests read, and the development
  Infrahub and NetBox as the example runs them. Its history starts at one commit: the moved tree
  as fylgja-core held it at a commit its message names.
- **It installs `fylgja-core[server]`, `fylgja-infrahub` and `fylgja-netbox` from PyPI,** each
  pinned exactly at `VERSION`, with a lock of its own at the uv version fylgja-core requires. The
  core a demonstration runs is the installed release, with its wheel's packages and
  `FYLGJA_PACKAGES` unset. It does not depend on `fylgja-nautobot`, since the example has no
  Nautobot source.
- **No test or script reads a path of a fylgja-core checkout.** What it needs of the core it
  reads from the installed distributions, or from this repository's own copy. A change that needs
  both repositories installs a checkout's members over the locked environment, by the make
  variable `CORE`; the lock stays the release's, CI never sets it, and the change merges here
  once the release is out.
- **Its network is its own.** The seeds, templates and fixtures here may differ from
  fylgja-core's. Its Compose projects are `fylgja-examples-infrahub` and
  `fylgja-examples-netbox`, with the published ports fylgja-core's take, so a host runs one source
  at a time, and its NetBox takes the subnet 192.0.2.0/24.
- **Its `VERSION` is the release, or the candidate, it pins,** and its first tag is `v1.1.0`. The
  example's distribution takes it and is published nowhere. Moving to a release is a commit
  here, with its tiers and both demonstrations made again, then the tag
  ([CONTRIBUTING.md](../CONTRIBUTING.md#moving-to-a-release)).
- **Its process is its own:** `AGENTS.md`, `CONTRIBUTING.md`, this log, and `verified-facts.md`,
  which begins by pointing at fylgja-core's. Its CI gates every pull request by lint, the pure
  tier, the link check and the check of the example's wheel.

#### Consequences

- A fix of the core that the example needs reaches it at the next release.
- A release has one more step: the pins moved and the demonstrations made here, then the tag.
- fylgja-core's pages link into this repository at a tag, never at `main`, and this repository
  links into fylgja-core's at the tag of the release it pins.
