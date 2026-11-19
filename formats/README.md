# Formats

The example orchestrator's two documents: the plan of a change and the rehearsal of it. Each
has one version, specified by its file here, as fylgja-core's formats do
([D-002](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-002), Constitution XII). A change found while building the
example is made here, in the same change as the code that reads or writes it. The formats the
core and the readers read and write are fylgja-core's, in its
[`formats/`](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/formats/README.md), and are carried by the installed distributions.

This directory stays the one place a format is changed ([D-066](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-066)):
the example's wheel carries these two as package data, copied when it is built from the list in
`orchestrator/setup.py`, and its tests read them from here. The wheel carries no format of the core's.

Every property has a description that names its consumer. `$id`s are under
`https://github.com/happypathnetworking/fylgja/schemas/`, as they were where the formats began,
and are identifiers, never fetched. Each document `$ref`s nothing outside the two files, so the
wheel resolves them alone.

## The files

| File | Introduced by |
|---|---|
| [`plan-1.schema.json`](plan-1.schema.json) | [D-086](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-086) |
| [`rehearsal-1.schema.json`](rehearsal-1.schema.json) | [D-086](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-086) |

## Notes

1. **The plan and the rehearsal are the example orchestrator's documents,** carried by its wheel
   and not the core's ([D-084](https://github.com/happypathnetworking/fylgja/blob/v1.0.0/design/decisions.md#d-084)). They were fylgja-core's
   `formats/` entries until fylgja-examples took them, and their content did not change in the move.
2. **The example's rules are its own,** in [`orchestrator/rules.md`](../orchestrator/rules.md),
   as findings 1 holds the core's rules alone.
