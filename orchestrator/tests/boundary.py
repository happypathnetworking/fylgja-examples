"""Copied from fylgja-core's core/tests/test_boundary.py at e7cdc0c968d481fd1f8446c344b6e0b4c4d37eeb; free to drift.

What the core's clients may never load (Constitution XI, D-025 in fylgja-core): the list of module prefixes and the
test of a module against it, which the rehearsal library's import test holds its own list beside."""

from __future__ import annotations

# What a client of the core must never load, by module or package prefix.
FORBIDDEN = (
    "compiler",
    "store",
    "local_store",
    "object_store",
    "driver",
    "drivers",
    "containerlab",
    "clabernetes",
    "reconcile",
    "queue",
    "push",
    "readiness",
    "credentials",
    "config",
    "packages",
    "server",
    "s3",
    "kubeapi",
    "lease",
)


def forbidden(module: str) -> bool:
    name = module.removeprefix("fylgja_core.")
    return any(name == f or name.startswith((f"{f}.", f"{f}_")) for f in FORBIDDEN)
