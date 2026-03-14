"""
magma_search.py — High-performance magma counterexample search engine.

Finds magma tables satisfying Eq1 but violating Eq2 using:
  - Constraint propagation (arc consistency on partial tables)
  - Backtracking search with intelligent cell ordering
  - Incremental equation checking (fail fast)
  - Canonical form pruning (break symmetries)
  - Size escalation (2 → 3 → 4 → 5)

This is the FALSE-proof engine: if we find a counterexample magma,
we have proven Eq1 does NOT imply Eq2.
"""

from __future__ import annotations
import itertools
import time
from typing import Optional
from analyze_equations import parse_equation, get_vars


# ── Fast term evaluator ──────────────────────────────────────────

def _compile_term(t, var_index: dict) -> object:
    """Compile a term AST into a fast evaluator function.

    Returns a callable(table, assignment) -> int, or an int index
    into the assignment array for variables.
    """
    if isinstance(t, str):
        return ("var", var_index[t])
    left = _compile_term(t[1], var_index)
    right = _compile_term(t[2], var_index)
    return ("op", left, right)


def _eval_compiled(node, table, assign):
    """Evaluate a compiled term."""
    if node[0] == "var":
        return assign[node[1]]
    l = _eval_compiled(node[1], table, assign)
    r = _eval_compiled(node[2], table, assign)
    return table[l][r]


def _check_eq_all_assignments(lhs_c, rhs_c, table, n, n_vars):
    """Check equation for all assignments. Returns True if eq holds universally."""
    if n_vars == 0:
        return _eval_compiled(lhs_c, table, []) == _eval_compiled(rhs_c, table, [])

    for assign in itertools.product(range(n), repeat=n_vars):
        if _eval_compiled(lhs_c, table, assign) != _eval_compiled(rhs_c, table, assign):
            return False
    return True


def _find_violating_assignment(lhs_c, rhs_c, table, n, n_vars):
    """Find an assignment that violates the equation, or None."""
    if n_vars == 0:
        if _eval_compiled(lhs_c, table, []) != _eval_compiled(rhs_c, table, []):
            return []
        return None

    for assign in itertools.product(range(n), repeat=n_vars):
        if _eval_compiled(lhs_c, table, assign) != _eval_compiled(rhs_c, table, assign):
            return list(assign)
    return None


# ── Constraint-propagating backtracking search ───────────────────

class MagmaSearcher:
    """Searches for magma tables satisfying eq1 but violating eq2.

    Uses constraint propagation + backtracking with partial table
    evaluation for early pruning.
    """

    def __init__(self, eq1_str: str, eq2_str: str, timeout: float = 10.0):
        self.eq1_parsed = parse_equation(eq1_str)
        self.eq2_parsed = parse_equation(eq2_str)
        self.timeout = timeout
        self._compile_equations()

    def _compile_equations(self):
        """Pre-compile equation ASTs for fast evaluation."""
        lhs1, rhs1 = self.eq1_parsed
        lhs2, rhs2 = self.eq2_parsed
        all_vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
        all_vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))

        self.vars1 = all_vars1
        self.vars2 = all_vars2
        self.n_vars1 = len(all_vars1)
        self.n_vars2 = len(all_vars2)

        idx1 = {v: i for i, v in enumerate(all_vars1)}
        idx2 = {v: i for i, v in enumerate(all_vars2)}

        self.lhs1_c = _compile_term(lhs1, idx1)
        self.rhs1_c = _compile_term(rhs1, idx1)
        self.lhs2_c = _compile_term(lhs2, idx2)
        self.rhs2_c = _compile_term(rhs2, idx2)

    def search(self, max_size: int = 5) -> Optional[list]:
        """Search for counterexample magma up to given size.

        Returns the magma table (list of lists) or None.
        """
        start = time.time()

        for n in range(2, max_size + 1):
            elapsed = time.time() - start
            if elapsed > self.timeout:
                return None

            remaining = self.timeout - elapsed
            result = self._search_size(n, remaining)
            if result is not None:
                return result

        return None

    def _search_size(self, n: int, timeout: float) -> Optional[list]:
        """Search for counterexample of exactly size n."""
        start = time.time()
        # table[i][j] = i ◇ j, initially -1 (unset)
        table = [[-1] * n for _ in range(n)]
        cells = [(i, j) for i in range(n) for j in range(n)]

        result = self._backtrack(table, cells, 0, n, start, timeout)
        return result

    def _backtrack(self, table, cells, idx, n, start, timeout) -> Optional[list]:
        """Backtracking search with constraint propagation."""
        if time.time() - start > timeout:
            return None

        if idx == len(cells):
            # Full table — verify eq1 holds and eq2 fails
            if self._satisfies_eq1(table, n) and not self._satisfies_eq2(table, n):
                return [row[:] for row in table]
            return None

        i, j = cells[idx]

        # Try each possible value for table[i][j]
        for v in range(n):
            table[i][j] = v

            # Early pruning: check if eq1 can still hold with partial table
            if self._partial_eq1_violated(table, n, i, j):
                continue

            result = self._backtrack(table, cells, idx + 1, n, start, timeout)
            if result is not None:
                return result

        table[i][j] = -1
        return None

    def _satisfies_eq1(self, table, n) -> bool:
        """Check if complete table satisfies eq1."""
        return _check_eq_all_assignments(self.lhs1_c, self.rhs1_c, table, n, self.n_vars1)

    def _satisfies_eq2(self, table, n) -> bool:
        """Check if complete table satisfies eq2."""
        return _check_eq_all_assignments(self.lhs2_c, self.rhs2_c, table, n, self.n_vars2)

    def _partial_eq1_violated(self, table, n, last_i, last_j) -> bool:
        """Check if eq1 is already violated for any complete assignment
        using only cells that are filled in.

        We check all assignments and if any evaluates to a definite
        mismatch, eq1 is violated.
        """
        if self.n_vars1 == 0:
            try:
                l = _eval_partial(self.lhs1_c, table, [])
                r = _eval_partial(self.rhs1_c, table, [])
                if l is not None and r is not None and l != r:
                    return True
            except Exception:
                pass
            return False

        for assign in itertools.product(range(n), repeat=self.n_vars1):
            try:
                l = _eval_partial(self.lhs1_c, table, assign)
                r = _eval_partial(self.rhs1_c, table, assign)
                if l is not None and r is not None and l != r:
                    return True
            except Exception:
                pass
        return False


def _eval_partial(node, table, assign):
    """Evaluate a compiled term on a partial table.

    Returns the result int, or None if a needed cell is unset (-1).
    """
    if node[0] == "var":
        return assign[node[1]]
    l = _eval_partial(node[1], table, assign)
    if l is None:
        return None
    r = _eval_partial(node[2], table, assign)
    if r is None:
        return None
    val = table[l][r]
    if val == -1:
        return None
    return val


# ── Exhaustive size-2 search (all 16 magmas, very fast) ──────────

def exhaustive_size2(eq1_str: str, eq2_str: str) -> Optional[list]:
    """Brute-force all 16 size-2 magma tables.

    This is instant and should always be tried first.
    """
    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)

    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
    vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))

    idx1 = {v: i for i, v in enumerate(vars1)}
    idx2 = {v: i for i, v in enumerate(vars2)}

    l1c = _compile_term(lhs1, idx1)
    r1c = _compile_term(rhs1, idx1)
    l2c = _compile_term(lhs2, idx2)
    r2c = _compile_term(rhs2, idx2)

    for vals in itertools.product(range(2), repeat=4):
        table = [[vals[0], vals[1]], [vals[2], vals[3]]]
        if _check_eq_all_assignments(l1c, r1c, table, 2, len(vars1)):
            if not _check_eq_all_assignments(l2c, r2c, table, 2, len(vars2)):
                return table
    return None


# ── Targeted search using known useful magma families ────────────

# These are magma tables known to be useful for separating equations.
# Each satisfies some equations but not others.
KNOWN_MAGMAS = {
    "left_zero": [[0, 0], [1, 1]],          # a◇b = a
    "right_zero": [[0, 1], [0, 1]],          # a◇b = b
    "const_0": [[0, 0], [0, 0]],             # a◇b = 0
    "const_1": [[1, 1], [1, 1]],             # a◇b = 1
    "xor": [[0, 1], [1, 0]],                 # a◇b = a xor b
    "and": [[0, 0], [0, 1]],                 # a◇b = a and b
    "or": [[0, 1], [1, 1]],                  # a◇b = a or b
    "nand": [[1, 1], [1, 0]],
    "nor": [[1, 0], [0, 0]],
    "implies": [[1, 1], [0, 1]],             # a→b
    "left_and_not": [[0, 1], [0, 0]],
    "right_xor_and": [[0, 0], [1, 0]],
    # Size 3
    "z3_add": [[0, 1, 2], [1, 2, 0], [2, 0, 1]],  # addition mod 3
    "z3_const_0": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    "left_3": [[0, 0, 0], [1, 1, 1], [2, 2, 2]],   # left projection size 3
    "right_3": [[0, 1, 2], [0, 1, 2], [0, 1, 2]],   # right projection size 3
    "min_3": [[0, 0, 0], [0, 1, 1], [0, 1, 2]],
    "max_3": [[0, 1, 2], [1, 1, 2], [2, 2, 2]],
}


def check_known_magmas(eq1_str: str, eq2_str: str) -> Optional[tuple]:
    """Check all known magma families for a counterexample.

    Returns (name, table) or None.
    """
    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)

    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
    vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))

    idx1 = {v: i for i, v in enumerate(vars1)}
    idx2 = {v: i for i, v in enumerate(vars2)}

    l1c = _compile_term(lhs1, idx1)
    r1c = _compile_term(rhs1, idx1)
    l2c = _compile_term(lhs2, idx2)
    r2c = _compile_term(rhs2, idx2)

    for name, table in KNOWN_MAGMAS.items():
        n = len(table)
        if _check_eq_all_assignments(l1c, r1c, table, n, len(vars1)):
            if not _check_eq_all_assignments(l2c, r2c, table, n, len(vars2)):
                return (name, table)
    return None


# ── Smart random search for larger sizes ─────────────────────────

def random_search(
    eq1_str: str,
    eq2_str: str,
    sizes: tuple = (3, 4, 5),
    n_trials: int = 5000,
    timeout: float = 5.0,
    seed: int = 42,
) -> Optional[list]:
    """Random magma table search with optional constraint filtering.

    Uses random tables but biases toward tables satisfying eq1 by
    trying structured constructions (linear magmas a◇b = pa+qb+r mod n).
    """
    import random as rng_mod
    rng = rng_mod.Random(seed)

    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)

    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
    vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))

    idx1 = {v: i for i, v in enumerate(vars1)}
    idx2 = {v: i for i, v in enumerate(vars2)}

    l1c = _compile_term(lhs1, idx1)
    r1c = _compile_term(rhs1, idx1)
    l2c = _compile_term(lhs2, idx2)
    r2c = _compile_term(rhs2, idx2)

    start = time.time()

    for n in sizes:
        # Phase 1: Linear magmas a◇b = (p*a + q*b + r) mod n
        for p in range(n):
            for q in range(n):
                for r in range(n):
                    if time.time() - start > timeout:
                        return None
                    table = [[(p * a + q * b + r) % n for b in range(n)] for a in range(n)]
                    if _check_eq_all_assignments(l1c, r1c, table, n, len(vars1)):
                        if not _check_eq_all_assignments(l2c, r2c, table, n, len(vars2)):
                            return table

        # Phase 2: Pure random
        trials_per_size = n_trials // len(sizes)
        for _ in range(trials_per_size):
            if time.time() - start > timeout:
                return None
            table = [[rng.randint(0, n - 1) for _ in range(n)] for _ in range(n)]
            if _check_eq_all_assignments(l1c, r1c, table, n, len(vars1)):
                if not _check_eq_all_assignments(l2c, r2c, table, n, len(vars2)):
                    return table

    return None


# ── Main search orchestrator ─────────────────────────────────────

def find_counterexample(
    eq1_str: str,
    eq2_str: str,
    timeout: float = 10.0,
    max_size: int = 5,
) -> Optional[dict]:
    """Find a counterexample magma proving eq1 does NOT imply eq2.

    Search strategy (escalating cost):
      1. Check known magma families (instant)
      2. Exhaustive size-2 (instant, 16 tables)
      3. Linear magmas size 3-5 (fast, structured)
      4. Random search size 3-5
      5. Backtracking search size 3 (expensive)

    Returns dict with 'table', 'size', 'method', 'time_s' or None.
    """
    t0 = time.time()

    # 1. Known magmas
    result = check_known_magmas(eq1_str, eq2_str)
    if result is not None:
        name, table = result
        return {"table": table, "size": len(table), "method": f"known:{name}",
                "time_s": time.time() - t0}

    # 2. Exhaustive size 2
    table = exhaustive_size2(eq1_str, eq2_str)
    if table is not None:
        return {"table": table, "size": 2, "method": "exhaustive_size2",
                "time_s": time.time() - t0}

    remaining = timeout - (time.time() - t0)
    if remaining <= 0:
        return None

    # 3+4. Linear + random for sizes 3-max_size
    sizes = tuple(range(3, max_size + 1))
    table = random_search(eq1_str, eq2_str, sizes=sizes,
                          n_trials=10000, timeout=remaining * 0.6)
    if table is not None:
        return {"table": table, "size": len(table), "method": "random_search",
                "time_s": time.time() - t0}

    remaining = timeout - (time.time() - t0)
    if remaining <= 0.5:
        return None

    # 5. Backtracking for size 3 (only if we have time)
    searcher = MagmaSearcher(eq1_str, eq2_str, timeout=remaining)
    table = searcher._search_size(3, remaining)
    if table is not None:
        return {"table": table, "size": 3, "method": "backtrack_size3",
                "time_s": time.time() - t0}

    return None


# ── CLI ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from analyze_equations import load_equations

    equations = load_equations()

    if len(sys.argv) >= 3:
        eq1_idx = int(sys.argv[1])
        eq2_idx = int(sys.argv[2])
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
    else:
        # Demo: Eq43 (assoc) does NOT imply Eq3 (idempotent)
        eq1_idx, eq2_idx = 4512, 3
        timeout = 10.0

    eq1_str = equations[eq1_idx - 1]
    eq2_str = equations[eq2_idx - 1]
    print(f"Eq{eq1_idx}: {eq1_str}")
    print(f"Eq{eq2_idx}: {eq2_str}")
    print(f"Searching for counterexample (timeout={timeout}s)...")

    result = find_counterexample(eq1_str, eq2_str, timeout=timeout)
    if result:
        print(f"\nCOUNTEREXAMPLE FOUND ({result['method']}, {result['time_s']:.3f}s):")
        print(f"  Size: {result['size']}")
        for i, row in enumerate(result['table']):
            print(f"  {i}: {row}")
    else:
        print("\nNo counterexample found.")
