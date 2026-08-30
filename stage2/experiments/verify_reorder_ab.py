#!/usr/bin/env python3
"""DIAGNOSIS ONLY (2026-08-27). Oracle-verify a candidate route order.

Runs `solve_problem` from an alternate solver directory (MAGMA_SOLVER_DIR) over
a row file and applies the exact offline oracle battery `audit_corpus.py` uses,
so a proposed reorder can be checked for soundness as well as speed.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVER_DIR = os.environ.get("MAGMA_SOLVER_DIR") or str(REPO / "stage2" / "solver")
sys.path.insert(0, str(REPO / "stage2" / "tests"))

_S = None
_O = None


def _init():
    global _S, _O
    if SOLVER_DIR not in sys.path:
        sys.path.insert(0, SOLVER_DIR)
    import solver as S
    import oracles as O
    _S, _O = S, O


def _battery(eq1):
    S, O = _S, _O
    extras = [t for _n, t in S.WITNESS_TABLES]
    extras.extend(t for _r, t in S.structured_family_tables())
    extras.extend(t for _r, t in S.affine_family_tables(max_n=5))
    return O.model_battery(eq1, extras, fin3_samples=300, seed=17)


def _run(args):
    problem, effort, row_budget, false_budget = args
    S, O = _S, _O
    S.set_effort(effort)
    S.clear_term_caches()
    S.set_hard_deadline(time.monotonic() + row_budget if row_budget else None)
    row = {"id": str(problem.get("id", "")), "status": "skip"}
    t0 = time.monotonic()
    try:
        rec = S.solve_problem(problem, false_time_budget=false_budget)
    except Exception as exc:  # noqa: BLE001
        row.update(status="crash", error=f"{type(exc).__name__}: {exc}")
        return row
    row["seconds"] = round(time.monotonic() - t0, 3)
    if rec is None:
        return row
    ans = rec["answer"]
    verdict = ans["verdict"]
    code = ans["code"]
    row.update(status="solved", verdict=verdict, route=str(rec["route"]),
               code_bytes=len(code.encode("utf-8")))
    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    if isinstance(problem.get("answer"), bool):
        exp = "true" if problem["answer"] else "false"
        row["label"] = exp
        if exp != verdict:
            row["oracle"] = "VERDICT_CONTRADICTS_LABEL"
            return row
    checks = []
    try:
        O.check_no_banned_tactics(code, row["route"])
        checks.append("no_banned_tactics")
        if verdict == "false":
            O.check_false_certificate(code, eq1, eq2)
            checks.append("false_table_verified")
        else:
            shape = O.classify_true_certificate(code)
            row["cert_shape"] = shape
            if shape == "exact_expr":
                O.check_true_exact_certificate(code, eq1, eq2)
                checks.append("kernel")
            elif shape == "singleton":
                O.check_true_singleton_certificate(code, eq1)
                checks.append("kernel")
            elif shape == "lemma":
                O.check_true_lemma_certificate(code, eq1, eq2)
                checks.append("kernel")
            elif shape == "lemma_chain":
                O.check_true_lemma_chain_certificate(code, eq1, eq2)
                checks.append("kernel")
            else:
                checks.append("kernel_skipped_unsupported_shape")
            b = _battery(eq1)
            row["nontrivial_models"] = O.nontrivial_model_count(b)
            O.model_check_true(eq2, b)
            checks.append("model_checked" if row["nontrivial_models"] else "model_check_vacuous")
        row["oracle"] = "ok"
    except O.OracleError as exc:
        row.update(oracle="FAILED", oracle_error=str(exc))
    row["checks"] = checks
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--row-budget", type=float, default=0.0)
    ap.add_argument("--false-budget", type=float, default=2.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    rows = [json.loads(l) for l in Path(a.rows).read_text(encoding="utf-8").splitlines() if l.strip()]
    payload = [(r, a.effort, a.row_budget, a.false_budget) for r in rows]
    out = []
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init) as ex:
        for res in ex.map(_run, payload, chunksize=1):
            out.append(res)
    solved = [r for r in out if r["status"] == "solved"]
    bad = [r for r in out if r.get("oracle") not in (None, "ok")]
    print(f"solver_dir={SOLVER_DIR}")
    print(f"rows={len(out)} solved={len(solved)} skip={len(out)-len(solved)} "
          f"oracle_failures={len(bad)} seconds={sum(r.get('seconds',0) for r in out):.1f}")
    for r in bad[:10]:
        print("  BAD", r["id"], r.get("oracle"), r.get("oracle_error", "")[:160])
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
