#!/usr/bin/env python3
"""Greedy set-cover over candidate witness tables + held-out generalization.

Candidates come from a z3_witness_search output (--witnesses) and/or the teorth
FinitePoly library (--library).  Targets are rows the solver missed.  Every
candidate table is re-checked with the solver's own `witness_check`,
`table_is_renderable` and `witness_decide_is_affordable`, and rows already
refuted by the SHIPPED portfolio (WITNESS_TABLES + FP_WITNESS_TABLES +
FORMULA_WITNESSES) are excluded, so the reported coverage is incremental.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
import solver as S  # noqa: E402


def load_rows(paths):
    out = {}
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[str(r["id"])] = r
    return list(out.values())


def table_bytes(table):
    return len(json.dumps(table, separators=(",", ":"))) + 14


def shipped_hit(eq1, eq2):
    for _n, t in S.WITNESS_TABLES:
        if S.witness_check(eq1, eq2, t):
            return True
    for _n, t in S.FP_WITNESS_TABLES:
        if S.witness_check(eq1, eq2, t):
            return True
    for _n, t in S.O5_WITNESS_TABLES:
        if S.witness_check(eq1, eq2, t):
            return True
    for _n, t in S.FORMULA_WITNESSES:
        if S.witness_check(eq1, eq2, t):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--witnesses", type=Path, nargs="*", default=[],
                    help="z3_witness_search jsonl (rows with .table)")
    ap.add_argument("--library", type=Path, default=None,
                    help="teorth finitepoly library jsonl")
    ap.add_argument("--max-order", type=int, default=12)
    ap.add_argument("--targets", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    cands = []
    seen = set()
    for p in args.witnesses:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("verdict") != "FALSE":
                continue
            key = json.dumps(r["table"])
            if key in seen or len(r["table"]) > args.max_order:
                continue
            seen.add(key)
            cands.append({"src": "z3:" + r["id"], "table": r["table"]})
    if args.library:
        for line in args.library.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e["order"] > args.max_order:
                continue
            key = json.dumps(e["table"])
            if key in seen:
                continue
            seen.add(key)
            cands.append({"src": "teorth:" + str(e.get("name", e["order"])),
                          "table": e["table"]})

    rows = load_rows(args.targets)
    print(f"{len(rows)} target rows x {len(cands)} candidate tables", flush=True)

    parsed = []
    for r in rows:
        eq1 = S.parse_equation(str(r["equation1"]))
        eq2 = S.parse_equation(str(r["equation2"]))
        parsed.append((str(r["id"]), eq1, eq2))

    t0 = time.monotonic()
    already = 0
    cover = {}          # candidate index -> set of row ids
    target_ids = []
    for rid, eq1, eq2 in parsed:
        if shipped_hit(eq1, eq2):
            already += 1
            continue
        target_ids.append(rid)
        for i, c in enumerate(cands):
            if S.witness_check(eq1, eq2, c["table"]):
                if not (S.table_is_renderable(c["table"])
                        and S.witness_decide_is_affordable(eq1, eq2, c["table"])):
                    continue
                cover.setdefault(i, set()).add(rid)
    print(f"scan {time.monotonic()-t0:.0f}s; shipped already covers {already}; "
          f"targets {len(target_ids)}", flush=True)

    coverable = set()
    for s in cover.values():
        coverable |= s
    print(f"coverable by candidates: {len(coverable)}")

    remaining = set(coverable)
    chosen = []
    total_bytes = 0
    while remaining:
        best, gain = None, 0
        for i, s in cover.items():
            g = len(s & remaining)
            if g > gain or (g == gain and g > 0 and best is not None
                            and table_bytes(cands[i]["table"]) < table_bytes(cands[best]["table"])):
                best, gain = i, g
        if not best and gain == 0:
            break
        b = table_bytes(cands[best]["table"])
        total_bytes += b
        newly = sorted(cover[best] & remaining)
        remaining -= cover[best]
        chosen.append({"src": cands[best]["src"], "order": len(cands[best]["table"]),
                       "bytes": b, "cum_bytes": total_bytes, "gain": gain,
                       "covers_total": len(cover[best]), "rows": newly,
                       "table": cands[best]["table"]})
        del cover[best]
    out = {"targets": len(target_ids), "already_shipped": already,
           "candidates": len(cands), "coverable": len(coverable),
           "chosen": chosen, "total_bytes": total_bytes}
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"selected {len(chosen)} tables covering {len(coverable)}/{len(target_ids)} "
          f"targets for {total_bytes} bytes")
    for c in chosen[:25]:
        print(f"  +{c['gain']:3d} (of {c['covers_total']}) order {c['order']:2d} "
              f"{c['bytes']:5d} B cum {c['cum_bytes']:6d} {c['src']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
