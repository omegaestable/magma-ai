#!/usr/bin/env python3
"""Are the order-5 FALSE witnesses quasigroups?  If so, a random-Latin-square
generator is a *live* (stdlib, shippable) route that needs no shipped data.

Generates random Latin squares of the given orders (row-by-row backtracking
with shuffled candidate symbols) and tests them against target rows with the
solver's own exhaustive `witness_check`."""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
import solver as S  # noqa: E402


def random_latin_square(n: int, rng: random.Random):
    """Row-by-row backtracking; each row a permutation avoiding used symbols."""
    table = [[-1] * n for _ in range(n)]
    cols = [set() for _ in range(n)]

    def fill_row(r: int) -> bool:
        used = set()

        def place(c: int) -> bool:
            if c == n:
                return True
            options = [v for v in range(n) if v not in used and v not in cols[c]]
            rng.shuffle(options)
            for v in options:
                table[r][c] = v
                used.add(v)
                cols[c].add(v)
                if place(c + 1):
                    return True
                used.discard(v)
                cols[c].discard(v)
                table[r][c] = -1
            return False

        return place(0)

    for r in range(n):
        for _ in range(60):
            if fill_row(r):
                break
        else:
            return None
    return table


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", type=Path, nargs="+", required=True)
    ap.add_argument("--orders", default="8,9")
    ap.add_argument("--squares", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    rows = {}
    for p in args.targets:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                rows[str(r["id"])] = r
    parsed = [(rid, S.parse_equation(str(r["equation1"])),
               S.parse_equation(str(r["equation2"])))
              for rid, r in rows.items()]
    print(f"{len(parsed)} targets, {args.squares} squares per order "
          f"{args.orders}", flush=True)
    rng = random.Random(args.seed)
    covered = {}
    t0 = time.monotonic()
    for n in (int(x) for x in args.orders.split(",")):
        for k in range(args.squares):
            tab = random_latin_square(n, rng)
            if tab is None:
                continue
            for rid, eq1, eq2 in parsed:
                if rid in covered:
                    continue
                if S.witness_check(eq1, eq2, tab):
                    covered[rid] = (n, k, tab)
            if (k + 1) % 250 == 0:
                print(f"  n={n} {k+1} squares -> {len(covered)} covered "
                      f"({time.monotonic()-t0:.0f}s)", flush=True)
    print(f"COVERED {len(covered)}/{len(parsed)} in {time.monotonic()-t0:.0f}s")
    if args.out:
        args.out.write_text(json.dumps(
            {k: {"order": v[0], "square_index": v[1], "table": v[2]}
             for k, v in covered.items()}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
