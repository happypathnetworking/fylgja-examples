# Working notes for coding agents

This is **fylgja-examples**: the example orchestrator and the two demonstrations of
[fylgja-core](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/README.md), which turns a blueprint (a network's intent, content-addressed)
into a twin running real network operating system images. The example rehearses a change of a
source of truth on a twin, a proposed change in Infrahub or a branch in NetBox, and is a client
of the core like any other. The demonstrations make that rehearsal from one command each:
`make infrahub-demo` and `make netbox-demo`.

It installs the released packages `fylgja-core`, `fylgja-infrahub` and `fylgja-netbox`, each
pinned exactly at `VERSION`, and reads nothing of a fylgja-core checkout. An experiment here
changes nothing there.

## Read first

- `CONTRIBUTING.md`: setup, tiers, the development Infrahub and NetBox, the runbooks, the
  demonstrations, the acceptance runs, and moving to a release.
- `design/decisions.md`: this repository's own log; check it before proposing a change of a
  decision.
- fylgja-core's entries about the example bind this repository until an entry here supersedes
  one: [D-085](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-085) to [D-088](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-088),
  [D-092](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-092) to [D-094](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-094),
  [D-097](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-097), [D-100](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-100),
  [D-101](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-101), [D-104](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-104) and
  [D-111](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/decisions.md#d-111). So do fylgja-core's
  [constitution](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/constitution.md) and [architecture](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/architecture.md).
- `formats/README.md`: the example's two formats, one current version each.
- `docs/demonstrations.md`: what a demonstration needs, does, writes and leaves.
- [fylgja-core's integrating page](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/docs/integrating.md): how to join Fylgja to a source of
  truth and a platform of your own, walked through this example.
- `design/verified-facts.md`: what this repository read for itself. What the development
  Infrahub, NetBox, Prefect, containerlab and the network operating systems do is read in
  [fylgja-core's facts](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/design/verified-facts.md): read it when a task touches one of them,
  and trust it over recollection.

## Rules

- **A change that alters a decision is a new entry in `design/decisions.md`, then a pull
  request.** The log is append-only: a changed decision is a new entry that supersedes the old
  one, and an entry of fylgja-core's is superseded the same way.
- **A change to a format is made in `formats/`,** in the same change as the code.
- **Verify against the running system** before asserting how Infrahub, NetBox, Prefect, uv,
  containerlab or a network operating system behaves. Record the result in
  `design/verified-facts.md`.
- **Read nothing of fylgja-core's tree.** A test or script reads what the installed
  distributions carry, or this repository's own copy. A link into fylgja-core is at a tag, never
  at `main`.
- **Never echo, log or persist a token or a password.** `local/.env` holds every value.
- **Commit with a conventional-commit message whose body says why.** Never commit `local/`.
  Never push without being asked.

## Build and test

`make venv` (it needs uv 0.12.23), then `make lint` (ruff, mypy strict), `make test` (the pure
tier, no infrastructure), `make linkcheck` and `make wheelcheck`.
