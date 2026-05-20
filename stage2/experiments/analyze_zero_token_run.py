#!/usr/bin/env python3
"""Analyze one zero-token Marathon run directory.

The vendored Marathon runner writes `answers.jsonl`, `summary.json`, and
`run.log`. This helper joins those artifacts back to the input manifest and
emits small ledgers that are easier to feed into Teorth/proof-mining tools.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_problem_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] == "[":
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [row for row in payload if isinstance(row, dict)]
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def load_answers(path: Path) -> dict[str, dict[str, Any]]:
    answers: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return answers
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            answers[row["id"]] = row
    return answers


def manifest_from_launcher(run_dir: Path) -> Path:
    command_path = run_dir / "launcher-command.json"
    if not command_path.exists():
        return manifest_from_run_log(run_dir)
    command = load_json(command_path).get("command", [])
    if not isinstance(command, list) or "--manifest" not in command:
        raise ValueError(f"Cannot find --manifest in {command_path}")
    idx = command.index("--manifest")
    return Path(command[idx + 1])


def manifest_from_run_log(run_dir: Path) -> Path:
    log_path = run_dir / "run.log"
    if not log_path.exists():
        raise FileNotFoundError(f"Missing {run_dir / 'launcher-command.json'} and {log_path}")
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.search(r"\bmanifest=([^\s]+)", line)
        if not match:
            continue
        raw = Path(match.group(1))
        candidates = [raw, REPO_ROOT / raw, run_dir.parent / raw]
        candidates.extend((REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems").glob(f"**/{raw.name}"))
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
    raise ValueError(f"Cannot recover manifest path from {log_path}")


def route_counts_from_log(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    route_counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        marker = "[marathon:stderr] "
        if marker not in line:
            continue
        payload = line.split(marker, 1)[1].strip()
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            continue
        routes = obj.get("routes")
        if isinstance(routes, dict):
            for route, count in routes.items():
                if isinstance(route, str) and isinstance(count, int):
                    route_counts[route] += count
    return dict(route_counts)


def gap_kind(problem: dict[str, Any], status: str) -> str:
    expected = problem.get("answer")
    if status != "not_attempted":
        return f"judge_{status}"
    if expected is True:
        return "true_template_gap"
    if expected is False:
        return "finite_countermodel_gap"
    pid = str(problem.get("id", ""))
    if pid.startswith("true_"):
        return "true_template_gap"
    if pid.startswith("false_"):
        return "finite_countermodel_gap"
    return "unknown_label_gap"


def answer_kind(answer: dict[str, Any]) -> str:
    verdict = answer.get("verdict")
    code = str(answer.get("code", ""))
    if verdict == "true":
        if "grind" in code:
            return "true:grind"
        return "true:certificate"
    if verdict == "false":
        return "false:finite"
    return "unknown:answer"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def analyze(run_dir: Path, manifest_override: Path | None = None) -> dict[str, Any]:
    manifest = manifest_override.resolve() if manifest_override is not None else manifest_from_launcher(run_dir)
    problems = load_problem_rows(manifest)
    by_id = {str(row.get("id")): row for row in problems}
    summary = load_json(run_dir / "summary.json")
    answers = load_answers(run_dir / "answers.jsonl")
    status_rows = summary.get("per_problem", [])

    accepted: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    gap_counts: Counter[str] = Counter()
    verdict_counts: Counter[str] = Counter()
    answer_status_counts: dict[str, Counter[str]] = {}
    for item in status_rows:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("id"))
        problem = by_id.get(pid, {"id": pid})
        status = str(item.get("status"))
        verdict = item.get("verdict")
        row = {
            "id": pid,
            "status": status,
            "verdict": verdict,
            "expected": problem.get("answer"),
            "answer": problem.get("answer"),
            "eq1_id": problem.get("eq1_id"),
            "eq2_id": problem.get("eq2_id"),
            "equation1": problem.get("equation1"),
            "equation2": problem.get("equation2"),
        }
        if status == "accepted":
            verdict_counts[str(verdict)] += 1
            answer = answers.get(pid)
            if answer is not None:
                row["code_bytes"] = len(str(answer.get("code", "")).encode("utf-8"))
                row["answer_kind"] = answer_kind(answer)
            accepted.append(row)
        else:
            kind = gap_kind(problem, status)
            row["gap_kind"] = kind
            gap_counts[kind] += 1
            answer = answers.get(pid)
            if answer is not None:
                row["answer_kind"] = answer_kind(answer)
            gaps.append(row)

        answer = answers.get(pid)
        if answer is not None:
            kind = answer_kind(answer)
            answer_status_counts.setdefault(kind, Counter())[status] += 1

    route_counts = route_counts_from_log(run_dir / "run.log")
    analysis = {
        "run_dir": str(run_dir.relative_to(REPO_ROOT)),
        "manifest": str(manifest.relative_to(REPO_ROOT)) if manifest.is_relative_to(REPO_ROOT) else str(manifest),
        "score": summary.get("score"),
        "attempted": summary.get("attempted"),
        "not_attempted": summary.get("not_attempted"),
        "by_status": summary.get("by_status", {}),
        "accepted_verdicts": dict(verdict_counts),
        "gap_counts": dict(gap_counts),
        "route_counts": route_counts,
        "answer_status_counts": {
            kind: dict(counts) for kind, counts in sorted(answer_status_counts.items())
        },
        "tokens_used": summary.get("tokens_used"),
        "wall_seconds": summary.get("wall_seconds"),
    }
    (run_dir / "analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(run_dir / "accepted.jsonl", accepted)
    write_jsonl(run_dir / "gaps.jsonl", gaps)
    return analysis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    args = parser.parse_args()

    for run_dir in args.run_dirs:
        analysis = analyze(run_dir.resolve(), args.manifest)
        print(
            f"{analysis['run_dir']}: score={analysis['score']} "
            f"gaps={analysis['gap_counts']} routes={len(analysis['route_counts'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
