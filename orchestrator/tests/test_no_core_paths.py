"""This repository reads no path of fylgja-core, links to neither repository at `main`, and says where each copy came
from (D-124: its packages are the core's wheel's).

What a test or a script needs of fylgja-core is read from the installed distributions (`fylgja_core.packages.shipped()`,
`fylgja_core.schemas`) or from this repository's own copy of it.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = "orchestrator/tests/test_no_core_paths.py"
SOURCE_COMMIT = "e7cdc0c968d481fd1f8446c344b6e0b4c4d37eeb"

CODE = (".py", ".sh", ".toml", ".yml", ".yaml", "Makefile")
OUTSIDE = (
    re.compile(r"""(?:parents\[\d\]|ROOT|HERE|TESTS)\s*/\s*["'](?:core|readers|psp|probes)["']"""),
    re.compile(r"""\.\./(?:core|readers|psp|probes)/"""),
    re.compile(r"""["']core["']\s*/\s*["']tests["']"""),
)
"""What a line of code says to read a directory of fylgja-core: a path built from this tree's root or a parent of the
file, or a relative path out of the tree."""
PYPROJECT = re.compile(r"\bcore/tests\b|\breaders/")

TO_BE_TRIMMED = ("scripts/wheelcheck.py",)
"""Files still holding fylgja-core's own build checks, which the trim of the wheel check removes."""

AT_MAIN = re.compile(
    r"github\.com/happypathnetworking/fylgja(?:-examples)?/(?:blob|tree|raw)/(?:main|HEAD)(?![\w.-])"
)

COPIES = {
    "orchestrator/tests/fakes.py": "core/tests/fakes.py",
    "orchestrator/tests/boundary.py": "core/tests/test_boundary.py",
    "infrahub/schema/fylgja-probe.yml": "readers/infrahub/schema/fylgja-probe.yml",
}
"""Each copy of a file of fylgja-core, by its path here, and the path it was copied from."""


def tracked() -> list[str]:
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [path for path in listed.decode().split("\0") if path]


def text(path: str) -> str | None:
    try:
        return (ROOT / path).read_text()
    except UnicodeDecodeError:
        return None


def test_no_tracked_file_reads_a_path_of_fylgja_core() -> None:
    found = []
    held = [path for path in tracked() if path != HERE and path not in TO_BE_TRIMMED]
    for path in held:
        body = text(path)
        if body is None:
            continue
        name = Path(path).name
        if name.endswith(CODE) or name == "Makefile":
            pattern = PYPROJECT if name == "pyproject.toml" else None
            for number, line in enumerate(body.splitlines(), 1):
                if any(rule.search(line) for rule in OUTSIDE) or (pattern and pattern.search(line)):
                    found.append(f"{path}:{number}: {line.strip()}")
    assert found == []


def test_no_link_into_either_repository_is_at_main() -> None:
    found = []
    for path in tracked():
        body = text(path)
        if body is None or path == HERE:
            continue
        found += [f"{path}: {hit.group(0)}" for hit in AT_MAIN.finditer(body)]
    assert found == []


def test_each_copy_names_its_source() -> None:
    for path, source in COPIES.items():
        body = (ROOT / path).read_text()
        if path.endswith(".py"):
            first = body.removeprefix('"""').splitlines()[0]
        else:
            first = next(line for line in body.splitlines() if line.startswith("#"))
        assert source in first, path
        assert SOURCE_COMMIT in first, path
