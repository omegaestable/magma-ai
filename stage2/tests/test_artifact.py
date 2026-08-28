"""The gate reads the source solver; the sandbox imports the *artifact*.

Everything else in `stage2/tests` loads `stage2/solver/solver.py` (529 KB of
source, comments included). What the graders run is the minified build - and the
minifier has already been caught once rewriting the contents of triple-quoted
literals, which is exactly where `DISTILLED_CERTS` lives. This file builds the
artifact the way the packager does and checks the properties whose failure is
silent and total:

* over 500,000 bytes -> the submission is refused outright;
* Python 3.12+ syntax -> the file does not import in `python:3.11-slim` and
  every problem is lost;
* a `PROMPT` the official AST extractor cannot read -> `pipeline/proxy.py`
  returns "" and the Solo LLM lane runs on an empty prompt with no error
  anywhere;
* anything besides `solver.py` in the submission directory -> the organizer's
  own `_validate_submission_layout` rejects the run before the first problem.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_primitives import _pep701_offenders

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLVER_SOURCE = REPO_ROOT / "stage2" / "solver" / "solver.py"
MINIFIER = REPO_ROOT / "stage2" / "solver" / "minify_submission.py"
VENDOR = REPO_ROOT / "vendor" / "stage2-official"
PY311 = Path("C:/Users/nacho/Documents/GitHub/magma-ai/.venv311/Scripts/python.exe")

MAX_SOLVER_BYTES = 500_000

# The placeholders the Solo lane's prompt must still carry after minification.
REQUIRED_PLACEHOLDERS = (
    "{problem.equation1}", "{problem.equation2}",
    "{solver.analysis}", "{solver.feedback}", "{history.attempts}",
)


@pytest.fixture(scope="module")
def artifact(tmp_path_factory) -> Path:
    """Build the submission the way `package_solver.ps1` does."""
    out_dir = tmp_path_factory.mktemp("submission")
    destination = out_dir / "solver.py"
    result = subprocess.run(
        [sys.executable, str(MINIFIER), str(SOLVER_SOURCE), str(destination)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
    assert result.returncode == 0, (
        f"minify_submission.py failed: {result.stdout}\n{result.stderr}")
    assert destination.exists()
    return destination


def _proxy_module():
    """Import the organizer's own proxy, so the checks are theirs, not ours."""
    if not (VENDOR / "pipeline" / "proxy.py").exists():
        pytest.skip(f"vendored harness not present at {VENDOR}")
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))
    try:
        from pipeline import proxy  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"pipeline.proxy is not importable here: {exc}")
    return proxy


def test_packed_tables_round_trip_to_the_source_literals(artifact):
    """The minifier packs `DISTILLED_CERTS` and the witness tables into
    zlib+base85 blobs (2026-08-28, ~96 KB saved). The packer's own check
    already compares the decoded blob to the source literal; this repeats it
    from the *shipped file*, through the same `_unpack_table` the sandbox will
    run, so a helper or blob edited by hand after packaging cannot pass."""
    import importlib.util  # noqa: PLC0415

    import solver  # noqa: PLC0415

    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("packed_solver_under_test", artifact)
    packed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packed)
    for name in ("DISTILLED_CERTS", "FP_WITNESS_TABLES", "O5_WITNESS_TABLES",
                 "WITNESS_TABLES"):
        want, got = getattr(solver, name), getattr(packed, name)
        assert type(got) is type(want), name
        assert got == want, f"{name} in the artifact differs from the source"
    assert all(type(k) is tuple and type(v) is tuple
               for k, v in packed.DISTILLED_CERTS.items())
    assert all(type(entry) is tuple and type(entry[1]) is list
               for entry in packed.FP_WITNESS_TABLES + packed.O5_WITNESS_TABLES
               + packed.WITNESS_TABLES)
    # Non-vacuity: the artifact really is packed, not a copy of the source.
    text = artifact.read_text(encoding="utf-8")
    assert "_unpack_table(" in text
    assert "DISTILLED_CERTS: dict" not in text


def test_artifact_is_under_the_judges_byte_cap(artifact):
    size = artifact.stat().st_size
    assert size < MAX_SOLVER_BYTES, (
        f"artifact is {size} bytes against a {MAX_SOLVER_BYTES} cap")


def test_artifact_parses(artifact):
    ast.parse(artifact.read_text(encoding="utf-8"))


def test_artifact_uses_no_syntax_newer_than_the_sandbox_interpreter(artifact):
    """The source is checked by test_primitives; this is the shipped text."""
    offenders = _pep701_offenders(artifact.read_text(encoding="utf-8"))
    assert not offenders, (
        f"the built artifact uses Python 3.12+ f-string syntax at {offenders[:5]}")


def test_the_official_extractor_still_finds_a_usable_prompt(artifact):
    """`proxy._extract_prompt_from_solver` accepts only a top-level
    `PROMPT = <str constant>`; a minifier that folded or concatenated it would
    empty the Solo LLM lane silently."""
    proxy = _proxy_module()
    prompt = proxy._extract_prompt_from_solver(artifact)
    assert len(prompt) > 1000, f"extracted prompt is {len(prompt)} chars"
    for placeholder in REQUIRED_PLACEHOLDERS:
        assert placeholder in prompt, f"{placeholder} vanished from the prompt"


def test_a_lone_solver_py_is_a_valid_submission_layout(artifact, tmp_path):
    """RC-01: the run is refused wholesale over one stray `__pycache__`."""
    proxy = _proxy_module()
    staged = tmp_path / "submission"
    staged.mkdir()
    shutil.copy2(artifact, staged / "solver.py")
    assert proxy._validate_submission_layout(staged) is None

    # Non-vacuity: the validator must actually reject the thing it is here for.
    (staged / "__pycache__").mkdir()
    assert proxy._validate_submission_layout(staged) is not None


@pytest.mark.skipif(
    not PY311.exists(),
    reason=(f"no 3.11 interpreter at {PY311} - the sandbox is python:3.11-slim, "
            "so this check is the local half of CI's; rail 16: a skip here is a "
            "gap in coverage, not coverage"))
def test_artifact_imports_under_the_sandbox_interpreter(artifact):
    result = subprocess.run(
        [str(PY311), "-c", "import solver; print(solver.__name__)"],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(artifact.parent),
        env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
    assert result.returncode == 0, (
        f"the artifact does not import on 3.11:\n{result.stdout}\n{result.stderr}")
