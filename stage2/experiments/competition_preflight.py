#!/usr/bin/env python3
"""Competition-readiness preflight for the Stage 2 lab.

This is a lightweight repo-local diagnosis script. It does not mutate the
solver artifact; it inspects packaging, problem caches, active tool imports,
public result coverage, and the known Marathon budget-doc ambiguity.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE2_DIR = REPO_ROOT / "stage2"
RESULTS_DIR = STAGE2_DIR / "results"
SUBMISSION_DIR = STAGE2_DIR / "submissions"
HF_MANIFEST = REPO_ROOT / "data" / "hf_cache" / "manifest.json"
OFFICIAL_MANIFEST = REPO_ROOT / "data" / "stage2_official_problems" / "manifest.json"
OFFICIAL_PROBLEMS_DIR = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
MARATHON_DOC = REPO_ROOT / "vendor" / "stage2-official" / "docs" / "marathon_mode.md"
EVAL_RULES = REPO_ROOT / "vendor" / "stage2-official" / "rules" / "evaluation.md"
DEFAULT_SETS = ("normal", "hard1", "hard2", "hard3")
IMPORT_SMOKE = (
    REPO_ROOT / "theory" / "tools" / "atlas_public_dev.py",
    REPO_ROOT / "theory" / "tools" / "proof_atlas.py",
    REPO_ROOT / "theory" / "tools" / "proof_construction_atlas.py",
    REPO_ROOT / "theory" / "tools" / "smoke_problem_sets.py",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_path(path: Path) -> str | None:
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return None
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"


def problem_count(name: str) -> int:
    path = OFFICIAL_PROBLEMS_DIR / f"{name}.jsonl"
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def result_stats(date: str, name: str) -> dict[str, int]:
    path = RESULTS_DIR / f"{date}-{name}-finite-countermodels.json"
    if not path.exists():
        return {"exists": 0, "rows": 0, "solved": 0}
    rows = load_json(path)
    return {
        "exists": 1,
        "rows": len(rows),
        "solved": sum(1 for row in rows if row.get("solved")),
    }


def build_report(date: str) -> str:
    lines: list[str] = [
        "# Competition Preflight",
        "",
        f"Date: {date}",
        "",
        "## Packaging",
        "",
    ]

    if SUBMISSION_DIR.exists():
        entries = sorted(item.name for item in SUBMISSION_DIR.iterdir())
    else:
        entries = []
    solver_path = SUBMISSION_DIR / "solver.py"
    solver_size = solver_path.stat().st_size if solver_path.exists() else 0
    lines.append(f"- submission entries: {entries or ['<missing>']}")
    lines.append(f"- solver size bytes: {solver_size}")
    lines.append(f"- single-file layout ok: {entries == ['solver.py']}")
    lines.append("")

    lines.extend(
        [
            "## Data Caches",
            "",
            f"- hf manifest: {'present' if HF_MANIFEST.exists() else 'missing'}",
            f"- official stage2 mirror manifest: {'present' if OFFICIAL_MANIFEST.exists() else 'missing'}",
            "",
            "## Tool Imports",
            "",
        ]
    )
    for path in IMPORT_SMOKE:
        error = import_path(path)
        if error is None:
            lines.append(f"- `{path.name}`: ok")
        else:
            lines.append(f"- `{path.name}`: FAIL ({error})")

    lines.extend(["", "## Public Result Coverage", ""])
    for name in DEFAULT_SETS:
        stats = result_stats(date, name)
        lines.append(
            f"- `{name}`: problems={problem_count(name)}, result_rows={stats['rows']}, "
            f"solved={stats['solved']}, exists={bool(stats['exists'])}"
        )

    marathon_doc = MARATHON_DOC.read_text(encoding="utf-8") if MARATHON_DOC.exists() else ""
    eval_rules = EVAL_RULES.read_text(encoding="utf-8") if EVAL_RULES.exists() else ""
    lines.extend(
        [
            "",
            "## Marathon Budget Ambiguity",
            "",
            f"- docs/marathon_mode.md mentions `600 s/problem`: {'600 s' in marathon_doc}",
            f"- rules/evaluation.md mentions `3600 s/problem`: {'3600 s' in eval_rules}",
            "- local recommendation: parameterize preflight and long-run tests for both reference values",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-05-12")
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "2026-05-12-competition-preflight.md",
    )
    args = parser.parse_args()

    report = build_report(args.date)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
