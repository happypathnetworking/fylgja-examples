#!/usr/bin/env python3
"""Build the example orchestrator's wheel from `orchestrator/` and `formats/` and install it outside the tree, beside
`fylgja-core`, `fylgja-infrahub` and `fylgja-netbox` at `VERSION`, taken from PyPI.

Run from the repository root: `python3 -I scripts/wheelcheck.py`, or `make wheelcheck`. It uses the standard
library alone. Everything happens in one temporary directory, so the tree is left as it was; uv builds and installs
from directories outside the tree, so no workspace or lock reaches what it checks, and a host with no `uv` on the PATH,
or another uv than the root `pyproject.toml` requires, is told so before anything is made. Needs the network, for
the build's requirements and for the three distributions and their dependencies, which are installed from the index
and never built here. The build's copy of the tree holds `VERSION` at its root beside `formats/`, as
`orchestrator/setup.py` reads it, and the wheel's `METADATA` says `VERSION`'s version. The wheel is built at the tree's
commit, `tree_commit`, which the build is given as `FYLGJA_BUILD_COMMIT` (the copy holds no `.git`), and holds it as
`fylgja_orchestrator/COMMIT`; and the installed command's `--version` is `<program> <version> (commit <commit>)`,
one line.

The check, `check_orchestrator`, runs in directories of its own, under `orchestrator/` in the temporary directory:

1. **Its wheel.** It is built by `uv build --wheel` from a copy of `orchestrator/` and
   `formats/` side by side, as `orchestrator/setup.py` finds `formats/`; its
   `fylgja_orchestrator/formats/` holds the formats of the example's two documents,
   `ORCHESTRATOR_FORMATS`, and no other, its `fylgja_orchestrator/infrahub/queries/` the tree's
   GraphQL documents of the change source, of which there is at least one, and no other, and the
   package carries `py.typed`.
2. **Beside the three pinned distributions**, `uv pip install fylgja-core==<VERSION> fylgja-infrahub==<VERSION>
   fylgja-netbox==<VERSION> <its wheel>` in an empty environment (`install_pinned`), the core with no extra, the
   readers since the example's two change sources read through them: `PROBE_ORCHESTRATOR`, run outside the tree,
   finds the formats the package reads beside it and not in the tree; a plan 1 and a rehearsal 1 document validate,
   the second's `plan` held to the wheel's own plan 1, and `{}` does not; the rehearsal
   library's entry points import; no module of the server's libraries, either reader or Prefect
   (`NOT_BESIDE`) is loaded then, and none of the server's libraries that Prefect does not bring
   (`NOT_INSTALLED`) is installed; and then the Infrahub change source imports and reads each of
   its GraphQL documents from the installed package, outside the tree, and the NetBox change
   source imports; each change source loads nothing of the other or of its reader (`CROSSED`),
   the NetBox one judged once the Infrahub one's modules and its reader's are dropped from
   `sys.modules`, so that an import of either is made again and seen. In a fresh interpreter
   there, `PROBE_EDGE` imports the command's module and finds nothing of the server's libraries
   or Prefect (`NOT_BESIDE_EDGE`) loaded; then `fylgja-orchestrator --help` and
   `fylgja-orchestrator stage mark --help` exit 0, and `fylgja-orchestrator --version` names `VERSION` and the
   tree's commit.

`main` prints the check's line. Exit 0 when it passes; 1 with the reason on stderr otherwise.
"""

import email.message
import email.parser
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The one version the distributions are pinned at, and the example's wheel is built at, copied beside the build's copy
# of the tree, as `formats/` is.
VERSION = ROOT / "VERSION"
# What the build reads at the root: the version.
ROOT_FILES = ("VERSION",)
# The three distributions the example's wheel is installed beside, from the index, at `VERSION`.
PINNED = ("fylgja-core", "fylgja-infrahub", "fylgja-netbox")
PRIVATE_CLASSIFIER = "Private :: Do Not Upload"
# The variable the build reads the commit it is made at from (`orchestrator/setup.py`).
COMMIT_VARIABLE = "FYLGJA_BUILD_COMMIT"

# The formats the example's wheel carries under `fylgja_orchestrator/formats/`, those of its two documents, and no
# other: stated here and not read from `orchestrator/setup.py`, so a list emptied or widened there fails the check.
ORCHESTRATOR_FORMATS = ("plan-1.schema.json", "rehearsal-1.schema.json")
ORCHESTRATOR_PREFIX = "fylgja_orchestrator/formats/"
ORCHESTRATOR_TYPED = "fylgja_orchestrator/py.typed"
ORCHESTRATOR_QUERIES = "fylgja_orchestrator/infrahub/queries/"
# The tree's GraphQL documents of the change source, each of which the example's wheel carries under
# `ORCHESTRATOR_QUERIES`, and no other.
SOURCE_QUERIES = ROOT / "orchestrator" / "src" / "fylgja_orchestrator" / "infrahub" / "queries"
# What the example's rehearsal library never loads beside the base and the two readers: the libraries of the core's
# `server` extra, either reader and Prefect, each a module or package; of those, what the command's module never loads,
# all but the two readers, which the change sources it opens read through; and what is not installed there, the
# server's libraries that Prefect does not bring: Prefect 3.9.2 brings starlette and uvicorn (fylgja-core's
# verified-facts.md, "Prefect 3.9.2"). A dotted name is judged whole, as `PROBE_READER` judges one.
READERS = ("fylgja_infrahub", "fylgja_netbox")
NOT_BESIDE = ("starlette", "uvicorn", "grpc", "google.protobuf", "httpx2", "lightkube", "msgspec", "pygnmi", "prefect",
              *READERS)
NOT_BESIDE_EDGE = tuple(name for name in NOT_BESIDE if name not in READERS)
NOT_INSTALLED = ("grpc", "google.protobuf", "httpx2", "lightkube", "msgspec", "pygnmi")
# What each change source, by its package under `fylgja_orchestrator`, never loads: the other source and its reader.
# `orchestrator/tests/test_boundary_edge.py` holds the same of what each names, and
# `orchestrator/tests/test_wheelcheck.py` holds the two tuples equal.
CROSSED = (
    ("infrahub", ("fylgja_netbox", "fylgja_orchestrator.netbox")),
    ("netbox", ("fylgja_infrahub", "fylgja_orchestrator.infrahub")),
)

# Run beside the base and the two readers, given the tree's root and then a JSON object of `NOT_BESIDE`,
# `NOT_INSTALLED` and `CROSSED`: the example's formats, outside the tree; its two documents validated; its rehearsal
# library imported; nothing of `NOT_BESIDE` loaded, and nothing of `NOT_INSTALLED` installed; then the Infrahub change
# source imported, with nothing of what `CROSSED` gives it loaded, and each of its GraphQL documents read from the
# installed package, outside the tree; then, the Infrahub source's modules and its reader's dropped from
# `sys.modules`, the NetBox change source imported, with nothing of what `CROSSED` gives it loaded again.
PROBE_ORCHESTRATOR = r"""
import importlib.util
import json
import sys
from pathlib import Path

import fylgja_orchestrator
from fylgja_core import schemas

root, given = Path(sys.argv[1]).resolve(), json.loads(sys.argv[2])
crossed = dict(given["crossed"])


def under(name, roots):
    return any(name == root or name.startswith(f"{root}.") for root in roots)

here = Path(fylgja_orchestrator.__file__).resolve().parent / "formats"
found = schemas.formats_dir("fylgja_orchestrator")
assert found == here, f"formats_dir('fylgja_orchestrator') is {found}, not {here}"
assert root not in found.parents, f"formats_dir('fylgja_orchestrator') {found} is under the tree {root}"

from fylgja_orchestrator.rehearsal import Limits, create, plan, rehearse, stage_list, step
from fylgja_orchestrator.rehearsal.documents import validate
from fylgja_orchestrator.rehearsal.report import render

planned = {"plan_version": "1", "status": "empty", "headline": "Nothing to plan",
           "change": {"id": "pc-1", "where": "a change"}, "scope": "tag:fylgja", "read_at": "2026-11-09T10:15:11Z",
           "findings": [], "stages": []}
rehearsed = {"rehearsal_version": "1", "status": "not_rehearsed", "headline": "Not rehearsed", "plan": planned,
             "twin": "rh-00000000-00000000", "run_id": "run-1", "took_s": 0, "stages": [], "already_failing": [],
             "reclaimed": [], "findings": []}
assert validate("plan-1", planned) == [], validate("plan-1", planned)
assert validate("rehearsal-1", rehearsed) == [], validate("rehearsal-1", rehearsed)
assert schemas.validator("rehearsal-1", "fylgja_orchestrator").is_valid(rehearsed), "rehearsal-1 refuses a rehearsal"
assert validate("rehearsal-1", {**rehearsed, "plan": {}}) != [], "rehearsal-1 does not hold its plan to plan 1"
assert validate("plan-1", {}) != [], "plan-1 accepts {}"
assert validate("rehearsal-1", {}) != [], "rehearsal-1 accepts {}"

loaded = sorted(m for m in sys.modules if any(m == name or m.startswith(f"{name}.") for name in given["not_loaded"]))
assert not loaded, f"loaded by the rehearsal library: {loaded}"


def present(name):
    # Whether `name` is installed: a missing parent package of a dotted name means it is not.
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


installed = [name for name in given["not_installed"] if present(name)]
assert not installed, f"installed beside the base and the two readers: {installed}"

# Only now, the rehearsal's loads judged: the Infrahub change source imports its reader, and reads each of its GraphQL
# documents from the installed wheel's package data, each naming its operation.
from fylgja_orchestrator.infrahub import transport

assert "fylgja_infrahub" in sys.modules, "the Infrahub change source loaded no fylgja_infrahub: the probe is blind"
loaded = sorted(m for m in sys.modules if under(m, crossed["infrahub"]))
assert not loaded, f"loaded by the Infrahub change source: {loaded}"

queries = Path(transport.__file__).resolve().parent / "queries"
assert root not in queries.parents, f"the Infrahub change source's queries {queries} are under the tree {root}"
names = sorted(path.stem for path in queries.glob("*.gql"))
assert names, f"no *.gql under {queries}"
for name in names:
    text, operation = transport._document(name)
    assert operation and operation in text, f"queries/{name}.gql names no operation"

# And the NetBox change source, which imports its reader, from the installed package, outside the tree: the Infrahub
# source's modules and its reader's dropped first, so that an import of either is made again and seen.
for name in [m for m in sys.modules if under(m, crossed["netbox"])]:
    del sys.modules[name]
import fylgja_orchestrator.netbox

assert "fylgja_netbox" in sys.modules, "the NetBox change source loaded no fylgja_netbox: the probe is blind"
loaded = sorted(m for m in sys.modules if under(m, crossed["netbox"]))
assert not loaded, f"loaded by the NetBox change source: {loaded}"

here = Path(fylgja_orchestrator.netbox.__file__).resolve()
assert root not in here.parents, f"the NetBox change source {here} is under the tree {root}"
assert fylgja_orchestrator.netbox.NetBoxSource.comment_limit is None, "the NetBox change source bounds its report"
"""

# Run in a fresh interpreter beside the base and the two readers, given `NOT_BESIDE_EDGE` as one JSON list: the
# command's module imported, and nothing of the list loaded, Prefect among it, since a command calls the library in its
# own process (D-085).
PROBE_EDGE = r"""
import json
import sys

import fylgja_orchestrator.edge.cli

absent = json.loads(sys.argv[1])
loaded = sorted(m for m in sys.modules if any(m == name or m.startswith(f"{name}.") for name in absent))
assert not loaded, f"loaded by the command's module: {loaded}"
"""


class Failure(Exception):
    pass


def tree_version(path: Path = VERSION) -> str:
    """The tree's version, the one line of `path` stripped; `Failure` naming the file where it is not one line."""
    try:
        lines = path.read_text().splitlines()
    except OSError as e:
        raise Failure(f"{path} cannot be read: {e.strerror or e}") from e
    if len(lines) != 1 or not lines[0].strip():
        raise Failure(f"{path} is not one line holding the version")
    return lines[0].strip()


def metadata(wheel: Path) -> email.message.Message:
    """The wheel's `*.dist-info/METADATA`, parsed; `Failure` where it holds none, or more than one."""
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if n.count("/") == 1 and n.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise Failure(f"{wheel.name} holds {len(names)} METADATA, not one")
        return email.parser.Parser().parsestr(archive.read(names[0]).decode())


def versioned(wheel: Path, version: str) -> None:
    """Nothing, once the wheel's `METADATA` says `Version: <version>`; `Failure` naming both otherwise."""
    said = metadata(wheel)["Version"]
    if said != version:
        raise Failure(f"{wheel.name} is version {said}, and VERSION says {version}")


@functools.cache
def tree_commit() -> str:
    """The tree's commit as `Makefile`'s `COMMIT` and each `setup.py` read it: git's HEAD at `ROOT`, `-dirty` after it
    where `git status --porcelain` prints anything; `unknown` where git cannot say. Worked out once, so the builds and
    the checks of one run agree whatever changes in the tree meanwhile."""
    outputs = []
    for argv in (["rev-parse", "HEAD"], ["status", "--porcelain"]):
        try:
            done = subprocess.run(["git", "-C", str(ROOT), *argv], capture_output=True, text=True, check=False)
        except OSError:
            return "unknown"
        if done.returncode != 0:
            return "unknown"
        outputs.append(done.stdout.strip())
    head, status = outputs
    return head + ("-dirty" if status else "") if re.fullmatch(r"[0-9a-f]{40}", head) else "unknown"


def held_commit(wheel: Path, package: str, commit: str) -> None:
    """Nothing, once the wheel holds `<package>/COMMIT` saying `commit` on one line; `Failure` naming the wheel and the
    file otherwise."""
    with zipfile.ZipFile(wheel) as archive:
        try:
            said = archive.read(f"{package}/COMMIT").decode()
        except KeyError:
            raise Failure(f"{wheel.name} holds no {package}/COMMIT") from None
    if said != commit + "\n":
        raise Failure(f"{wheel.name}'s {package}/COMMIT says {said.strip()!r}, and the tree is at {commit}")


def private_metadata(wheel: Path) -> None:
    """Nothing, once the example's wheel is marked `Classifier: Private :: Do Not Upload`, the one classifier it holds,
    so that PyPI refuses it (D-106), and holds no `Project-URL`; `Failure` otherwise."""
    found = metadata(wheel)
    if found.get_all("Classifier") != [PRIVATE_CLASSIFIER]:
        raise Failure(f"{wheel.name} holds the classifiers {found.get_all('Classifier')}, "
                      f"not [{PRIVATE_CLASSIFIER!r}]: it could be uploaded")
    if found.get_all("Project-URL") or found.get_all("Author") or found.get_all("Author-email"):
        raise Failure(f"{wheel.name} states a project URL or an author, and the example states neither")


def held_licence(wheel: Path, package: str, expected: bool = True) -> None:
    """Nothing, once the wheel holds `<package>/LICENSE`, the root `LICENSE`'s bytes (or, where `expected` is false,
    holds no file of that name); `Failure` naming the wheel and the file otherwise."""
    with zipfile.ZipFile(wheel) as archive:
        try:
            held = archive.read(f"{package}/LICENSE")
        except KeyError:
            held = None
    if expected and held is None:
        raise Failure(f"{wheel.name} holds no {package}/LICENSE")
    if expected and held != (ROOT / "LICENSE").read_bytes():
        raise Failure(f"{wheel.name}'s {package}/LICENSE is not the root LICENSE's bytes")
    if not expected and held is not None:
        raise Failure(f"{wheel.name} holds {package}/LICENSE, and the example carries none")


def answers_version(command: Path, program: str, version: str, commit: str, cwd: Path) -> None:
    """Nothing, once `command --version` exits 0 printing exactly `<program> <version> (commit <commit>)` and a newline
    on stdout; `Failure` with what it printed otherwise."""
    done = exits([str(command), "--version"], cwd, 0)
    expected = f"{program} {version} (commit {commit})\n"
    if done.stdout != expected or done.stderr:
        raise Failure(f"{command.name} --version printed {done.stdout!r} on stdout and {done.stderr!r} on stderr, "
                      f"not {expected!r}")


def run(argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    """`argv` run in `cwd`, in `env` where it is given, which must exit 0; `Failure` with what it printed otherwise."""
    exits(argv, cwd, 0, env)


def exits(
    argv: list[str], cwd: Path, status: int, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """`argv` run in `cwd`, in `env` where it is given and else in this process's environment, which must exit
    `status`: what it printed, or `Failure` with that otherwise."""
    try:
        done = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    except OSError as e:
        raise Failure(f"{argv[0]} cannot be run: {e}") from e
    if done.returncode != status:
        raise Failure(f"{' '.join(argv[:4])} ... exited {done.returncode}, not {status}:\n{done.stdout}{done.stderr}")
    return done


def uv() -> str:
    """The `uv` on the PATH, which must be the version the root `pyproject.toml` requires: every call of this check runs
    outside the tree, where uv never reads that. `Failure` in one line where there is none or it is another, before
    anything is made."""
    found = shutil.which("uv")
    if found is None:
        raise Failure('uv is not on the PATH: the wheel check builds and installs by it (CONTRIBUTING.md, "Tooling")')
    required = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["uv"]["required-version"].removeprefix("==")
    try:
        said = subprocess.run([found, "--version"], capture_output=True, text=True, check=False).stdout.split()
    except OSError as e:
        raise Failure(f"{found} cannot be run: {e}") from e
    version = said[1] if len(said) > 1 else "unreadable"
    if version != required:
        raise Failure(f"uv {version} is on the PATH, and the root pyproject.toml requires uv {required}")
    return found


def venv(path: Path) -> Path:
    """An empty environment made at `path` by uv, over this interpreter, outside any project: its `bin/`."""
    run([uv(), "venv", "--no-project", "--no-python-downloads", "--python", sys.executable, str(path)], path.parent)
    return path / "bin"


def wheel(source: Path, dist: Path) -> None:
    """The one wheel of the distribution at `source`, built by `uv build` into `dist`, from `dist`'s parent, at the
    tree's commit: the build is given `FYLGJA_BUILD_COMMIT`, whatever this process's environment holds, since the copy
    it builds from holds no `.git`; where the tree's commit is `unknown` it is given none, and the build says so."""
    env = {k: v for k, v in os.environ.items() if k != COMMIT_VARIABLE}
    if tree_commit() != "unknown":
        env[COMMIT_VARIABLE] = tree_commit()
    run([uv(), "build", "--wheel", "--no-python-downloads", "--python", sys.executable, "--out-dir", str(dist),
         str(source)], dist.parent, env)


def install(env: Path, *requirements: str) -> None:
    """`requirements` installed by `uv pip` from the index into the environment whose `bin/` is `env`, from `env`'s
    grandparent."""
    run([uv(), "pip", "install", "--python", str(env / "python"), *requirements], env.parent.parent)


def install_pinned(env: Path, *wheels: str) -> None:
    """`fylgja-core`, `fylgja-infrahub` and `fylgja-netbox` at the tree's `VERSION`, taken from the index, and the
    `wheels` given, installed into the environment whose `bin/` is `env`."""
    version = tree_version()
    install(env, *(f"{name}=={version}" for name in PINNED), *wheels)


def copy_root_files(src: Path) -> None:
    """`ROOT_FILES` copied to the root of a build's copy of the tree, where `orchestrator/setup.py` reads them
    (`../VERSION`)."""
    for name in ROOT_FILES:
        shutil.copyfile(ROOT / name, src / name)


def carried_by_example(wheel: Path) -> int:
    """How many GraphQL documents the example's wheel carries, once it carries under `ORCHESTRATOR_PREFIX` exactly
    `ORCHESTRATOR_FORMATS`, under `ORCHESTRATOR_QUERIES` exactly the tree's `*.gql` in `SOURCE_QUERIES`, and
    `ORCHESTRATOR_TYPED`; `Failure` otherwise."""
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    queries = {path.name for path in SOURCE_QUERIES.glob("*.gql")}
    if not queries:
        raise Failure(f"the tree's {SOURCE_QUERIES.relative_to(ROOT)} holds no *.gql: the queries' comparison would "
                      "pass vacuously")
    problems: list[str] = []
    for prefix, expected, listed in (
        (ORCHESTRATOR_PREFIX, set(ORCHESTRATOR_FORMATS), "ORCHESTRATOR_FORMATS in scripts/wheelcheck.py"),
        (ORCHESTRATOR_QUERIES, queries, f"the tree's {SOURCE_QUERIES.relative_to(ROOT)}"),
    ):
        found = {n[len(prefix) :] for n in names if n.startswith(prefix) and not n.endswith("/")}
        problems += [f"missing from the wheel: {prefix}{n} ({listed})" for n in sorted(expected - found)]
        problems += [f"extra in the wheel: {prefix}{n} ({listed})" for n in sorted(found - expected)]
    if ORCHESTRATOR_TYPED not in names:
        problems.append(f"missing from the wheel: {ORCHESTRATOR_TYPED}")
    if problems:
        raise Failure(f"{wheel.name} does not carry the example's formats, its GraphQL documents and py.typed, and no "
                      "other:\n" + "\n".join(problems))
    return sum(1 for n in names if n.startswith(ORCHESTRATOR_QUERIES) and n.endswith(".gql"))


def check_orchestrator(tmp: Path) -> str:
    """The example orchestrator's check, under `tmp/orchestrator`: its wheel built from a copy of `orchestrator/` and
    `formats/`, and what it carries; then the wheel installed in an empty venv beside `fylgja-core`, `fylgja-infrahub`
    and `fylgja-netbox` at `VERSION` from the index (`install_pinned`), where `PROBE_ORCHESTRATOR` and then `PROBE_EDGE`
    run outside the tree, and the command answers `--help`, `--version` and `stage mark --help`."""
    here = tmp / "orchestrator"
    src, dist = here / "src", here / "dist"
    shutil.copytree(
        ROOT / "orchestrator",
        src / "orchestrator",
        ignore=shutil.ignore_patterns(".venv", "tests", "build", "*.egg-info", "__pycache__", ".*_cache"),
    )
    shutil.copytree(ROOT / "formats", src / "formats")
    copy_root_files(src)
    wheel(src / "orchestrator", dist)
    wheels = sorted(dist.glob("*.whl"))
    if len(wheels) != 1:
        raise Failure(f"expected one wheel in {dist}, found {[w.name for w in wheels]}")
    built = wheels[0]
    versioned(built, tree_version())
    held_commit(built, "fylgja_orchestrator", tree_commit())
    private_metadata(built)
    held_licence(built, "fylgja_orchestrator", expected=False)
    queries = carried_by_example(built)
    env = venv(here / "venv")
    install_pinned(env, str(built))
    given = {"not_loaded": list(NOT_BESIDE), "not_installed": list(NOT_INSTALLED), "crossed": list(CROSSED)}
    run([str(env / "python"), "-I", "-c", PROBE_ORCHESTRATOR, str(ROOT), json.dumps(given)], tmp)
    run([str(env / "python"), "-I", "-c", PROBE_EDGE, json.dumps(list(NOT_BESIDE_EDGE))], tmp)
    run([str(env / "fylgja-orchestrator"), "--help"], tmp)
    answers_version(env / "fylgja-orchestrator", "fylgja-orchestrator", tree_version(), tree_commit(), tmp)
    run([str(env / "fylgja-orchestrator"), "stage", "mark", "--help"], tmp)
    return (f"wheelcheck: {built.name} is marked {PRIVATE_CLASSIFIER!r} and carries no licence file; it carries the "
            f"example's {len(ORCHESTRATOR_FORMATS)} formats and no other, and its {queries} GraphQL documents; beside "
            f"{', '.join(f'{name}=={tree_version()}' for name in PINNED)} from the index alone it validates a plan and "
            "a rehearsal outside the tree, its rehearsal library imports with nothing of the server, either reader or "
            "Prefect, both change sources import, each with nothing of the other or its reader, its command's module "
            "with nothing of the server or Prefect, and fylgja-orchestrator answers --help, stage mark --help and "
            "--version")


def main() -> int:
    try:
        uv()
    except Failure as failure:
        print(f"wheelcheck: {failure}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="fylgja-wheelcheck-") as name:
        try:
            print(check_orchestrator(Path(name)))
        except Failure as failure:
            print(f"wheelcheck: {failure}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
