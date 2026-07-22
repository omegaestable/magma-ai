"""Corpus audit: run the solver over public problem sets and verify every
emitted certificate offline (no Lean required).

Serves two jobs:

1. Soundness gate (WS0) - every TRUE certificate in the kernel-checkable shape
   is proof-checked; every FALSE certificate's witness table is independently
   re-verified; every TRUE verdict is model-checked against finite models of
   the hypothesis. Any failure is a latent `incorrect` submission.

2. Subsumption matrix (WS1) - with --subsumption, records for each solved row
   whether the general engines (equational closure / derived critical-pair
   closure) also solve it, so bespoke routes that are fully subsumed can be
   deleted with evidence.

Usage:
    python stage2/experiments/audit_corpus.py --set sample_20
    python stage2/experiments/audit_corpus.py --set normal --limit 200 --subsumption
    python stage2/experiments/audit_corpus.py --all --out stage2/results/audit.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402

PROBLEMS_DIR = REPO_ROOT / "data" / "stage2_official_problems"

SETS = {
    "sample_20": PROBLEMS_DIR / "sample_20.json",
    "sample_200": PROBLEMS_DIR / "sample_200.json",
    "normal": PROBLEMS_DIR / "normal.jsonl",
    "hard1": PROBLEMS_DIR / "hard1.jsonl",
    "hard2": PROBLEMS_DIR / "hard2.jsonl",
    "hard3": PROBLEMS_DIR / "hard3.jsonl",
}

# HF mirror evaluation sets. Deliberately excluded from headline public
# evidence (see CURRENT_STATE.md), but they cover a different slice of the
# law space and are the only local proxy for "a distribution we did not
# tune against" - which makes them essential for de-bloat decisions.
HF_SETS = {
    f"hf_{name}": REPO_ROOT / "data" / "hf_cache" / f"{name}.jsonl"
    for name in ("evaluation_normal", "evaluation_hard",
                 "evaluation_extra_hard", "evaluation_order5")
}


def load_problems(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def build_battery(eq1: dict) -> list[list[list[int]]]:
    extras = [table for _name, table in S.WITNESS_TABLES]
    extras.extend(table for _route, table in S.structured_family_tables())
    extras.extend(table for _route, table in S.affine_family_tables(max_n=5))
    return oracles.model_battery(eq1, extras, fin3_samples=300, seed=17)


def audit_row(problem: dict, *, subsumption: bool, false_budget: float,
              effort: str = "fast") -> dict:
    S.set_effort(effort)
    row: dict = {"id": str(problem.get("id", "")), "status": "skip"}
    started = time.monotonic()
    try:
        record = S.solve_problem(problem, false_time_budget=false_budget)
    except Exception as exc:  # noqa: BLE001
        row["status"] = "crash"
        row["error"] = f"{type(exc).__name__}: {exc}"
        return row
    row["seconds"] = round(time.monotonic() - started, 3)
    if record is None:
        return row

    answer = record["answer"]
    verdict = answer["verdict"]
    code = answer["code"]
    route = str(record["route"])
    row.update(status="solved", verdict=verdict, route=route,
               code_bytes=len(code.encode("utf-8")))

    try:
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError) as exc:
        row["oracle"] = "problem_parse_failed"
        row["oracle_error"] = str(exc)
        return row

    # Ground truth cross-check when the fixture carries a label.
    if isinstance(problem.get("answer"), bool):
        expected = "true" if problem["answer"] else "false"
        row["label"] = expected
        if expected != verdict:
            row["oracle"] = "VERDICT_CONTRADICTS_LABEL"
            return row

    checks: list[str] = []
    try:
        if verdict == "false":
            oracles.check_false_certificate(code, eq1, eq2)
            checks.append("false_table_verified")
        else:
            shape = oracles.classify_true_certificate(code)
            row["cert_shape"] = shape
            if shape == "exact_expr":
                oracles.check_true_exact_certificate(code, eq1, eq2)
                checks.append("proof_kernel_verified")
            elif shape == "singleton":
                oracles.check_true_singleton_certificate(code, eq1)
                checks.append("collapse_kernel_verified")
            else:
                checks.append("proof_kernel_skipped_unsupported_shape")
            battery = build_battery(eq1)
            row["battery"] = len(battery)
            oracles.model_check_true(eq2, battery)
            checks.append("model_checked")
        row["oracle"] = "ok"
        row["checks"] = checks
    except oracles.OracleError as exc:
        row["oracle"] = "FAILED"
        row["oracle_error"] = str(exc)
        row["checks"] = checks
        return row

    if subsumption and verdict == "true":
        row["subsumed_by"] = probe_general_engines(eq1, eq2)
    return row


def probe_general_engines(eq1: dict, eq2: dict) -> list[str]:
    """Which general engines also prove this row (for de-bloat evidence)."""
    hits: list[str] = []
    for name, fn in (
        ("equational_closure", S.equational_closure_route),
        ("derived_cp_closure", S.derived_cp_closure_route),
    ):
        try:
            if fn(eq1, eq2) is not None:
                hits.append(name)
        except Exception:  # noqa: BLE001
            pass
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="set_name",
                    choices=sorted({**SETS, **HF_SETS}), default="sample_20")
    ap.add_argument("--all", action="store_true", help="audit every public set")
    ap.add_argument("--hf", action="store_true",
                    help="audit the HF mirror evaluation sets instead")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--subsumption", action="store_true")
    ap.add_argument("--false-budget", type=float, default=2.0)
    ap.add_argument("--effort", choices=("fast", "standard", "deep"),
                    default="fast",
                    help="engine effort tier; Marathon/Solo pick this from "
                         "their real budget at runtime")
    ap.add_argument("--workers", type=int,
                    default=max(1, min(16, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    all_sets = {**SETS, **HF_SETS}
    if args.hf:
        set_names = sorted(HF_SETS)
    elif args.all:
        set_names = sorted(SETS)
    else:
        set_names = [args.set_name]
    report: dict = {"sets": {}}
    exit_code = 0

    for set_name in set_names:
        path = all_sets[set_name]
        if not path.exists():
            print(f"[skip] {set_name}: missing {path}")
            continue
        problems = load_problems(path)
        if args.limit:
            problems = problems[: args.limit]

        started = time.monotonic()
        worker = partial(audit_row, subsumption=args.subsumption,
                         false_budget=args.false_budget, effort=args.effort)
        if args.workers == 1:
            rows = []
            for i, problem in enumerate(problems, 1):
                rows.append(worker(problem))
                if i % 50 == 0:
                    print(f"  {set_name}: {i}/{len(problems)}"
                          f" ({time.monotonic() - started:.0f}s)", flush=True)
        else:
            print(f"  {set_name}: {len(problems)} problems on "
                  f"{args.workers} workers...", flush=True)
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                rows = list(pool.map(worker, problems, chunksize=4))
        elapsed = time.monotonic() - started

        solved = [r for r in rows if r["status"] == "solved"]
        failures = [r for r in solved if r.get("oracle") not in (None, "ok")]
        crashes = [r for r in rows if r["status"] == "crash"]
        summary = {
            "problems": len(rows),
            "solved": len(solved),
            "skipped": sum(1 for r in rows if r["status"] == "skip"),
            "crashes": len(crashes),
            "true": sum(1 for r in solved if r.get("verdict") == "true"),
            "false": sum(1 for r in solved if r.get("verdict") == "false"),
            "oracle_failures": len(failures),
            "seconds": round(elapsed, 1),
            "routes": dict(Counter(r["route"] for r in solved).most_common()),
            "cert_shapes": dict(Counter(
                r.get("cert_shape", "-") for r in solved
                if r.get("verdict") == "true")),
        }
        if args.subsumption:
            subsumed = Counter()
            for r in solved:
                if r.get("verdict") != "true":
                    continue
                for engine in r.get("subsumed_by", []):
                    subsumed[f"{r['route']}|{engine}"] += 1
            summary["subsumption"] = dict(subsumed.most_common())

        report["sets"][set_name] = {"summary": summary, "rows": rows}

        print(f"\n=== {set_name} ===")
        print(json.dumps({k: v for k, v in summary.items()
                          if k not in ("routes", "subsumption")}, indent=2))
        if failures or crashes:
            exit_code = 1
            for r in (failures + crashes)[:20]:
                print(f"  !! {r['id']} {r.get('route', '-')}: "
                      f"{r.get('oracle_error') or r.get('error')}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote {args.out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
