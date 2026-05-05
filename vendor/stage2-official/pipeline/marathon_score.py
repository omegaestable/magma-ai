"""
Marathon-mode scoring: read solver output JSONL, run ``verify_answer`` on
each entry, emit a summary.

Rules from ``docs/marathon_mode.md``:

* Multiple lines for the same id → last one wins.
* Missing id (in manifest but not in output) → ``not_attempted`` in the
  summary; counts toward neither ``accepted`` nor ``incorrect``.
* Score = number of ``accepted`` verdicts.
* Tiebreak: lower wall-clock used (the runner provides this; we just record).

This module does not run the solver. It is invoked after
``pipeline/marathon_runner.py`` has produced an output file (whether the
solver finished cleanly or was killed at the budget).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from judge.verify import (  # noqa: E402
    JudgeConfig,
    JudgeConfigurationError,
    JudgeInfrastructureError,
    verify_answer,
)


# Public five-status set from CLAUDE.md.
PUBLIC_STATUSES = (
    "accepted", "unparsed", "malformed", "incomplete_proof", "incorrect",
)


@dataclass
class PerProblemResult:
    id: str
    status: str  # one of PUBLIC_STATUSES, "not_attempted", or "harness_error"
    verdict: str | None = None
    message: str = ""


@dataclass
class MarathonSummary:
    score: int = 0
    attempted: int = 0
    not_attempted: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    per_problem: list[PerProblemResult] = field(default_factory=list)
    wall_seconds: float | None = None
    sigterm_fired: bool = False
    sigkill_fired: bool = False
    tokens_used: int | None = None
    tokens_exhausted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "attempted": self.attempted,
            "not_attempted": self.not_attempted,
            "by_status": dict(self.by_status),
            "wall_seconds": self.wall_seconds,
            "sigterm_fired": self.sigterm_fired,
            "sigkill_fired": self.sigkill_fired,
            "tokens_used": self.tokens_used,
            "tokens_exhausted": self.tokens_exhausted,
            "per_problem": [
                {
                    "id": r.id,
                    "status": r.status,
                    "verdict": r.verdict,
                    "message": r.message,
                }
                for r in self.per_problem
            ],
        }


def _load_manifest(manifest_path: Path) -> list[dict]:
    """Same loader semantics as ``pipeline.proxy.load_problems`` but here we
    only need the small slice used at scoring; keep this self-contained so
    score-only invocations don't import the proxy chain."""
    text = manifest_path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] == "[":
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError(f"{manifest_path}: top-level JSON must be a list")
        return data
    out: list[dict] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{manifest_path}:{lineno}: invalid JSONL ({exc})"
            ) from exc
        if not isinstance(obj, dict) or "id" not in obj:
            raise ValueError(
                f"{manifest_path}:{lineno}: expected problem dict with 'id'"
            )
        out.append(obj)
    return out


def _load_last_writes(output_path: Path) -> dict[str, dict]:
    """Read the solver's append-only JSONL output; last-write-wins per id.

    Malformed lines are skipped silently — they're equivalent to
    ``not_attempted`` for that id (the solver wrote garbage but never
    succeeded). The summary will report whatever the *next* well-formed line
    for that id said, or ``not_attempted`` if none.
    """
    last: dict[str, dict] = {}
    if not output_path.exists():
        return last
    text = output_path.read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        pid = obj.get("id")
        if not isinstance(pid, str):
            continue
        last[pid] = obj
    return last


def _to_judge_problem(problem: dict) -> dict:
    """Same shape as ``pipeline.proxy._to_judge_problem`` — we duplicate
    here so the score module is independent of the proxy import chain."""
    from pipeline.proxy import DEFAULT_PROOF_POLICY  # local to avoid OpenAI dep at import time
    return {
        "id": problem["id"],
        "eq1_id": problem["eq1_id"],
        "eq2_id": problem["eq2_id"],
        "equation1": problem["equation1"],
        "equation2": problem["equation2"],
        "proof_policy": problem.get("proof_policy") or DEFAULT_PROOF_POLICY,
    }


def _grade_one(
    problem: dict,
    submission: dict,
    judge_config: JudgeConfig | None,
) -> PerProblemResult:
    pid = problem["id"]
    verdict = submission.get("verdict")
    code = submission.get("code")
    if not isinstance(verdict, str) or not isinstance(code, str):
        return PerProblemResult(
            id=pid, status="malformed", verdict=verdict if isinstance(verdict, str) else None,
            message="solver output line missing 'verdict' or 'code' string fields",
        )
    raw_answer = json.dumps({"verdict": verdict, "code": code})
    judge_problem = _to_judge_problem(problem)
    try:
        result = verify_answer(judge_problem, raw_answer, config=judge_config)
    except JudgeInfrastructureError as exc:
        return PerProblemResult(
            id=pid, status="harness_error", verdict=verdict,
            message=f"judge infrastructure error: {exc}",
        )
    except JudgeConfigurationError as exc:
        return PerProblemResult(
            id=pid, status="harness_error", verdict=verdict,
            message=f"judge configuration error: {exc}",
        )
    status = result.get("status", "harness_error")
    msg = result.get("message", "") or result.get("stderr", "")
    return PerProblemResult(
        id=pid, status=status, verdict=verdict, message=str(msg)[:1000],
    )


def score_marathon(
    *,
    manifest_path: str | Path | None = None,
    output_path: str | Path,
    judge_config: JudgeConfig | None = None,
    wall_seconds: float | None = None,
    sigterm_fired: bool = False,
    sigkill_fired: bool = False,
    tokens_used: int | None = None,
    tokens_exhausted: bool = False,
    manifest_problems: tuple[dict, ...] | list[dict] | None = None,
    log_stream=None,
) -> MarathonSummary:
    """Read manifest + solver output, grade each id, return summary.

    Pass ``manifest_problems`` (the snapshot the runner read before launching
    the solver) to bypass the on-disk manifest entirely — that's the
    tamper-resistant scoring path. ``manifest_path`` remains supported for
    score-only invocations or external tooling, but the runner-fed snapshot
    takes precedence when both are supplied.
    """
    output_path = Path(output_path)
    if manifest_problems is not None:
        problems = list(manifest_problems)
    elif manifest_path is not None:
        problems = _load_manifest(Path(manifest_path))
    else:
        raise ValueError(
            "score_marathon: must supply either manifest_problems or manifest_path"
        )
    last_writes = _load_last_writes(output_path)

    summary = MarathonSummary(
        wall_seconds=wall_seconds,
        sigterm_fired=sigterm_fired,
        sigkill_fired=sigkill_fired,
        tokens_used=tokens_used,
        tokens_exhausted=tokens_exhausted,
    )

    for prob in problems:
        pid = prob["id"]
        sub = last_writes.get(pid)
        if sub is None:
            summary.per_problem.append(
                PerProblemResult(id=pid, status="not_attempted")
            )
            summary.not_attempted += 1
            summary.by_status["not_attempted"] = (
                summary.by_status.get("not_attempted", 0) + 1
            )
            continue
        summary.attempted += 1
        per = _grade_one(prob, sub, judge_config)
        summary.per_problem.append(per)
        summary.by_status[per.status] = summary.by_status.get(per.status, 0) + 1
        if per.status == "accepted":
            summary.score += 1
        if log_stream is not None:
            tag = per.status.upper()
            print(
                f"[score] {pid}: {tag}"
                + (f" — {per.message[:120]}" if per.message and per.status != "accepted" else ""),
                file=log_stream, flush=True,
            )

    if log_stream is not None:
        print(
            f"[score] score={summary.score}/{len(problems)} "
            f"attempted={summary.attempted} not_attempted={summary.not_attempted} "
            f"by_status={dict(summary.by_status)}",
            file=log_stream, flush=True,
        )
    return summary
