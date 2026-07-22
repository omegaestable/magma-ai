"""Compact finite model finder for magma counterexamples (WS3).

Goal: find an order-n magma satisfying eq1 but violating eq2, for the sizes
where the solver's fixed family portfolio + Fin<=3 enumeration come up empty.

Two complementary engines:

- `dfs_find`   : backtracking over the Cayley table with early constraint
                 checking and unit propagation. Complete for a given n, so a
                 clean exhaustion is real evidence no order-n model exists.
- `local_find` : randomized repair search (WalkSAT-style) over full tables.
                 Incomplete but fast, and effective at n=5..8 where DFS is
                 hopeless.

Kept dependency-free and small so a winning version can be inlined into
solver.py without meaningful byte cost.
"""

from __future__ import annotations

import random
import time
from itertools import product
from typing import Any

Term = tuple[Any, ...]
UNSET = -1


# ---------------------------------------------------------------------------
# Partial evaluation
# ---------------------------------------------------------------------------

def _ev(term: Term, env: dict[str, int], table: list[list[int]]) -> int:
    """Evaluate, or return UNSET if it depends on an unassigned cell."""
    if term[0] == "var":
        return env[term[1]]
    a = _ev(term[1], env, table)
    if a == UNSET:
        return UNSET
    b = _ev(term[2], env, table)
    if b == UNSET:
        return UNSET
    return table[a][b]


def _ev_blocked(term: Term, env: dict[str, int], table: list[list[int]]):
    """Return (value, blocking_cell). Exactly one of the two is meaningful.

    blocking_cell is the unique unassigned cell this term is waiting on, or
    None if the term is fully determined or blocked on more than one cell.
    """
    if term[0] == "var":
        return env[term[1]], None
    a, ba = _ev_blocked(term[1], env, table)
    b, bb = _ev_blocked(term[2], env, table)
    if a == UNSET and b == UNSET:
        return UNSET, None          # waiting on two subtrees: not unit
    if a == UNSET:
        return UNSET, ba
    if b == UNSET:
        return UNSET, bb
    if table[a][b] == UNSET:
        return UNSET, (a, b)
    return table[a][b], None


def equation_holds(lhs: Term, rhs: Term, variables: list[str],
                   table: list[list[int]]) -> bool:
    n = len(table)
    for values in product(range(n), repeat=len(variables)):
        env = dict(zip(variables, values))
        if _ev(lhs, env, table) != _ev(rhs, env, table):
            return False
    return True


def is_counterexample(eq1: dict, eq2: dict, table: list[list[int]]) -> bool:
    return (equation_holds(eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
            and not equation_holds(eq2["lhs"], eq2["rhs"],
                                   list(eq2["variables"]), table))


# ---------------------------------------------------------------------------
# DFS with propagation
# ---------------------------------------------------------------------------

def dfs_find(eq1: dict, eq2: dict, n: int, *, deadline: float | None = None,
             rng: random.Random | None = None) -> list[list[int]] | None:
    lhs1, rhs1 = eq1["lhs"], eq1["rhs"]
    vars1 = list(eq1["variables"])
    envs1 = [dict(zip(vars1, vals))
             for vals in product(range(n), repeat=len(vars1))]

    table = [[UNSET] * n for _ in range(n)]
    order = [(r, c) for r in range(n) for c in range(n)]
    values = list(range(n))

    def consistent() -> bool:
        """No fully-determined eq1 instance is violated."""
        for env in envs1:
            a = _ev(lhs1, env, table)
            if a == UNSET:
                continue
            b = _ev(rhs1, env, table)
            if b == UNSET:
                continue
            if a != b:
                return False
        return True

    def propagate() -> list[tuple[int, int]] | None:
        """Force cells uniquely determined by a pending eq1 instance."""
        forced: list[tuple[int, int]] = []
        changed = True
        while changed:
            changed = False
            for env in envs1:
                va, ba = _ev_blocked(lhs1, env, table)
                vb, bb = _ev_blocked(rhs1, env, table)
                if va != UNSET and vb == UNSET and bb is not None:
                    r, c = bb
                    table[r][c] = va
                    forced.append(bb)
                    changed = True
                elif vb != UNSET and va == UNSET and ba is not None:
                    r, c = ba
                    table[r][c] = vb
                    forced.append(ba)
                    changed = True
        return forced

    def undo(cells: list[tuple[int, int]]) -> None:
        for r, c in cells:
            table[r][c] = UNSET

    def step(idx: int) -> bool:
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError
        while idx < len(order) and table[order[idx][0]][order[idx][1]] != UNSET:
            idx += 1
        if idx == len(order):
            return is_counterexample(eq1, eq2, table)
        r, c = order[idx]
        vals = values if rng is None else rng.sample(values, len(values))
        for v in vals:
            table[r][c] = v
            if consistent():
                forced = propagate()
                if consistent() and step(idx + 1):
                    return True
                undo(forced)
            table[r][c] = UNSET
        return False

    try:
        if step(0):
            return [row[:] for row in table]
    except (TimeoutError, RecursionError):
        return None
    return None


# ---------------------------------------------------------------------------
# Randomized repair search
# ---------------------------------------------------------------------------

def local_find(eq1: dict, eq2: dict, n: int, *, deadline: float | None = None,
               seed: int = 0, max_flips: int = 40000,
               noise: float = 0.25) -> list[list[int]] | None:
    """Minimise eq1 violations while requiring eq2 to fail somewhere."""
    rng = random.Random(seed)
    lhs1, rhs1 = eq1["lhs"], eq1["rhs"]
    vars1 = list(eq1["variables"])
    envs1 = [dict(zip(vars1, vals))
             for vals in product(range(n), repeat=len(vars1))]
    lhs2, rhs2 = eq2["lhs"], eq2["rhs"]
    vars2 = list(eq2["variables"])
    envs2 = [dict(zip(vars2, vals))
             for vals in product(range(n), repeat=len(vars2))]

    def violations(table) -> list[dict[str, int]]:
        return [env for env in envs1
                if _ev(lhs1, env, table) != _ev(rhs1, env, table)]

    def breaks_eq2(table) -> bool:
        return any(_ev(lhs2, env, table) != _ev(rhs2, env, table)
                   for env in envs2)

    while deadline is None or time.monotonic() < deadline:
        table = [[rng.randrange(n) for _ in range(n)] for _ in range(n)]
        for _ in range(max_flips):
            if deadline is not None and time.monotonic() >= deadline:
                return None
            bad = violations(table)
            if not bad:
                if breaks_eq2(table):
                    return table
                # Satisfies eq1 but also eq2: perturb and continue.
                r, c = rng.randrange(n), rng.randrange(n)
                table[r][c] = rng.randrange(n)
                continue
            env = bad[rng.randrange(len(bad))]
            cells = _touched_cells(lhs1, env, table) | _touched_cells(rhs1, env, table)
            if not cells:
                break
            cell_list = sorted(cells)
            r, c = cell_list[rng.randrange(len(cell_list))]
            if rng.random() < noise:
                table[r][c] = rng.randrange(n)
            else:
                best, best_score = table[r][c], len(bad) + 1
                for v in range(n):
                    old, table[r][c] = table[r][c], v
                    score = len(violations(table))
                    if breaks_eq2(table):
                        score -= 0.5
                    table[r][c] = old
                    if score < best_score:
                        best, best_score = v, score
                table[r][c] = best
    return None


def _touched_cells(term: Term, env: dict[str, int],
                   table: list[list[int]]) -> set[tuple[int, int]]:
    if term[0] == "var":
        return set()
    out = _touched_cells(term[1], env, table) | _touched_cells(term[2], env, table)
    a = _ev(term[1], env, table)
    b = _ev(term[2], env, table)
    if a != UNSET and b != UNSET:
        out.add((a, b))
    return out


def find_counterexample(eq1: dict, eq2: dict, *, sizes=(4, 5, 6),
                        time_budget: float = 5.0,
                        seed: int = 0) -> tuple[int, list[list[int]], str] | None:
    """Try each size with DFS then local search, within one shared budget."""
    deadline = time.monotonic() + time_budget
    for n in sizes:
        if time.monotonic() >= deadline:
            return None
        table = dfs_find(eq1, eq2, n, deadline=min(
            deadline, time.monotonic() + time_budget / (2 * len(sizes))))
        if table is not None and is_counterexample(eq1, eq2, table):
            return n, table, f"false:mace_dfs{n}"
        if time.monotonic() >= deadline:
            return None
        table = local_find(eq1, eq2, n, deadline=min(
            deadline, time.monotonic() + time_budget / (2 * len(sizes))), seed=seed)
        if table is not None and is_counterexample(eq1, eq2, table):
            return n, table, f"false:mace_ls{n}"
    return None
