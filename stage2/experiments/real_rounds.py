"""Real playground-equivalent rounds: solve fresh problems and verify every
emitted certificate through the ACTUAL local Lean judge (the same
`judge.verify.verify_answer` + production proof policy the playground uses),
not the offline oracle. Reports acceptance by status, verdict, and route.

This is the honest end-to-end check: an offline-kernel pass is necessary but a
real Lean `accepted` is what the playground scores. Emphasis on the new
`true:egg_closure` engine, which had never been through the real judge in a
full solve->judge flow until now.

Usage:
    python stage2/experiments/real_rounds.py --true 3 --false 3 --workers 6
    python stage2/experiments/real_rounds.py --sources hard2,hard3 --true 5 --false 0
    python stage2/experiments/real_rounds.py --egg-frontier   # only egg-solvable misses
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "vendor" / "stage2-official"))
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))

import spotcheck  # noqa: E402  (sampling + sources)

DEFAULT_PROOF_POLICY = {
    "allowed_axioms": ["propext", "Quot.sound", "Classical.choice"],
    "allowed_declarations": ["letFun"],
    "allowed_declaration_prefixes": [
        "And.", "Bool.", "Classical.", "Decidable.", "Eq.",
        "EquationLHS", "EquationRHS", "Goal", "Exists.", "False.",
        "Fin.", "Fintype.", "Function.", "HEq.", "Iff.", "Init.", "Int.", "Lean.",
        "List.", "Magma.", "Mathlib.", "MemoFinOp.", "Nat.", "Nonempty.", "Not.",
        "NthRewrites.", "OfNat.", "Option.", "Or.", "Prod.", "PUnit.",
        "RewriteCombinations.", "RewriteGoal.", "RewriteHypothesis.",
        "RewriteHypothesisAndGoal.", "SimpleRewrites.",
        "Std.", "Subgraph.", "Subtype.", "Sum.",
        "Trans.", "True.", "Unit.",
        "JudgeDecide.", "JudgeFinOp.", "JudgeMagma.",
        "inst", "of_decide_", "submission.",
        "congrArg", "congr_arg", "eq_self", "of_eq_true", "id",
        "eq_comm", "eq_mp", "eq_mpr", "rfl", "absurd",
    ],
}


def _to_judge_problem(problem: dict) -> dict:
    return {
        "id": problem.get("id"),
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "equation1": problem["equation1"],
        "equation2": problem["equation2"],
        "proof_policy": DEFAULT_PROOF_POLICY,
    }


def _solve_and_judge(item: tuple[str, dict], *, false_budget: float,
                     effort: str) -> dict:
    """One real round: solve, then run the emitted cert through Lean."""
    import solver as S
    from judge.verify import verify_answer

    source, problem = item
    S.set_effort(effort)
    label = bool(problem.get("answer"))
    t0 = time.monotonic()
    record = S.solve_problem(problem, false_time_budget=false_budget)
    solve_s = time.monotonic() - t0
    out = {
        "source": source, "id": problem.get("id"),
        "label": "true" if label else "false",
        "solve_s": round(solve_s, 1),
    }
    if record is None:
        out["outcome"] = "skip"
        return out
    answer = record["answer"]
    out["route"] = record.get("route")
    out["verdict"] = answer.get("verdict")
    out["code_bytes"] = len(answer.get("code", "").encode("utf-8"))
    # verdict-vs-label sanity BEFORE the judge (a wrong verdict is a bug even
    # if Lean somehow accepted a bogus proof, which it will not)
    if (answer.get("verdict") == "true") != label:
        out["outcome"] = "WRONG_VERDICT"
        return out
    # The judge requires the payload to contain EXACTLY {verdict, code}; the
    # solver's answer dict also carries an id, so strip it the way the real
    # Solo/Marathon runner does before submitting.
    payload = S.judge_answer_payload(answer)
    if payload is None:
        out["outcome"] = "rejected"
        out["status"] = "malformed"
        out["error_kind"] = "payload_rejected_locally"
        return out
    t1 = time.monotonic()
    try:
        verdict_res = verify_answer(
            _to_judge_problem(problem), json.dumps(payload))
    except Exception as exc:  # transient Lean/lake infra failure under load
        out["judge_s"] = round(time.monotonic() - t1, 1)
        out["outcome"] = "judge_error"
        out["status"] = "infra_error"
        out["error_kind"] = f"{type(exc).__name__}: {str(exc)[:80]}"
        return out
    out["judge_s"] = round(time.monotonic() - t1, 1)
    out["status"] = verdict_res.get("status")
    out["error_kind"] = verdict_res.get("error_kind")
    out["outcome"] = "accepted" if verdict_res.get("status") == "accepted" else "rejected"
    return out


def _egg_frontier_items() -> list[tuple[str, dict]]:
    """The TRUE-miss rows the egg prototype solved (from the frontier study)."""
    skips = json.loads(
        (REPO / "stage2/results/skips-2026-07-23.json").read_text(encoding="utf-8"))
    from audit_corpus import SETS, HF_SETS, load_problems
    by_set: dict[str, dict] = {}
    items = []
    for m in skips:
        if not m["answer"]:
            continue
        name = m["set"]
        if name not in by_set:
            p = SETS.get(name) or HF_SETS.get(name)
            by_set[name] = {r["id"]: r for r in load_problems(p)}
        items.append((name, by_set[name][m["id"]]))
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--true", dest="n_true", type=int, default=3)
    ap.add_argument("--false", dest="n_false", type=int, default=3)
    ap.add_argument("--sources", default=",".join(spotcheck.ALL_SOURCES))
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--effort", default="standard",
                    choices=("fast", "standard", "deep"))
    ap.add_argument("--false-budget", type=float, default=3.0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--egg-frontier", action="store_true",
                    help="ignore sampling; judge the egg-solvable TRUE misses")
    args = ap.parse_args()

    if args.egg_frontier:
        batch = _egg_frontier_items()
        label = "egg-frontier"
    else:
        seed = args.seed if args.seed is not None else int(time.time())
        import random
        rng = random.Random(seed)
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
        etp = spotcheck.ETPMatrix() if spotcheck.ETP_SOURCE in sources else None
        seen = spotcheck.load_coverage()
        batch = spotcheck.sample_batch(
            sources, args.n_true, args.n_false, seen, rng,
            pure_random=False, etp=etp)
        label = f"seed={seed}"
        print(f"real-round {label} sources={sources} "
              f"true={args.n_true} false={args.n_false} effort={args.effort}",
              flush=True)

    print(f"solving+judging {len(batch)} rows through the REAL Lean judge "
          f"({args.workers} workers, effort={args.effort})...", flush=True)

    worker = partial(_solve_and_judge, false_budget=args.false_budget,
                     effort=args.effort)
    t0 = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(worker, batch, chunksize=1))
    elapsed = time.monotonic() - t0

    # tally
    from collections import Counter
    outc = Counter(r["outcome"] for r in results)
    solved = [r for r in results if r["outcome"] in ("accepted", "rejected")]
    accepted = [r for r in solved if r["outcome"] == "accepted"]
    print(f"\n=== real round: {len(batch)} rows in {elapsed:.0f}s ({label}) ===")
    print(f"  accepted (Lean): {len(accepted)}")
    print(f"  rejected (Lean): {outc.get('rejected', 0)}")
    print(f"  skipped (no cert): {outc.get('skip', 0)}")
    print(f"  judge infra error: {outc.get('judge_error', 0)}")
    print(f"  WRONG VERDICT:   {outc.get('WRONG_VERDICT', 0)}")
    if solved:
        print(f"  Lean accept rate (of submitted): "
              f"{100*len(accepted)/len(solved):.0f}%")

    # by verdict
    for v in ("true", "false"):
        vsolved = [r for r in solved if r.get("verdict") == v]
        vacc = [r for r in vsolved if r["outcome"] == "accepted"]
        if vsolved:
            print(f"  {v.upper():5s} submitted {len(vsolved)}, "
                  f"accepted {len(vacc)}")

    # egg specifically
    egg = [r for r in solved if str(r.get("route", "")).startswith("true:egg")]
    if egg:
        eacc = sum(1 for r in egg if r["outcome"] == "accepted")
        print(f"  true:egg_closure: {eacc}/{len(egg)} accepted by Lean")

    rejected = [r for r in solved if r["outcome"] == "rejected"]
    if rejected:
        print("\n  rejections:")
        for r in rejected[:25]:
            print(f"    {r['id']:26s} {r.get('verdict'):5s} "
                  f"{str(r.get('route'))[:34]:34s} "
                  f"{r.get('status')}/{r.get('error_kind')}")
    wrong = [r for r in results if r["outcome"] == "WRONG_VERDICT"]
    if wrong:
        print("\n  !!! WRONG VERDICTS (submitted answer contradicts label):")
        for r in wrong:
            print(f"    {r['id']} label={r['label']} verdict={r['verdict']} route={r.get('route')}")

    # accepted egg detail
    if egg:
        print("\n  egg rows judged:")
        for r in sorted(egg, key=lambda x: x["id"]):
            print(f"    {r['id']:26s} {r['outcome']:9s} "
                  f"cert={r.get('code_bytes')}b judge={r.get('judge_s')}s "
                  f"{r.get('route')}")

    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
