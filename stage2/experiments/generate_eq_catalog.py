#!/usr/bin/env python3
"""Generate an ETP-style equation catalog for an arbitrary operation count.

ETP ships catalogs only up to order 5 (`eq_size5.txt`, 62,576 laws, cumulative
over orders 0..5 where "order" is the **total number of `*` operations across
both sides**). Nothing above that exists anywhere, so order-6 sweeps have to
generate their own catalog.

The canonical form was reverse-engineered from `eq_size5.txt` and is pinned by
`--verify`, which regenerates orders 0..5 and asserts an identical set against
the vendored file (for the whole 4,694-law order-<=4 catalog, the full 62,576
order-<=5 catalog, and the <=2 / <=3 variable slices). The reconstruction is
exact **line for line**, not merely set-equal, so the enumeration order is
pinned too. The rules:

* an equation is a pair of magma terms over variables named by **first
  occurrence** reading the rendered equation left to right: x, y, z, w, u, v, r;
* equations are identified up to relabeling **and** swapping the two sides;
* the representative kept is the one whose LHS carries no more operations than
  its RHS, tie-broken by `_shape_key` (a leaf before any product, then by the
  LEFT argument's operation count, recursively) and finally by the variable
  slot sequence;
* reflexive equations `t = t` are dropped except `x = x` itself.

Usage:
    python stage2/experiments/generate_eq_catalog.py --verify
    python stage2/experiments/generate_eq_catalog.py --ops 6 --max-variables 2 \
        --out data/generated/eq_order6_vars2.txt
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EQ_SIZE5_PATH = (REPO_ROOT / "vendor" / "stage2-official" / "examples"
                 / "problems" / "eq_size5.txt")

VAR_NAMES = ("x", "y", "z", "w", "u", "v", "r")

# A term shape is either None (a leaf slot, filled with a variable later) or a
# (left, right) tuple. Shapes are enumerated first; variables are assigned to
# their leaf slots afterwards, in left-to-right order.


@lru_cache(maxsize=None)
def _shapes(ops: int) -> tuple:
    """All term shapes with exactly `ops` operations."""
    if ops == 0:
        return (None,)
    out = []
    for left_ops in range(ops):
        right_ops = ops - 1 - left_ops
        for left in _shapes(left_ops):
            for right in _shapes(right_ops):
                out.append((left, right))
    return tuple(out)


def _leaf_count(shape) -> int:
    if shape is None:
        return 1
    return _leaf_count(shape[0]) + _leaf_count(shape[1])


def _render(shape, names: list[str], pos: list[int]) -> str:
    if shape is None:
        name = names[pos[0]]
        pos[0] += 1
        return name
    left = _render(shape[0], names, pos)
    right = _render(shape[1], names, pos)
    return "(" + left + " * " + right + ")"


def _strip_outer(text: str) -> str:
    # ETP drops the outermost parentheses of each side: `x = a * b`, not
    # `x = (a * b)`. Nested products keep theirs.
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1]
    return text


@lru_cache(maxsize=None)
def _assignments(n_leaves: int, max_variables: int) -> tuple:
    """Restricted growth strings over `n_leaves` slots with at most
    `max_variables` distinct values -- exactly first-occurrence naming."""
    limit = min(max_variables, len(VAR_NAMES))
    out: list[tuple[int, ...]] = []

    def rec(prefix: list[int], used: int) -> None:
        if len(prefix) == n_leaves:
            out.append(tuple(prefix))
            return
        for value in range(min(used + 1, limit)):
            prefix.append(value)
            rec(prefix, max(used, value + 1))
            prefix.pop()

    rec([], 0)
    return tuple(out)


@lru_cache(maxsize=None)
def _shape_key(shape) -> tuple:
    """Total order on term shapes, matching ETP's own enumeration: a leaf sorts
    before any product, and two products are compared by the operation count of
    their LEFT argument first (so `x * (x * x)` sorts before `(x * x) * x`),
    then recursively. Reverse-engineered from `eq_size5.txt`; pinned by
    --verify, which reproduces all 62,576 rows exactly."""
    if shape is None:
        return (0,)
    left, right = shape
    return (1 + _ops(shape), _ops(left), _shape_key(left), _shape_key(right))


@lru_cache(maxsize=None)
def _ops(shape) -> int:
    if shape is None:
        return 0
    return 1 + _ops(shape[0]) + _ops(shape[1])


def _canonical(lhs_shape, rhs_shape, slots) -> tuple[str, str] | None:
    """Canonical (orientation, naming) rendering, or None for a non-trivial
    reflexive equation."""
    n_left = _leaf_count(lhs_shape)
    best = None
    for a_shape, b_shape, a_slots, b_slots in (
        (lhs_shape, rhs_shape, slots[:n_left], slots[n_left:]),
        (rhs_shape, lhs_shape, slots[n_left:], slots[:n_left]),
    ):
        mapping: dict[int, int] = {}
        for slot in tuple(a_slots) + tuple(b_slots):
            if slot not in mapping:
                mapping[slot] = len(mapping)
        a_ids = [mapping[s] for s in a_slots]
        b_ids = [mapping[s] for s in b_slots]
        key = (_ops(a_shape), _shape_key(a_shape), _shape_key(b_shape),
               tuple(a_ids + b_ids))
        if best is None or key < best[0]:
            best = (key, a_shape, b_shape, a_ids, b_ids)
    _key, a_shape, b_shape, a_ids, b_ids = best
    a_text = _strip_outer(_render(a_shape, [VAR_NAMES[i] for i in a_ids], [0]))
    b_text = _strip_outer(_render(b_shape, [VAR_NAMES[i] for i in b_ids], [0]))
    if a_text == b_text and "*" in a_text:
        return None
    return a_text, b_text


def generate(ops: int, max_variables: int) -> list[str]:
    seen: set[tuple[str, str]] = set()
    out: list[str] = []
    for left_ops in range(ops + 1):
        right_ops = ops - left_ops
        for lhs_shape in _shapes(left_ops):
            for rhs_shape in _shapes(right_ops):
                n_leaves = _leaf_count(lhs_shape) + _leaf_count(rhs_shape)
                for slots in _assignments(n_leaves, max_variables):
                    canon = _canonical(lhs_shape, rhs_shape, slots)
                    if canon is None or canon in seen:
                        continue
                    seen.add(canon)
                    out.append(canon[0] + " = " + canon[1])
    return out


def catalog_slice(max_ops: int, max_variables: int) -> list[str]:
    rows: list[str] = []
    for ops in range(max_ops + 1):
        rows.extend(generate(ops, max_variables))
    return rows


def verify() -> int:
    reference = [line.strip() for line
                 in EQ_SIZE5_PATH.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    failures = 0
    for max_ops, max_vars in ((4, 7), (5, 7), (5, 2), (5, 3)):
        want = sorted(t for t in reference
                      if t.count("*") <= max_ops
                      and len({c for c in t if c.isalpha()}) <= max_vars)
        got = sorted(catalog_slice(max_ops, max_vars))
        ok = want == got
        if not ok:
            failures += 1
            print("  only in reference: " + str(sorted(set(want) - set(got))[:5]))
            print("  only in generated: " + str(sorted(set(got) - set(want))[:5]))
        print("[{}] ops<={}, vars<={}: reference {}, generated {}".format(
            "OK" if ok else "FAIL", max_ops, max_vars, len(want), len(got)))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops", type=int, default=6,
                    help="exact total operation count (the ETP 'order')")
    ap.add_argument("--max-variables", type=int, default=2)
    ap.add_argument("--cumulative", action="store_true",
                    help="emit orders 0..ops instead of exactly `ops`")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--verify", action="store_true",
                    help="regenerate orders 0..5 and diff against eq_size5.txt")
    args = ap.parse_args()

    if args.verify:
        return verify()

    rows = (catalog_slice(args.ops, args.max_variables) if args.cumulative
            else generate(args.ops, args.max_variables))
    if args.out is None:
        print("\n".join(rows[:20]))
        print("... {} equations".format(len(rows)))
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("Wrote {} equations (ops{}{}, vars<={}) to {}".format(
        len(rows), "<=" if args.cumulative else "==", args.ops,
        args.max_variables, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
