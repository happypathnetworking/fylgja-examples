"""The wheel check's parts that need no network: what it holds each change source never to load is the example's own
import scan's `CROSSED`, and the three distributions it installs beside the example's wheel are fylgja-core,
fylgja-infrahub and fylgja-netbox at `VERSION`, from the index, never built here. The check itself builds and
installs, and runs as `make wheelcheck`."""

from __future__ import annotations

import ast
import importlib.util
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "wheelcheck.py"
VERSION = (ROOT / "VERSION").read_text().strip()


@cache
def _script() -> ModuleType:
    """`scripts/wheelcheck.py`, loaded by path."""
    spec = importlib.util.spec_from_file_location("script_wheelcheck", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assigned(path: Path, name: str) -> tuple[object, ...]:
    """The tuple the file at `path` assigns to `name`, read by `ast`."""
    assigned = [
        statement.value
        for statement in ast.parse(path.read_text(), str(path)).body
        if isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in statement.targets)
    ]
    assert len(assigned) == 1, f"{path} assigns {name} once"
    held = ast.literal_eval(assigned[0])
    assert isinstance(held, tuple)
    return held


def test_what_each_change_source_never_loads_is_the_example_scans() -> None:
    """Importing the Infrahub change source loads nothing of the NetBox one or its reader, and the reverse."""
    held = _assigned(SCRIPT, "CROSSED")
    assert held == _assigned(ROOT / "orchestrator" / "tests" / "test_boundary_edge.py", "CROSSED")
    assert sorted(str(pair[0]) for pair in held if isinstance(pair, tuple)) == ["infrahub", "netbox"]


def test_the_check_installs_the_three_at_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The install's arguments, faked: the three distributions pinned at `VERSION`, from the index, no directory of
    wheels, no constraints and no pre-release flag."""
    module = _script()
    ran: list[list[str]] = []
    monkeypatch.setattr(module, "uv", lambda: "/opt/uv")
    monkeypatch.setattr(module, "run", lambda argv, cwd, env=None: ran.append(argv))
    env = tmp_path / "orchestrator" / "venv" / "bin"
    module.install_pinned(env, str(tmp_path / "example.whl"))
    assert len(ran) == 1
    argv = ran[0]
    assert argv[:3] == ["/opt/uv", "pip", "install"]
    assert argv[argv.index("--python") + 1] == str(env / "python")
    assert argv[argv.index("--python") + 2 :] == [
        f"fylgja-core=={VERSION}",
        f"fylgja-infrahub=={VERSION}",
        f"fylgja-netbox=={VERSION}",
        str(tmp_path / "example.whl"),
    ]
    assert not {"--no-index", "--find-links", "--constraints", "--prerelease"} & set(argv)


def test_the_check_installs_by_install_pinned_and_not_a_bare_install() -> None:
    """`check_orchestrator` calls `install_pinned` once and `install` never, so the pins cannot be dropped from it."""
    tree = ast.parse(SCRIPT.read_text(), str(SCRIPT))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "check_orchestrator")
    called = [
        node.func.id
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert called.count("install_pinned") == 1
    assert "install" not in called
