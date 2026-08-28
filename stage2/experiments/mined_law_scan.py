#!/usr/bin/env python3
"""Scan a set of candidate rung laws over a row file, egg_ladder-style.

For every row: prove each law from eq1 by multi-rule equality saturation; if
proved, add it as a `have` rung and try the goal.  A hit is rendered as the
shipped `lemma_chain` certificate and re-checked by the offline kernel, so
nothing here can report an unsound win.

Used to ask whether laws mined from a handful of LLM answers generalise to a
family, i.e. whether they belong in `LEMMA_LIBRARY_TEXT`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402


def scan_row(job) -> dict:
    row, laws, budget = job
    S.set_effort("fast")
    S.set_hard_deadline(None)
    S.clear_term_caches()
    out = {"id": str(row.get("id")), "label": row.get("label")}
    try:
        eq1 = S.parse_equation(str(row["equation1"]))
        eq2 = S.parse_equation(str(row["equation2"]))
    except (KeyError, ValueError):
        out["status"] = "parse_error"
        return out
    base = [S._egg_rule_from(eq1, "h")]
    proved: list[str] = []
    t0 = time.monotonic()
    for text in laws:
        lemma = S.usable_llm_lemma(text)
        if lemma is None:
            continue
        if not S.lemma_survives_models(eq1, lemma):
            continue
        proof = S.egg_saturate_prove_multi(base, lemma, time_budget=budget)
        if proof is None:
            continue
        proved.append(text)
        rules = base + [S._egg_rule_from(lemma, "hlem0")]
        gproof = S.egg_saturate_prove_multi(rules, eq2, time_budget=budget)
        if gproof is None:
            continue
        code = S._lemma_chain_goal_certificate(
            [("hlem0", lemma, proof)], eq2["variables"], gproof)
        try:
            oracles.check_no_banned_tactics(code, "egg_ladder")
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
        except oracles.OracleError as exc:
            out["status"] = "oracle_fail"
            out["detail"] = str(exc)[:150]
            out["law"] = text
            return out
        out.update(status="solved", law=text,
                   code_bytes=len(code.encode("utf-8")),
                   seconds=round(time.monotonic() - t0, 1),
                   laws_proved=proved)
        return out
    out.update(status="unsolved", laws_proved=proved,
               seconds=round(time.monotonic() - t0, 1))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--laws", type=Path, required=True)
    ap.add_argument("--ids", type=Path, default=None,
                    help="json list of ids to keep")
    ap.add_argument("--budget", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    rows = [json.loads(l) for l in
            args.rows.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.ids:
        keep = set(json.loads(args.ids.read_text(encoding="utf-8")))
        rows = [r for r in rows if str(r.get("id")) in keep]
    if args.limit:
        rows = rows[: args.limit]
    laws = json.loads(args.laws.read_text(encoding="utf-8"))
    print("rows %d laws %d budget %.1fs" % (len(rows), len(laws), args.budget),
          flush=True)
    jobs = [(r, laws, args.budget) for r in rows]
    t0 = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        done = list(pool.map(scan_row, jobs, chunksize=1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in done:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    import collections
    print("statuses", collections.Counter(r["status"] for r in done))
    hits = collections.Counter(r.get("law") for r in done
                               if r["status"] == "solved")
    for law, n in hits.most_common():
        print("  %3d  %s" % (n, law))
    print("wall %.0fs" % (time.monotonic() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
