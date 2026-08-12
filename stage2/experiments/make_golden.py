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

# Mirror test_golden.route_family: collapse timing-variant suffixes so each
# wall-clock-budgeted engine is grouped as one family. Selection picks the
# FASTEST rows per family, which keeps every engine covered while dropping
# budget-marginal singletons (e.g. a lone `true:lemma_chain:enum319` row that
# solved at its 10 s ceiling in one lucky audit and then skips under gate
# load). Route labels within a family are timing-dependent (which library
# index or witness matched first), so pinning the marginal one is what made
# the pre-package gate flaky (2026-07-23).
# Audit seconds above which a row is not golden material. See the filter below.
GOLDEN_MAX_SECONDS = 10.0

_GENERAL_CLOSURE_FAMILIES = {
    "true:absorption_closure",
    "true:equational_closure",
    "true:derived_cp_closure",
}


def _route_family(route: str) -> str:
    family = ":".join(route.split(":")[:2])
    if family in _GENERAL_CLOSURE_FAMILIES:
        return "true:general_closure"
    return family


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
                # narrow_grind is a last-ditch speculative lane: its certs are
                # model-check-only locally and the cloud judge rejected one in
                # the field (2026-07-22 session 4), and the budgeted lemma
                # routes ahead of it win its rows nondeterministically. Not
                # golden material on either count.
                if row["route"].startswith("true:narrow_grind"):
                    continue
                # egg_closure is the last TRUE engine and wall-clock budgeted,
                # so an egg-only row can time out under CPU load and read as a
                # coverage regression (nothing else can pick it up — egg is
                # last). Its certs are kernel-verified in every audit and
                # spotcheck run, so it needs no golden coverage; keeping it out
                # avoids a flaky pre-package gate (2026-07-23).
                if row["route"].startswith("true:egg_closure"):
                    continue
                # Same reasoning for the other two engines that sit at the very
                # end of the pipeline behind a large wall-clock budget: measured
                # 2026-07-29, `egg_collapse` rows take 41-85 s to re-solve at
                # `fast` and `egg_bootstrap` 5-20 s, both budget-marginal. Pinning
                # them would add minutes to the gate and make it flake on load,
                # which is how a gate ends up routinely skipped. Their
                # certificates are kernel-checked (the `lemma` shape) in every
                # audit and spotcheck run, and 10 of them are judge-verified.
                # `egg_ladder` joins them for the same reason and more strongly:
                # it is the very last kernel-verifiable engine, it re-solves in
                # 4-27 s at `fast`, and it spends part of that budget scanning
                # the lemma library for a rung — so which rung it finds, and
                # therefore which pivot closes the row, is wall-clock dependent.
                if row["route"].startswith(("true:egg_collapse",
                                            "true:egg_bootstrap",
                                            "true:egg_ladder")):
                    continue
                # A row that took real time in the audit is budget-marginal by
                # definition, whatever route claimed it, and the audit's own
                # `seconds` predicts the gate almost exactly — measured
                # 2026-08-11 on `evaluation_order5_0065`: 170.3 s audited,
                # 170.7 s in the gate. Pinning those is how a 22 s gate became a
                # 208 s one, and a slow gate is a gate people `-SkipTests`.
                #
                # This started life as a `false:constraint_fin`-only rule. It
                # should never have been route-specific: what makes a row unfit
                # for the gate is its cost, and the routes that run *after* the
                # TRUE engines (`local_model`, the wide constraint tier) now pay
                # for `egg_ladder` too, so more of them cross the line. Families
                # whose cheapest instance is over the line simply go unpinned;
                # their certificates are still kernel-checked in every audit and
                # spotcheck run, which is the same argument the egg exclusions
                # above rest on.
                if row.get("seconds", 0) > GOLDEN_MAX_SECONDS:
                    continue
                by_route[_route_family(row["route"])].append(row)

    entries = []
    for route in sorted(by_route):
        # Prefer the cheapest rows so the gate stays fast AND reproducible:
        # the fastest row in a family has the most budget headroom, so it
        # re-solves reliably under the loaded single-process gate. Dedupe by
        # id in case the same row appears in multiple audit reports.
        rows = sorted(by_route[route], key=lambda r: r.get("seconds", 99))
        seen_ids: set[str] = set()
        picked = 0
        for row in rows:
            if picked >= args.per_route:
                break
            if row["id"] in seen_ids:
                continue
            seen_ids.add(row["id"])
            picked += 1
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
