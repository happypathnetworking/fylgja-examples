# Fylgja examples

The example orchestrator and the demonstrations of [Fylgja](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/README.md). Fylgja turns a
blueprint, a network's intent, into a twin: that network running on real network operating system
images, where a change is rehearsed before it reaches production. This repository shows how to
join it to a source of truth.

The example orchestrator, under `orchestrator/`, rehearses a change of a source of truth on a
twin and files the report where the source files such things: a proposed change in
[Infrahub](https://github.com/opsmill/infrahub), or a branch in NetBox. It is a client of the
core like any other, through the core's API alone.
[Integrating Fylgja](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/docs/integrating.md) walks through it.

> **This is the `nornir-ospf` branch,** kept off `main` on purpose. It adds one judgement to the
> example orchestrator's rehearsal: after each stage, every link between two OSPF-speaking devices
> has a FULL adjacency on both ends, checked over Nornir 3.7.0a1's asyncio runner and
> nornir-scrapli 1.6.0a1, both alphas pinned exactly. Only the example, the Infrahub seed and
> template, and the fixtures change; the core and the readers are the release `VERSION` names.
> Its design is `docs/superpowers/specs/2026-11-16-nornir-ospf-check-design.md`.
>
> Run it with `make infrahub-demo` from a checkout of this branch. When switching the demo between
> `main` and this branch, run `make demo-down PURGE=1` first: the seed loads nothing onto an
> Infrahub that holds the devices already, so the other branch's devices, without this branch's
> link addresses, would stay, and the check would find no OSPF instance.
>
> Then run `make venv`: this branch's lock adds Nornir and nornir-scrapli to `main`'s, and a
> demonstration makes `.venv` only where it is missing, never remaking one that exists, so a venv
> made on the other branch would be run as it is.

## One release

The example installs the released packages from PyPI, `fylgja-core`, `fylgja-infrahub` and
`fylgja-netbox`, each pinned exactly at one release, the one `VERSION` names, and its lock is its
own. A change here is made against the pinned release; one that needs a change of the core is built
against a checkout of it and merges here once that release is out. [CONTRIBUTING.md](CONTRIBUTING.md#moving-to-a-release) says how the pins move.

## A demonstration

From a clone, on a host that meets [what the demonstrations need](docs/demonstrations.md), one
command starts a source of truth, seeds it with a network, makes a change in it and rehearses the
change on a twin:

```sh
make netbox-demo
```

`make infrahub-demo` does the same with Infrahub, from a branch, since it refuses a detached head.
`make demo-down` ends what either started. [The demonstrations](docs/demonstrations.md) say what
each writes and leaves.

## Read on

- [CONTRIBUTING.md](CONTRIBUTING.md) says how to set up, test and change the repository, and
  holds the runbooks the demonstrations take.
- [fylgja-core](https://github.com/happypathnetworking/fylgja/blob/v1.1.0/README.md) holds the core, the two readers and the pages of the server, the
  command and API 1.

## Licence

[Apache License 2.0](LICENSE).
