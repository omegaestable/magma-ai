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
