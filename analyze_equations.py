"""
analyze_equations.py — Parse and analyze equational laws for magmas.

Provides structural feature extraction for equations of the form "LHS = RHS"
where ◇ is a binary magma operation.
"""

import re
import itertools
import random
from typing import Optional


def parse_equation(eq_str: str) -> tuple:
    """Parse an equation string like 'x ◇ (y ◇ z) = (x ◇ y) ◇ z' into (LHS_tree, RHS_tree)."""
    parts = eq_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid equation: {eq_str}")
    return (parse_term(parts[0].strip()), parse_term(parts[1].strip()))


def parse_term(s: str):
    """Parse a term string into an AST. Returns a string for variables, or ('*', left, right) for operations."""
    s = s.strip()
    # Replace ◇ with * for internal representation
    s = s.replace('◇', '*')
    # Remove spaces
    s = s.replace(' ', '')

    # Remove outermost balanced parentheses
    while s.startswith('(') and s.endswith(')'):
        depth = 0
        is_balanced = True
        for i in range(len(s) - 1):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
            if depth == 0:
                is_balanced = False
                break
        if is_balanced:
            s = s[1:-1]
        else:
            break

    # Find the main '*' operator at depth 0 (rightmost for left-associativity)
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        if s[i] == ')':
            depth += 1
        elif s[i] == '(':
            depth -= 1
        elif s[i] == '*' and depth == 0:
            return ('*', parse_term(s[:i]), parse_term(s[i + 1:]))
    return s  # Variable


def tree_to_str(t, use_diamond: bool = True) -> str:
    """Convert AST back to string."""
    if isinstance(t, str):
        return t
    op = ' ◇ ' if use_diamond else ' * '
    left = tree_to_str(t[1], use_diamond)
    right = tree_to_str(t[2], use_diamond)
    return f'({left}{op}{right})'


def get_vars(t) -> set:
    """Get all variables in a term."""
    if isinstance(t, str):
        return {t} if t.isalpha() else set()
    return get_vars(t[1]) | get_vars(t[2])


def get_depth(t) -> int:
    """Get the depth of a term tree."""
    if isinstance(t, str):
        return 0
    return 1 + max(get_depth(t[1]), get_depth(t[2]))


def count_ops(t) -> int:
    """Count operations in a term."""
    if isinstance(t, str):
        return 0
    return 1 + count_ops(t[1]) + count_ops(t[2])


def term_size(t) -> int:
    """Count total nodes (vars + ops) in a term."""
    if isinstance(t, str):
        return 1
    return 1 + term_size(t[1]) + term_size(t[2])


def count_var_occ(t, var: str) -> int:
    """Count occurrences of a variable in a term."""
    if isinstance(t, str):
        return 1 if t == var else 0
    return count_var_occ(t[1], var) + count_var_occ(t[2], var)


def get_dual(t):
    """Get the dual of a term (swap left and right children of every operation)."""
    if isinstance(t, str):
        return t
    return ('*', get_dual(t[2]), get_dual(t[1]))


def match(pattern, expr, mapping: dict, _depth: int = 0) -> bool:
    """Check if expr matches pattern, building variable mapping."""
    if _depth > 50:
        return False
    if isinstance(pattern, str):
        if pattern.isalpha():
            if pattern in mapping:
                return mapping[pattern] == expr
            mapping[pattern] = expr
            return True
        return pattern == expr
    if isinstance(expr, str) or not isinstance(expr, tuple):
        return False
    if len(pattern) != len(expr):
        return False
    return all(match(pattern[i], expr[i], mapping, _depth + 1) for i in range(len(pattern)))


def substitute(t, mapping: dict):
    """Apply a variable substitution to a term."""
    if isinstance(t, str):
        return mapping.get(t, t)
    return (t[0], substitute(t[1], mapping), substitute(t[2], mapping))


def is_specialization(eq1, eq2) -> bool:
    """Check if eq1 directly specializes to eq2 (i.e., eq1 implies eq2 via substitution)."""
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    # Try matching eq1 pattern against eq2
    m = {}
    if match(lhs1, lhs2, m) and match(rhs1, rhs2, m):
        return True
    # Try with eq1 sides swapped
    m = {}
    if match(rhs1, lhs2, m) and match(lhs1, rhs2, m):
        return True
    return False


def get_rewrites(term, rules, limit=500):
    """BFS rewrite a term using the given rules. Returns set of reachable terms."""
    visited = {term}
    queue = [term]
    for curr in queue:
        if len(visited) >= limit:
            break
        for rl, rr in rules:
            m = {}
            if match(rl, curr, m):
                new_term = substitute(rr, m)
                if new_term not in visited:
                    visited.add(new_term)
                    queue.append(new_term)
        if isinstance(curr, tuple):
            for lt in _single_rewrites(curr[1], rules):
                new_term = ('*', lt, curr[2])
                if new_term not in visited:
                    visited.add(new_term)
                    queue.append(new_term)
            for rt in _single_rewrites(curr[2], rules):
                new_term = ('*', curr[1], rt)
                if new_term not in visited:
                    visited.add(new_term)
                    queue.append(new_term)
    return visited


def _single_rewrites(term, rules):
    """Get single-step rewrites of a term."""
    res = set()
    for rl, rr in rules:
        m = {}
        if match(rl, term, m):
            res.add(substitute(rr, m))
    if isinstance(term, tuple):
        for lt in _single_rewrites(term[1], rules):
            res.add(('*', lt, term[2]))
        for rt in _single_rewrites(term[2], rules):
            res.add(('*', term[1], rt))
    return res


def can_prove_by_rewriting(eq1, eq2, max_steps=500) -> bool:
    """Check if eq1 implies eq2 by BFS rewriting."""
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    rules = [(lhs1, rhs1), (rhs1, lhs1)]
    reachable_from_lhs2 = get_rewrites(lhs2, rules, limit=max_steps)
    reachable_from_rhs2 = get_rewrites(rhs2, rules, limit=max_steps)
    return not reachable_from_lhs2.isdisjoint(reachable_from_rhs2)


def check_magma(eq, table: list) -> bool:
    """Check if a magma (given as multiplication table) satisfies an equation."""
    lhs, rhs = eq
    vars_list = sorted(get_vars(lhs) | get_vars(rhs))
    n = len(table)
    n_vars = len(vars_list)

    def ev(t, env):
        if isinstance(t, str):
            return env[t]
        return table[ev(t[1], env)][ev(t[2], env)]

    if n_vars == 0:
        return ev(lhs, {}) == ev(rhs, {})

    limit = min(n ** n_vars, 1024)
    if n ** n_vars <= limit:
        for vals in itertools.product(range(n), repeat=n_vars):
            env = dict(zip(vars_list, vals))
            if ev(lhs, env) != ev(rhs, env):
                return False
    else:
        rng = random.Random(42)
        for _ in range(limit):
            vals = [rng.randint(0, n - 1) for _ in range(n_vars)]
            env = dict(zip(vars_list, vals))
            if ev(lhs, env) != ev(rhs, env):
                return False
    return True


def find_counterexample(eq1, eq2, magma_sizes=(2, 3, 4)) -> Optional[list]:
    """Try to find a magma satisfying eq1 but not eq2."""
    for sz in magma_sizes:
        # Try all size-2 magmas exhaustively
        if sz == 2:
            for vals in itertools.product(range(sz), repeat=sz * sz):
                table = [list(vals[i * sz:(i + 1) * sz]) for i in range(sz)]
                if check_magma(eq1, table) and not check_magma(eq2, table):
                    return table
        else:
            # Random search for larger sizes
            rng = random.Random(42)
            for _ in range(500):
                table = [[rng.randint(0, sz - 1) for _ in range(sz)] for _ in range(sz)]
                if check_magma(eq1, table) and not check_magma(eq2, table):
                    return table
    return None


def analyze_equation(eq_str: str) -> dict:
    """Extract structural features from an equation string."""
    eq = parse_equation(eq_str)
    lhs, rhs = eq
    vars_l = get_vars(lhs)
    vars_r = get_vars(rhs)
    all_vars = vars_l | vars_r

    return {
        'equation': eq_str,
        'parsed': eq,
        'vars_lhs': vars_l,
        'vars_rhs': vars_r,
        'all_vars': all_vars,
        'num_vars': len(all_vars),
        'ops_lhs': count_ops(lhs),
        'ops_rhs': count_ops(rhs),
        'depth_lhs': get_depth(lhs),
        'depth_rhs': get_depth(rhs),
        'size_lhs': term_size(lhs),
        'size_rhs': term_size(rhs),
        'is_identity': lhs == rhs,
        'lhs_is_var': isinstance(lhs, str),
        'rhs_is_var': isinstance(rhs, str),
        'vars_balanced': vars_l == vars_r,
    }


# Well-known equation patterns
PATTERNS = {
    'associative': (('*', ('*', 'a', 'b'), 'c'), ('*', 'a', ('*', 'b', 'c'))),
    'commutative': (('*', 'a', 'b'), ('*', 'b', 'a')),
    'idempotent': (('*', 'a', 'a'), 'a'),
    'left_projection': (('*', 'a', 'b'), 'a'),
    'right_projection': (('*', 'a', 'b'), 'b'),
    'constant': (('*', 'a', 'b'), ('*', 'c', 'd')),
    'left_distributive': (('*', 'a', ('*', 'b', 'c')), ('*', ('*', 'a', 'b'), ('*', 'a', 'c'))),
    'right_distributive': (('*', ('*', 'a', 'b'), 'c'), ('*', ('*', 'a', 'c'), ('*', 'b', 'c'))),
}


def matches_pattern(eq, pattern_name: str) -> bool:
    """Check if an equation matches a well-known pattern."""
    if pattern_name not in PATTERNS:
        return False
    p = PATTERNS[pattern_name]
    lhs, rhs = eq
    m = {}
    if match(p[0], lhs, m) and match(p[1], rhs, m):
        return True
    m = {}
    if match(p[1], lhs, m) and match(p[0], rhs, m):
        return True
    return False


def load_equations(filepath: str = 'equations.txt') -> list:
    """Load equations from file. Line number (1-indexed) = equation number."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == '__main__':
    eqs = load_equations()
    print(f"Loaded {len(eqs)} equations")

    # Show some examples
    for i, eq_str in enumerate([eqs[0], eqs[1], eqs[2], eqs[3], eqs[42]], start=1):
        info = analyze_equation(eq_str)
        print(f"\nEquation {i}: {eq_str}")
        for k, v in info.items():
            if k not in ('equation', 'parsed'):
                print(f"  {k}: {v}")
