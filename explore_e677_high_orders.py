#!/usr/bin/env python3
"""
High-order exploration for the finite E677 =>? E255 problem.

We study finite magmas (M, *) satisfying

    (A)  x = y * ( x * ( (y * x) * y ) )

and look for failures of

    (B)  x = ((x * x) * x) * x.

This script is built around specific math for E677/E255, not generic full
brute force over all magmas.

Main ideas used
===============

1. Finite models of (A) are left quasigroups.
   For each fixed y, x = y * (...) shows L_y is surjective; on a finite set that
   means bijective. So every row of the table is a permutation.

2. On a finite model, (A) is equivalent to a much more local permutation law.
   If a leftdiv b means left division (the unique z with a * z = b), then from (A):

       (y * x) * y = leftdiv(x, leftdiv(y, x)).

   Writing rows as permutations p_a(z) = a * z and inv_a = p_a^{-1}, this is

       p_{p_y(x)}(y) = inv_x(inv_y(x)).

   This formula is the workhorse of the search.

3. High-order structured families.
   We search affine and translation-invariant models on Z/nZ using formulas that
   reduce (A) to O(n) or O(1) congruence checks instead of O(n^2) table checks.

4. Row-repair search inside the left-quasigroup space.
   For a target row r and each column y, the local law forces exactly one value:

       row_r[y] = inv_x(inv_y(x)), where x = inv_y[r].

   Given all other rows, this yields a suggested row for r. We repeatedly repair
   rows toward these suggested values, with random perturbations and restarts.

Subcommands
===========

  affine       scan affine cyclic models quickly
  transinv     scan translation-invariant cyclic models quickly
  power5       build explicit A-models of sizes 5^k by direct product
  search       high-order randomized row-repair search inside left quasigroups
  sweep        run the randomized search over a range of sizes

Examples
========

  python explore_e677_high_orders.py affine --nmax 200
  python explore_e677_high_orders.py transinv --n 35 --samples 200000
  python explore_e677_high_orders.py power5 --k 3
  python explore_e677_high_orders.py search --n 49 --seconds 300 --workers 8 --seed-mode mixed
  python explore_e677_high_orders.py sweep --nmin 20 --nmax 60 --seconds 60 --workers 8
"""

from __future__ import annotations

import argparse
import itertools
import math
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

Table = List[List[int]]
Perm = List[int]


# -----------------------------------------------------------------------------
# A known nontrivial finite model of (A), of size 5
# -----------------------------------------------------------------------------

KNOWN_MODEL_5: Table = [
    [0, 2, 1, 4, 3],
    [3, 1, 4, 0, 2],
    [4, 3, 2, 1, 0],
    [2, 4, 0, 3, 1],
    [1, 0, 3, 2, 4],
]


# -----------------------------------------------------------------------------
# Basic utilities
# -----------------------------------------------------------------------------


def inverse_rows(table: Table) -> Table:
    n = len(table)
    inv = [[0] * n for _ in range(n)]
    for a, row in enumerate(table):
        for j, v in enumerate(row):
            inv[a][v] = j
    return inv


def is_left_quasigroup(table: Table) -> bool:
    n = len(table)
    target = set(range(n))
    return all(set(row) == target for row in table)


def check_A_direct(table: Table) -> bool:
    n = len(table)
    for y in range(n):
        row_y = table[y]
        for x in range(n):
            if row_y[table[x][table[row_y[x]][y]]] != x:
                return False
    return True


def check_A_local(table: Table, inv: Optional[Table] = None) -> bool:
    if inv is None:
        inv = inverse_rows(table)
    n = len(table)
    for y in range(n):
        row_y = table[y]
        inv_y = inv[y]
        for x in range(n):
            k = row_y[x]
            if table[k][y] != inv[x][inv_y[x]]:
                return False
    return True


def count_A_violations_local(table: Table, inv: Optional[Table] = None) -> int:
    if inv is None:
        inv = inverse_rows(table)
    n = len(table)
    bad = 0
    for y in range(n):
        row_y = table[y]
        inv_y = inv[y]
        for x in range(n):
            k = row_y[x]
            if table[k][y] != inv[x][inv_y[x]]:
                bad += 1
    return bad


def row_involvement_loads(table: Table, inv: Optional[Table] = None) -> Tuple[List[int], int]:
    if inv is None:
        inv = inverse_rows(table)
    n = len(table)
    loads = [0] * n
    bad = 0
    for y in range(n):
        row_y = table[y]
        inv_y = inv[y]
        for x in range(n):
            k = row_y[x]
            if table[k][y] != inv[x][inv_y[x]]:
                bad += 1
                loads[x] += 1
                loads[y] += 1
                loads[k] += 1
    return loads, bad


def B_witnesses(table: Table) -> List[int]:
    n = len(table)
    out: List[int] = []
    for x in range(n):
        if table[table[table[x][x]][x]][x] != x:
            out.append(x)
    return out


def format_table(table: Table) -> str:
    n = len(table)
    width = max(2, len(str(n - 1)))
    head = " " * (width + 3) + " ".join(f"{j:>{width}}" for j in range(n))
    sep = " " * (width + 1) + "+" + "-" * ((width + 1) * n + (n - 1))
    rows = [head, sep]
    for i, row in enumerate(table):
        rows.append(f"{i:>{width}} | " + " ".join(f"{v:>{width}}" for v in row))
    return "\n".join(rows)


def print_model(table: Table, label: str) -> None:
    inv = inverse_rows(table)
    print(f"[{label}] size={len(table)}")
    print(format_table(table))
    print(f"left quasigroup: {is_left_quasigroup(table)}")
    print(f"A (local check): {check_A_local(table, inv)}")
    print(f"A (direct check): {check_A_direct(table)}")
    badB = B_witnesses(table)
    print(f"B witnesses: {badB if badB else 'none'}")
    print()


# -----------------------------------------------------------------------------
# Direct products: produce explicit large A-models quickly
# -----------------------------------------------------------------------------


def direct_product(a: Table, b: Table) -> Table:
    na = len(a)
    nb = len(b)
    n = na * nb
    out = [[0] * n for _ in range(n)]
    for xa in range(na):
        for xb in range(nb):
            x = xa * nb + xb
            row = out[x]
            rowa = a[xa]
            rowb_index = xb
            for ya in range(na):
                rowa_ya = rowa[ya] * nb
                brow = b[rowb_index]
                base = ya * nb
                for yb in range(nb):
                    y = base + yb
                    row[y] = rowa_ya + brow[yb]
    return out


def repeated_power5(k: int) -> Table:
    if k < 1:
        raise ValueError("k must be >= 1")
    t = [row[:] for row in KNOWN_MODEL_5]
    for _ in range(1, k):
        t = direct_product(t, KNOWN_MODEL_5)
    return t


# -----------------------------------------------------------------------------
# Affine cyclic family: x*y = a x + b y + c mod n
# -----------------------------------------------------------------------------


def affine_table(n: int, a: int, b: int, c: int) -> Table:
    return [[(a * x + b * y + c) % n for y in range(n)] for x in range(n)]


def affine_A_conditions(n: int, a: int, b: int, c: int) -> bool:
    # Derived by symbolic expansion of (A) in Z/nZ.
    # x coefficient: 1 = a*b*(1+b^2)
    # y coefficient: 0 = a + b^2*(a^2+b)
    # constant:      0 = c*(b*(b*(a+1)+1)+1)
    return (
        (a * b * (1 + b * b) - 1) % n == 0
        and (a + (b * b) * (a * a + b)) % n == 0
        and (c * (b * (b * (a + 1) + 1) + 1)) % n == 0
    )


def affine_B_witnesses(n: int, a: int, b: int, c: int) -> List[int]:
    # (((x*x)*x)*x) = alpha*x + beta, so either all x satisfy B or all fail.
    alpha = (a * (a * (a + b) + b) + b) % n
    beta = ((a * (a + 1) + 1) * c) % n
    if alpha == 1 and beta == 0:
        return []
    return list(range(n))


def cmd_affine(args: argparse.Namespace) -> int:
    total = 0
    for n in range(args.nmin, args.nmax + 1):
        units = [u for u in range(n) if math.gcd(u, n) == 1]
        for a in range(n):
            for b in units:
                for c in range(n):
                    if not affine_A_conditions(n, a, b, c):
                        continue
                    total += 1
                    badB = affine_B_witnesses(n, a, b, c)
                    label = f"affine n={n} a={a} b={b} c={c}"
                    if args.print_tables:
                        print_model(affine_table(n, a, b, c), label)
                    else:
                        print(f"[{label}] A holds, B witnesses: {badB if badB else 'none'}")
                    if badB and args.stop_on_counterexample:
                        return 1
    print(f"total affine models found: {total}")
    return 0


# -----------------------------------------------------------------------------
# Translation-invariant cyclic family: x*y = x + f(y-x) mod n
# -----------------------------------------------------------------------------


def transinv_table_from_perm(perm: Sequence[int]) -> Table:
    n = len(perm)
    return [[(x + perm[(y - x) % n]) % n for y in range(n)] for x in range(n)]


def transinv_A_holds(perm: Sequence[int]) -> bool:
    # Derived functional equation:
    #   f(d + f(-d + f(d) + f(-f(d)))) = d
    n = len(perm)
    for d in range(n):
        fd = perm[d]
        t = (-d + fd + perm[(-fd) % n]) % n
        u = (d + perm[t]) % n
        if perm[u] != d:
            return False
    return True


def transinv_B_witnesses(perm: Sequence[int]) -> List[int]:
    # Either B holds for all x or fails for all x in a translation-invariant model.
    n = len(perm)
    a = perm[0]
    b = perm[(-a) % n]
    c = perm[(-a - b) % n]
    if (a + b + c) % n == 0:
        return []
    return list(range(n))


def cmd_transinv(args: argparse.Namespace) -> int:
    rng = random.Random(args.seed)
    n = args.n
    total = 0

    if args.all:
        iterator: Iterable[Tuple[int, ...]] = itertools.permutations(range(n))
    else:
        def iterator_gen() -> Iterable[Tuple[int, ...]]:
            base = list(range(n))
            for _ in range(args.samples):
                rng.shuffle(base)
                yield tuple(base)
        iterator = iterator_gen()

    for idx, perm in enumerate(iterator, 1):
        if not transinv_A_holds(perm):
            continue
        total += 1
        badB = transinv_B_witnesses(perm)
        label = f"transinv n={n} f={perm}"
        if args.print_tables:
            print_model(transinv_table_from_perm(perm), label)
        else:
            print(f"[{label}] A holds, B witnesses: {badB if badB else 'none'}")
        if badB and args.stop_on_counterexample:
            return 1
        if (not args.all) and idx % 10000 == 0:
            print(f"checked {idx} permutations", file=sys.stderr)

    print(f"total translation-invariant models found: {total}")
    return 0


# -----------------------------------------------------------------------------
# Row-repair machinery for high-order left-quasigroup search
# -----------------------------------------------------------------------------


def random_left_quasigroup(n: int, rng: random.Random) -> Table:
    base = list(range(n))
    out = []
    for _ in range(n):
        row = base[:]
        rng.shuffle(row)
        out.append(row)
    return out


def random_transinv_seed(n: int, rng: random.Random) -> Table:
    perm = list(range(n))
    rng.shuffle(perm)
    return transinv_table_from_perm(perm)


def seed_table(n: int, rng: random.Random, mode: str) -> Table:
    if mode == "random":
        return random_left_quasigroup(n, rng)
    if mode == "transinv":
        return random_transinv_seed(n, rng)
    if mode == "mixed":
        return random_left_quasigroup(n, rng) if rng.random() < 0.5 else random_transinv_seed(n, rng)
    if mode == "power5":
        # Only available when n = 5^k.
        m = n
        k = 0
        while m > 1 and m % 5 == 0:
            m //= 5
            k += 1
        if m == 1 and k >= 1:
            return repeated_power5(k)
        return random_left_quasigroup(n, rng)
    raise ValueError(f"unknown seed mode {mode!r}")


def target_suggestions_for_row(table: Table, inv: Table, r: int) -> List[int]:
    # For each column y, the local law forces row_r[y] to exactly one value.
    n = len(table)
    s = [0] * n
    for y in range(n):
        x = inv[y][r]           # unique x with y*x = r
        s[y] = inv[x][inv[y][x]]
    return s


def best_response_permutation(suggest: Sequence[int], current: Sequence[int], rng: random.Random) -> List[int]:
    # We want a permutation matching as many suggested values as possible.
    # Since the reward is 1 per matched column and suggested values may repeat,
    # we can realize at most one column per distinct suggested value.
    n = len(suggest)
    freq = Counter(suggest)
    cols = list(range(n))
    rng.shuffle(cols)
    cols.sort(key=lambda i: (freq[suggest[i]], i))  # rare suggestions first

    row: List[Optional[int]] = [None] * n
    used = set()

    # First preserve existing matches when possible.
    for i in cols:
        v = suggest[i]
        if current[i] == v and v not in used:
            row[i] = v
            used.add(v)

    # Then realize one column for each remaining distinct suggestion value.
    for i in cols:
        if row[i] is not None:
            continue
        v = suggest[i]
        if v not in used:
            row[i] = v
            used.add(v)

    # Fill the rest with unused values, preferring current entries when possible.
    unused = [v for v in range(n) if v not in used]
    unused_set = set(unused)
    for i in range(n):
        if row[i] is None and current[i] in unused_set:
            row[i] = current[i]
            unused_set.remove(current[i])
    unused = list(unused_set)
    rng.shuffle(unused)
    it = iter(unused)
    for i in range(n):
        if row[i] is None:
            row[i] = next(it)

    return [int(v) for v in row]


def random_row_perturbation(row: Sequence[int], rng: random.Random) -> List[int]:
    out = list(row)
    n = len(out)
    mode = rng.random()
    if mode < 0.6:
        i, j = rng.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
    elif mode < 0.9:
        idx = rng.sample(range(n), 3)
        a, b, c = idx
        out[a], out[b], out[c] = out[c], out[a], out[b]
    else:
        rng.shuffle(out)
    return out


def score_table(table: Table) -> Tuple[int, int]:
    inv = inverse_rows(table)
    a_bad = count_A_violations_local(table, inv)
    b_good = len(table) - len(B_witnesses(table))
    return a_bad, b_good


@dataclass
class SearchResult:
    found_counterexample: bool
    best_a_bad: int
    best_b_good: int
    counterexample: Optional[Table]
    model_A: Optional[Table]
    elapsed: float


def high_order_search_one(
    n: int,
    seconds: float,
    seed: int,
    seed_mode: str,
    keep_A_models: bool,
) -> SearchResult:
    rng = random.Random(seed)
    deadline = time.time() + seconds

    table = seed_table(n, rng, seed_mode)
    best = [row[:] for row in table]
    best_score = score_table(best)
    best_A_model: Optional[Table] = None
    if best_score[0] == 0:
        best_A_model = [row[:] for row in best]
        if B_witnesses(best):
            return SearchResult(True, 0, best_score[1], [row[:] for row in best], best_A_model, 0.0)

    while time.time() < deadline:
        inv = inverse_rows(table)
        loads, bad = row_involvement_loads(table, inv)
        b_good = n - len(B_witnesses(table))

        if bad == 0:
            if B_witnesses(table):
                return SearchResult(True, 0, b_good, [row[:] for row in table], [row[:] for row in table], seconds - max(deadline - time.time(), 0.0))
            if keep_A_models:
                best_A_model = [row[:] for row in table]
            # Found an A-model but not a counterexample. Jump away but keep it.
            table = seed_table(n, rng, seed_mode)
            continue

        # Choose candidate rows to repair: mostly the heaviest rows, sometimes a random row.
        order = list(range(n))
        order.sort(key=lambda r: loads[r], reverse=True)
        candidates = order[: min(max(6, n // 6), n)]
        if rng.random() < 0.2:
            candidates.append(rng.randrange(n))

        improved = False
        cur_score = (bad, b_good)
        for r in candidates:
            cur_row = table[r]
            suggest = target_suggestions_for_row(table, inv, r)
            new_row = best_response_permutation(suggest, cur_row, rng)
            if new_row == cur_row:
                continue
            table[r] = new_row
            new_score = score_table(table)
            if new_score <= cur_score or rng.random() < 0.03:
                cur_score = new_score
                improved = improved or (new_score < (bad, b_good))
                break
            table[r] = cur_row

        if not improved:
            # Large-neighborhood perturbation around a bad zone.
            r = max(range(n), key=lambda i: loads[i]) if max(loads) > 0 else rng.randrange(n)
            old_row = table[r]
            table[r] = random_row_perturbation(old_row, rng)
            new_score = score_table(table)
            if not (new_score < (bad, b_good) or rng.random() < 0.10):
                table[r] = old_row

        now_score = score_table(table)
        if now_score < best_score:
            best_score = now_score
            best = [row[:] for row in table]
            if best_score[0] == 0:
                best_A_model = [row[:] for row in best]
                if B_witnesses(best):
                    return SearchResult(True, 0, best_score[1], [row[:] for row in best], best_A_model, seconds - max(deadline - time.time(), 0.0))

        # Occasional full restart.
        if rng.random() < 0.002:
            table = seed_table(n, rng, seed_mode)

    return SearchResult(False, best_score[0], best_score[1], None, best_A_model, seconds)


def _search_worker(args: Tuple[int, float, int, str, bool]) -> SearchResult:
    return high_order_search_one(*args)


def cmd_search(args: argparse.Namespace) -> int:
    workers = max(1, args.workers)
    tasks = [(args.n, args.seconds, args.seed + 1000003 * i, args.seed_mode, args.keep_A_models) for i in range(workers)]

    best_result: Optional[SearchResult] = None
    if workers == 1:
        best_result = _search_worker(tasks[0])
    else:
        with mp.Pool(processes=workers) as pool:
            for res in pool.imap_unordered(_search_worker, tasks):
                if best_result is None or (res.best_a_bad, res.best_b_good) < (best_result.best_a_bad, best_result.best_b_good):
                    best_result = res
                if res.found_counterexample:
                    pool.terminate()
                    best_result = res
                    break

    assert best_result is not None
    if best_result.found_counterexample and best_result.counterexample is not None:
        print_model(best_result.counterexample, f"counterexample n={args.n}")
        return 1

    print(f"no counterexample found at n={args.n}")
    print(f"best local A-violation count: {best_result.best_a_bad}")
    print(f"best local B-good count: {best_result.best_b_good} / {args.n}")
    if best_result.model_A is not None:
        print_model(best_result.model_A, f"A-model found at n={args.n} (still satisfies B)")
    return 0


def cmd_sweep(args: argparse.Namespace) -> int:
    exit_code = 0
    for n in range(args.nmin, args.nmax + 1):
        ns = argparse.Namespace(
            n=n,
            seconds=args.seconds,
            workers=args.workers,
            seed=args.seed + 7919 * n,
            seed_mode=args.seed_mode,
            keep_A_models=args.keep_A_models,
        )
        print(f"===== n={n} =====")
        code = cmd_search(ns)
        if code != 0:
            exit_code = code
            if args.stop_on_counterexample:
                return exit_code
    return exit_code


def cmd_power5(args: argparse.Namespace) -> int:
    table = repeated_power5(args.k)
    print_model(table, f"power5 k={args.k}")
    return 0 if not B_witnesses(table) else 1


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="High-order exploration for the finite E677/E255 problem")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("affine", help="scan affine cyclic models x*y = a x + b y + c mod n")
    pa.add_argument("--nmin", type=int, default=1)
    pa.add_argument("--nmax", type=int, default=50)
    pa.add_argument("--stop-on-counterexample", action="store_true")
    pa.add_argument("--print-tables", action="store_true")

    pt = sub.add_parser("transinv", help="scan translation-invariant cyclic models x*y = x + f(y-x) mod n")
    pt.add_argument("--n", type=int, required=True)
    pt.add_argument("--all", action="store_true", help="exhaust all permutations f (small n only)")
    pt.add_argument("--samples", type=int, default=100000)
    pt.add_argument("--seed", type=int, default=0)
    pt.add_argument("--stop-on-counterexample", action="store_true")
    pt.add_argument("--print-tables", action="store_true")

    pp = sub.add_parser("power5", help="construct the explicit direct-product model of size 5^k")
    pp.add_argument("--k", type=int, required=True)

    ps = sub.add_parser("search", help="high-order randomized row-repair search inside left quasigroups")
    ps.add_argument("--n", type=int, required=True)
    ps.add_argument("--seconds", type=float, default=60.0)
    ps.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    ps.add_argument("--seed", type=int, default=0)
    ps.add_argument("--seed-mode", choices=["random", "transinv", "mixed", "power5"], default="mixed")
    ps.add_argument("--keep-A-models", action="store_true")

    pw = sub.add_parser("sweep", help="run the high-order search over a range of sizes")
    pw.add_argument("--nmin", type=int, required=True)
    pw.add_argument("--nmax", type=int, required=True)
    pw.add_argument("--seconds", type=float, default=30.0)
    pw.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    pw.add_argument("--seed", type=int, default=0)
    pw.add_argument("--seed-mode", choices=["random", "transinv", "mixed", "power5"], default="mixed")
    pw.add_argument("--keep-A-models", action="store_true")
    pw.add_argument("--stop-on-counterexample", action="store_true")

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "affine":
        return cmd_affine(args)
    if args.cmd == "transinv":
        return cmd_transinv(args)
    if args.cmd == "power5":
        return cmd_power5(args)
    if args.cmd == "search":
        return cmd_search(args)
    if args.cmd == "sweep":
        return cmd_sweep(args)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
