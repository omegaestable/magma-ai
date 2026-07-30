#!/usr/bin/env python3
"""Analyze a dev_true_loop ledger.jsonl: cluster failures to drive solver work.

Adds signals the run summary lacks:
  * which round accepted wins land on (repair-loop value)
  * the model's verdict choice per round (true vs false on TRUE-only frontier)
  * Lean-error signatures (normalized first line) for the non-accepted rows
  * a coarse syntactic family of the goal equation (route-mining hint)

Dev-time only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVER_DIR = REPO / "stage2" / "solver"
sys.path.insert(0, str(SOLVER_DIR))
import solver as S  # noqa: E402


def lean_error_signature(err: str) -> str:
    if not err:
        return "(none)"
    # first non-empty line, path-stripped, digits/anon vars normalized
    for line in err.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"Submission\.lean:\d+:\d+", "Submission.lean:L:C", line)
        line = re.sub(r"\b\d+\b", "N", line)
        return line[:140]
    return "(none)"


def goal_family(problem: dict) -> str:
    try:
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
    except Exception:  # noqa: BLE001
        return "unparseable"
    feats = []
    lhs_is_var = eq2["lhs"][0] == "var"
    rhs_is_var = eq2["rhs"][0] == "var"
    if lhs_is_var or rhs_is_var:
        feats.append("goal_projection")  # one side a bare variable
    if S.term_vars(eq2["lhs"]) != S.term_vars(eq2["rhs"]):
        feats.append("goal_var_mismatch")
    if S.absorption_hypothesis(eq1):
        feats.append("absorption_hyp")
    nv = len(eq2["variables"])
    feats.append(f"goal_vars={nv}")
    depth = max(S.term_depth(eq2["lhs"]), S.term_depth(eq2["rhs"]))
    feats.append(f"goal_depth={depth}")
    return ",".join(feats)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--show", type=int, default=12, help="top-N per histogram")
    ap.add_argument("--dump-fails", default=None, help="write non-accepted rows (compact) here")
    args = ap.parse_args()

    rows = [json.loads(l) for l in Path(args.ledger).read_text(encoding="utf-8").splitlines() if l.strip()]
    n = len(rows)
    accepted = [r for r in rows if r.get("accepted")]
    failed = [r for r in rows if not r.get("accepted")]

    win_round = Counter()
    win_route = Counter()
    verdict_choice = Counter()  # per (parseable) round
    last_outcome = Counter()
    error_codes = Counter()
    lean_sigs = Counter()
    parse_reasons = Counter()
    fail_families = Counter()
    truncations = 0
    llm_errors = 0

    for r in rows:
        for rd in r.get("rounds", []):
            if rd.get("truncated"):
                truncations += 1
            if rd.get("llm_error"):
                llm_errors += 1
            if rd.get("verdict"):
                verdict_choice[rd["verdict"]] += 1
            if rd.get("outcome") == "parse_reject":
                parse_reasons[rd.get("parse_reason", "?")] += 1
        if r.get("accepted"):
            # find the accepting round
            for rd in r["rounds"]:
                if rd.get("outcome") == "accepted":
                    win_round[rd["round"]] += 1
            win_route[r.get("accepted_route", "?")] += 1
        else:
            fam = goal_family(r)
            fail_families[fam] += 1
            last = r["rounds"][-1] if r.get("rounds") else {}
            last_outcome[last.get("outcome", "none")] += 1
            if last.get("error_code"):
                error_codes[last["error_code"]] += 1
            if last.get("lean_error"):
                lean_sigs[lean_error_signature(last["lean_error"])] += 1

    def top(counter, k=args.show):
        return dict(counter.most_common(k))

    print(f"ledger: {args.ledger}")
    print(f"problems={n}  accepted={len(accepted)} ({len(accepted)/max(1,n):.0%})  failed={len(failed)}")
    print(f"llm_errors={llm_errors}  truncations={truncations}")
    print(f"\nmodel verdict choice (parseable rounds): {dict(verdict_choice)}")
    print(f"accepted win-round histogram: {dict(win_round)}")
    print(f"accepted by route: {top(win_route)}")
    print(f"\n[FAILED] last-round outcome: {top(last_outcome)}")
    print(f"[FAILED] judge error_codes: {top(error_codes)}")
    print(f"[FAILED] parse_reject reasons (all rounds): {top(parse_reasons)}")
    print("\n[FAILED] lean error signatures:")
    for sig, c in lean_sigs.most_common(args.show):
        print(f"  {c:4d}  {sig}")
    print("\n[FAILED] goal syntactic families:")
    for fam, c in fail_families.most_common(args.show):
        print(f"  {c:4d}  {fam}")

    if args.dump_fails:
        with Path(args.dump_fails).open("w", encoding="utf-8") as fh:
            for r in failed:
                last = r["rounds"][-1] if r.get("rounds") else {}
                fh.write(json.dumps({
                    "id": r["id"], "eq1_id": r.get("eq1_id"), "eq2_id": r.get("eq2_id"),
                    "equation1": r.get("equation1"), "equation2": r.get("equation2"),
                    "family": goal_family(r),
                    "last_outcome": last.get("outcome"),
                    "error_code": last.get("error_code"),
                    "lean_sig": lean_error_signature(last.get("lean_error", "")),
                }, ensure_ascii=False) + "\n")
        print(f"\nwrote failed rows -> {args.dump_fails}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
