"""Shared test fixtures: import the solver module by path.

The solver is a single file (competition contract), not a package, so tests
load it via sys.path. Everything in stage2/tests is repo-side tooling and is
never packaged into the submission artifact.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLVER_DIR = REPO_ROOT / "stage2" / "solver"
PROBLEMS_DIR = REPO_ROOT / "data" / "stage2_official_problems"

if str(SOLVER_DIR) not in sys.path:
    sys.path.insert(0, str(SOLVER_DIR))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture(scope="session")
def solver():
    import solver as solver_module

    return solver_module


@pytest.fixture(scope="session")
def problems_dir() -> Path:
    return PROBLEMS_DIR


@pytest.fixture(scope="session")
def problems_by_id() -> dict:
    """Every local benchmark problem keyed by id (official sets, then HF).

    Official sets win on collision: `sample_20` / `sample_200` are subsets of
    `normal` and carry the same ids.
    """
    import json

    HF_DIR = REPO_ROOT / "data" / "hf_cache"
    out: dict = {}

    def add(path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
                if path.suffix == ".jsonl" else json.loads(text))
        for problem in rows:
            out.setdefault(str(problem.get("id", "")), problem)

    for name in ("normal.jsonl", "hard1.jsonl", "hard2.jsonl", "hard3.jsonl",
                 "sample_200.json", "sample_20.json"):
        path = PROBLEMS_DIR / name
        if path.exists():
            add(path)
    if HF_DIR.exists():
        for path in sorted(HF_DIR.glob("evaluation_*.jsonl")):
            add(path)
    return out
