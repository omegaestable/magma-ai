from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from judge.verify import JudgeConfig, verify_answer, _resolve_config

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "tests" / "challenger_manifest.json"
DEFAULT_ARTIFACT_DIR = REPO_ROOT / ".artifacts" / "challenger"


def _stable_projection(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "error_code": result["error_code"],
        "message": result["message"],
        "verdict": result.get("verdict"),
        "direct_declarations": result.get("direct_declarations", []),
        "axioms": result.get("axioms", []),
    }


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _run_public_attack(case: dict[str, Any], config: JudgeConfig) -> dict[str, Any]:
    problem = json.loads((REPO_ROOT / case["problem_path"]).read_text(encoding="utf-8"))
    raw_answer = (REPO_ROOT / case["answer_path"]).read_text(encoding="utf-8")
    result = verify_answer(problem, raw_answer, config=config)
    ok = result["status"] == case["expected_status"]
    if "expected_error_code" in case:
        ok = ok and result["error_code"] == case["expected_error_code"]
    return {
        "name": case["name"],
        "kind": "public_attack",
        "ok": ok,
        "expected_status": case["expected_status"],
        "expected_error_code": case.get("expected_error_code"),
        "result": _stable_projection(result),
    }


def _run_false_negative_case(case: dict[str, Any], config: JudgeConfig) -> dict[str, Any]:
    """Snapshot a documented false-negative against its current known-bad status.

    These are proofs Lean accepts but the policy currently rejects (e.g., due to
    ``letFun`` or ``Trans.trans`` declaration leaks). We lock in today's
    ``current_status`` / ``current_error_code`` so any silent policy drift
    fails the harness. A flip to ``expected_status = accepted`` is surfaced as
    a failure too — that's the cue to retire the case rather than ignore it.
    """
    problem = json.loads((REPO_ROOT / case["problem_path"]).read_text(encoding="utf-8"))
    raw_answer = (REPO_ROOT / case["answer_path"]).read_text(encoding="utf-8")
    result = verify_answer(problem, raw_answer, config=config)
    current_status = case.get("current_status")
    current_error_code = case.get("current_error_code")
    status_match = result["status"] == current_status
    code_match = (
        current_error_code is None or result["error_code"] == current_error_code
    )
    ok = status_match and code_match
    return {
        "name": case["name"],
        "kind": "false_negative",
        "ok": ok,
        "expected_status": case.get("expected_status"),
        "current_status": current_status,
        "current_error_code": current_error_code,
        "result": _stable_projection(result),
    }


def _run_infra_attack(case: dict[str, Any], config: JudgeConfig) -> dict[str, Any]:
    problem = json.loads((REPO_ROOT / case["problem_path"]).read_text(encoding="utf-8"))
    raw_answer = (REPO_ROOT / case["answer_path"]).read_text(encoding="utf-8")
    expected_exception = case["expected_exception"]
    try:
        verify_answer(problem, raw_answer, config=config)
    except Exception as exc:  # noqa: BLE001
        ok = type(exc).__name__ == expected_exception
        return {
            "name": case["name"],
            "kind": "infra_attack",
            "ok": ok,
            "expected_exception": expected_exception,
            "raised_exception": type(exc).__name__,
            "message": str(exc),
        }

    return {
        "name": case["name"],
        "kind": "infra_attack",
        "ok": False,
        "expected_exception": expected_exception,
        "raised_exception": None,
        "message": "verify_answer returned a public verdict instead of failing closed",
    }


def run_challenger_suite(
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    env_config = _resolve_config(None)
    config = JudgeConfig(
        lake_bin=env_config.lake_bin,
        lean_bin=env_config.lean_bin,
        artifact_dir=artifact_dir,
        lean_timeout_seconds=env_config.lean_timeout_seconds,
    )

    public_results = [_run_public_attack(case, config) for case in manifest.get("public_attack_cases", [])]
    infra_results = [_run_infra_attack(case, config) for case in manifest.get("infra_attack_cases", [])]
    false_negative_results = [
        _run_false_negative_case(case, config)
        for case in manifest.get("false_negative_cases", [])
    ]

    failing_public = [case for case in public_results if not case["ok"]]
    failing_infra = [case for case in infra_results if not case["ok"]]
    failing_false_negative = [case for case in false_negative_results if not case["ok"]]
    return {
        "public_attack_count": len(public_results),
        "passed_public_attack_count": sum(1 for case in public_results if case["ok"]),
        "infra_attack_count": len(infra_results),
        "passed_infra_attack_count": sum(1 for case in infra_results if case["ok"]),
        "false_negative_count": len(false_negative_results),
        "passed_false_negative_count": sum(1 for case in false_negative_results if case["ok"]),
        "failing_public_attacks": failing_public,
        "failing_infra_attacks": failing_infra,
        "failing_false_negatives": failing_false_negative,
    }


__all__ = ["run_challenger_suite"]
