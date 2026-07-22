"""Regenerate the golden-route fixture from a corpus audit report.

Picks a route-diverse, self-contained sample: up to N problems per distinct
route, so the fast merge gate exercises every live route rather than just the
common ones. Problems are inlined into the fixture, so the gate needs no
dataset files and stays fast.

Usage:
    python stage2/experiments/audit_corpus.py --all --out stage2/results/audit.json
    python stage2/experiments/make_golden.py --audit stage2/results/audit.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

from audit_corpus import HF_SETS, SETS, load_problems  # noqa: E402

GOLDEN_PATH = REPO_ROOT / "stage2" / "tests" / "golden_routes.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, nargs="+", required=True,
                    help="one or more audit reports; routes are merged")
    ap.add_argument("--per-route", type=int, default=2)
    ap.add_argument("--out", type=Path, default=GOLDEN_PATH)
    args = ap.parse_args()

    reports = [json.loads(p.read_text(encoding="utf-8")) for p in args.audit]
    seen_sets = {s for r in reports for s in r.get("sets", {})}

    problems_by_id: dict[str, dict] = {}
    for set_name, path in {**SETS, **HF_SETS}.items():
        if set_name in seen_sets and path.exists():
            for problem in load_problems(path):
                problems_by_id[str(problem.get("id"))] = problem

    by_route: dict[str, list[dict]] = defaultdict(list)
    for report in reports:
        for set_name, payload in report["sets"].items():
            for row in payload["rows"]:
                if row.get("status") != "solved" or row.get("oracle") != "ok":
                    continue
                by_route[row["route"]].append(row)

    entries = []
    for route in sorted(by_route):
        # Prefer the cheapest rows so the gate stays fast.
        rows = sorted(by_route[route], key=lambda r: r.get("seconds", 99))
        for row in rows[: args.per_route]:
            problem = problems_by_id.get(row["id"])
            if problem is None:
                continue
            entries.append({
                "id": row["id"],
                "problem": {
                    "id": problem.get("id"),
                    "eq1_id": problem.get("eq1_id"),
                    "eq2_id": problem.get("eq2_id"),
                    "equation1": problem.get("equation1"),
                    "equation2": problem.get("equation2"),
                },
                "verdict": row["verdict"],
                "route": row["route"],
                "cert_shape": row.get("cert_shape"),
            })

    payload = {
        "note": "Golden route fixture. Regenerate with make_golden.py after an "
                "intentional route change; never edit by hand.",
        "sources": sorted(seen_sets),
        "routes": len(by_route),
        "entries": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.out}: {len(entries)} entries across {len(by_route)} routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
