"""The example's three distributions are pinned at `VERSION` and the lock holds them at it, from PyPI alone.

The pins are exact because the tests reach past the promise: they read the core's fakes of a runtime and its
packages, which a release's compatibility statement does not cover (D-124 in fylgja-core). A pin moved without
`VERSION`, or `VERSION` moved without the pins and `uv lock`, fails here.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

REGISTRY = "https://pypi.org/simple"

ROOT = Path(__file__).resolve().parents[2]
VERSION = (ROOT / "VERSION").read_text().strip()
PINNED = ("fylgja-core", "fylgja-infrahub", "fylgja-netbox")
# The workspace's own member, whose source in the lock is its path.
MEMBER = "fylgja-orchestrator"


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "orchestrator" / "pyproject.toml").read_text())


def _lock_packages() -> list[dict[str, object]]:
    packages = tomllib.loads((ROOT / "uv.lock").read_text())["package"]
    assert isinstance(packages, list)
    return packages


def test_the_three_distributions_are_pinned_at_version() -> None:
    project = _pyproject()["project"]
    assert isinstance(project, dict)
    assert {*project["dependencies"]} >= {f"{name}=={VERSION}" for name in PINNED}
    assert project["optional-dependencies"]["dev"][0] == f"fylgja-core[server]=={VERSION}"


def test_the_lock_holds_version_of_each() -> None:
    held = {p["name"]: p["version"] for p in _lock_packages() if p["name"] in PINNED}
    assert held == dict.fromkeys(PINNED, VERSION)


def test_the_lock_is_pypis_alone() -> None:
    """Every package but the workspace member is from `REGISTRY` itself, not any registry. A candidate release's lock
    is from TestPyPI, so plan 3's candidate branch amends this test; `main` never does."""
    for package in _lock_packages():
        source = package["source"]
        assert isinstance(source, dict)
        if package["name"] == MEMBER:
            assert set(source) == {"editable"}
            continue
        assert source == {"registry": REGISTRY}, f"{package['name']} is not from {REGISTRY}: {source}"
