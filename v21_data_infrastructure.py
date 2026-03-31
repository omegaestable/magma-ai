#!/usr/bin/env python3
"""
v21_data_infrastructure.py — Phase 1 data infrastructure for the v21 cheatsheet.

Builds:
  1. Equation text ↔ ID mapper (equations.txt → bidirectional map)
  2. Witness pre-evaluator (all 4694 eqs × 11 witnesses → bitmasks)
  3. Implications CSV parser (dense matrix → (row, col) → TRUE/FALSE)
  4. Benchmark coverage analysis (maps every benchmark pair to IDs + ground truth)
  5. Witness separation analysis for FALSE pairs

Run:
    python v21_data_infrastructure.py
"""
from __future__ import annotations

import csv
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
EQUATIONS_FILE = ROOT / "data" / "exports" / "equations.txt"
CSV_FILE = ROOT / "data" / "exports" / "export_raw_implications_14_3_2026.csv"
BENCHMARK_DIR = ROOT / "data" / "benchmark"

# ---------------------------------------------------------------------------
# Witness library (identical to sim_lab.py EXTENDED_WITNESS_LIBRARY)
# ---------------------------------------------------------------------------
WITNESSES = [
    {"name": "LP",   "table": [[0, 0], [1, 1]]},
    {"name": "RP",   "table": [[0, 1], [0, 1]]},
    {"name": "C0",   "table": [[0, 0], [0, 0]]},
    {"name": "XOR",  "table": [[0, 1], [1, 0]]},
    {"name": "Z3A",  "table": [[0, 1, 2], [1, 2, 0], [2, 0, 1]]},
    {"name": "AND",  "table": [[0, 0], [0, 1]]},
    {"name": "OR",   "table": [[0, 1], [1, 1]]},
    {"name": "XNOR", "table": [[1, 0], [0, 1]]},
    {"name": "A2",   "table": [[0, 0], [1, 0]]},
    {"name": "T3L",  "table": [[0, 0, 0], [0, 0, 0], [0, 1, 0]]},
    {"name": "T3R",  "table": [[0, 0, 0], [0, 0, 0], [0, 0, 1]]},
]
WITNESS_NAMES = [w["name"] for w in WITNESSES]


# ---------------------------------------------------------------------------
# Equation parser (self-contained, mirrors distill.py)
# ---------------------------------------------------------------------------
def _find_matching(expr: str, start: int) -> int:
    depth = 0
    for i in range(start, len(expr)):
        if expr[i] == '(':
            depth += 1
        elif expr[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1


def _parse_expr(expr: str):
    expr = expr.strip()
    if expr.startswith('(') and _find_matching(expr, 0) == len(expr) - 1:
        expr = expr[1:-1].strip()
    depth = 0
    last_star = -1
    for i, ch in enumerate(expr):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == '*' and depth == 0:
            last_star = i
    if last_star >= 0:
        return ('*', _parse_expr(expr[:last_star].strip()),
                      _parse_expr(expr[last_star + 1:].strip()))
    return ('var', expr)


def _collect_vars(tree, out: set):
    if tree[0] == 'var':
        out.add(tree[1])
    else:
        _collect_vars(tree[1], out)
        _collect_vars(tree[2], out)


def _eval(tree, assign: dict, table: list):
    if tree[0] == 'var':
        return assign[tree[1]]
    return table[_eval(tree[1], assign, table)][_eval(tree[2], assign, table)]


def normalize_eq(eq: str) -> str:
    """Canonical form: ◇ → *, strip whitespace."""
    return eq.replace('\u25c7', '*').strip()


def check_equation(eq: str, table: list) -> bool:
    """Does `eq` hold for ALL assignments on `table`?"""
    norm = normalize_eq(eq)
    lhs_str, _, rhs_str = norm.partition(' = ')
    lhs, rhs = _parse_expr(lhs_str), _parse_expr(rhs_str)
    variables: set = set()
    _collect_vars(lhs, variables)
    _collect_vars(rhs, variables)
    ordered = sorted(variables)
    n = len(table)
    for vals in itertools.product(range(n), repeat=len(ordered)):
        assign = dict(zip(ordered, vals))
        if _eval(lhs, assign, table) != _eval(rhs, assign, table):
            return False
    return True


def first_failing_assignment(eq: str, table: list) -> dict | None:
    """Return first failing assignment, or None if eq holds everywhere."""
    norm = normalize_eq(eq)
    lhs_str, _, rhs_str = norm.partition(' = ')
    lhs, rhs = _parse_expr(lhs_str), _parse_expr(rhs_str)
    variables: set = set()
    _collect_vars(lhs, variables)
    _collect_vars(rhs, variables)
    ordered = sorted(variables)
    n = len(table)
    for vals in itertools.product(range(n), repeat=len(ordered)):
        assign = dict(zip(ordered, vals))
        lv = _eval(lhs, assign, table)
        rv = _eval(rhs, assign, table)
        if lv != rv:
            return {"assignment": assign, "lhs": lv, "rhs": rv}
    return None


# ---------------------------------------------------------------------------
# Step 1: Equation text ↔ ID mapper
# ---------------------------------------------------------------------------
def load_equations() -> list[str]:
    """Load equations.txt. Returns list[eq_text] indexed by 0-based ID."""
    lines = EQUATIONS_FILE.read_text(encoding="utf-8").splitlines()
    return [normalize_eq(line) for line in lines if line.strip()]


def build_equation_map(equations: list[str]) -> dict[str, int]:
    """Map normalized equation text → 0-based equation ID."""
    return {eq: i for i, eq in enumerate(equations)}


# ---------------------------------------------------------------------------
# Step 2: Witness pre-evaluator
# ---------------------------------------------------------------------------
def compute_witness_masks(equations: list[str]) -> list[int]:
    """For each equation, compute an 11-bit mask: bit i is set if witness i satisfies eq."""
    masks = []
    total = len(equations)
    for idx, eq in enumerate(equations):
        mask = 0
        for w_idx, w in enumerate(WITNESSES):
            if check_equation(eq, w["table"]):
                mask |= (1 << w_idx)
        masks.append(mask)
        if (idx + 1) % 500 == 0:
            print(f"  Witness masks: {idx + 1}/{total}")
    return masks


def mask_to_str(mask: int) -> str:
    """Convert 11-bit mask to 'YNNYNNYNNYY' string (one char per witness)."""
    return ''.join('Y' if mask & (1 << i) else 'N' for i in range(len(WITNESSES)))


# ---------------------------------------------------------------------------
# Step 3: Parse implications CSV
# ---------------------------------------------------------------------------
def load_implications_csv() -> list[list[int]]:
    """Load dense matrix. Returns matrix[row][col] with values 3,4,-3,-4.
    Row i = Equation (i+1), Col j = Equation (j+1).
    Positive (3 or 4) = TRUE, negative (-3 or -4) = FALSE.
    Note: The CSV rows correspond to Equation 1 through Equation 4694 (1-indexed).
    """
    matrix = []
    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            matrix.append([int(v) for v in row])
    return matrix


def implication_answer(matrix: list[list[int]], eq1_id: int, eq2_id: int) -> bool | None:
    """Look up whether eq1 → eq2. IDs are 0-based. Returns True/False or None if out of range."""
    if eq1_id < 0 or eq1_id >= len(matrix) or eq2_id < 0 or eq2_id >= len(matrix[0]):
        return None
    val = matrix[eq1_id][eq2_id]
    return val > 0


# ---------------------------------------------------------------------------
# Step 4: Benchmark mapping
# ---------------------------------------------------------------------------
def load_all_benchmarks() -> list[dict]:
    """Load all benchmark JSONL files, return flat list of problems."""
    problems = []
    for path in sorted(BENCHMARK_DIR.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                obj["_benchmark_file"] = path.name
                problems.append(obj)
    return problems


def map_benchmark_to_ids(
    problems: list[dict],
    eq_map: dict[str, int],
) -> tuple[list[dict], list[dict]]:
    """Annotate each benchmark problem with equation IDs.
    Returns (mapped_problems, unmapped_problems).
    """
    mapped, unmapped = [], []
    for p in problems:
        eq1_norm = normalize_eq(p["equation1"])
        eq2_norm = normalize_eq(p["equation2"])
        id1 = eq_map.get(eq1_norm)
        id2 = eq_map.get(eq2_norm)
        rec = dict(p, eq1_id=id1, eq2_id=id2, eq1_norm=eq1_norm, eq2_norm=eq2_norm)
        if id1 is not None and id2 is not None:
            mapped.append(rec)
        else:
            unmapped.append(rec)
    return mapped, unmapped


# ---------------------------------------------------------------------------
# Step 5: Witness separation analysis
# ---------------------------------------------------------------------------
def witness_separates(masks: list[int], eq1_id: int, eq2_id: int) -> list[str]:
    """Return list of witness names that satisfy E1 but NOT E2."""
    m1, m2 = masks[eq1_id], masks[eq2_id]
    separating = m1 & ~m2
    return [WITNESS_NAMES[i] for i in range(len(WITNESSES)) if separating & (1 << i)]


# ===========================================================================
# Main pipeline
# ===========================================================================
def main():
    print("=" * 72)
    print("v21 Data Infrastructure — Phase 1")
    print("=" * 72)

    # Step 1: Load equations
    print("\n[Step 1] Loading equations.txt ...")
    equations = load_equations()
    eq_map = build_equation_map(equations)
    print(f"  Loaded {len(equations)} equations")
    # Verify no duplicates
    if len(eq_map) != len(equations):
        dupes = len(equations) - len(eq_map)
        print(f"  WARNING: {dupes} duplicate equations after normalization")
    # Sample
    for i in [0, 1, 2, 42, 4693]:
        if i < len(equations):
            print(f"  Eq{i}: {equations[i]}")

    # Step 2: Witness pre-evaluation
    print("\n[Step 2] Computing witness masks for all equations ...")
    masks = compute_witness_masks(equations)
    # Summary stats
    pop_counts = Counter(bin(m).count('1') for m in masks)
    print(f"  Witness mask popcount distribution:")
    for k in sorted(pop_counts):
        print(f"    {k} witnesses satisfy: {pop_counts[k]} equations")
    # How many equations satisfy zero witnesses? (these are "exotic")
    exotic = sum(1 for m in masks if m == 0)
    print(f"  Exotic (0 witnesses): {exotic}")

    # Step 3: Parse CSV
    print("\n[Step 3] Loading implications CSV ...")
    matrix = load_implications_csv()
    print(f"  Matrix size: {len(matrix)} rows × {len(matrix[0]) if matrix else 0} cols")
    # Verify dimensions
    if len(matrix) != len(equations):
        print(f"  WARNING: Matrix rows ({len(matrix)}) != equations count ({len(equations)})")
    # Count TRUE/FALSE
    true_count = sum(1 for row in matrix for v in row if v > 0)
    false_count = sum(1 for row in matrix for v in row if v < 0)
    total = true_count + false_count
    print(f"  TRUE: {true_count} ({100*true_count/total:.1f}%)")
    print(f"  FALSE: {false_count} ({100*false_count/total:.1f}%)")

    # Step 4: Benchmark mapping
    print("\n[Step 4] Mapping benchmark problems to equation IDs ...")
    all_problems = load_all_benchmarks()
    print(f"  Loaded {len(all_problems)} total problems from {len(set(p['_benchmark_file'] for p in all_problems))} files")
    mapped, unmapped = map_benchmark_to_ids(all_problems, eq_map)
    print(f"  Mapped: {len(mapped)}, Unmapped: {len(unmapped)}")
    if unmapped:
        print(f"  WARNING: {len(unmapped)} problems could not be mapped!")
        for u in unmapped[:5]:
            print(f"    {u['id']}: E1='{u['eq1_norm']}' E2='{u['eq2_norm']}'")

    # Verify ground truth matches
    match_count, mismatch_count, no_lookup = 0, 0, 0
    for p in mapped:
        gt = implication_answer(matrix, p["eq1_id"], p["eq2_id"])
        if gt is None:
            no_lookup += 1
        elif gt == p["answer"]:
            match_count += 1
        else:
            mismatch_count += 1
    print(f"  Ground truth verification: {match_count} match, {mismatch_count} mismatch, {no_lookup} no-lookup")
    if mismatch_count > 0:
        print("  WARNING: Ground truth mismatches detected!")

    # Count unique equations in benchmarks
    unique_eq_ids = set()
    for p in mapped:
        unique_eq_ids.add(p["eq1_id"])
        unique_eq_ids.add(p["eq2_id"])
    print(f"  Unique equations in benchmarks: {len(unique_eq_ids)}")

    # Step 5: Witness separation analysis
    print("\n[Step 5] Witness separation analysis on benchmark FALSE pairs ...")
    false_pairs = [p for p in mapped if p["answer"] is False]
    true_pairs = [p for p in mapped if p["answer"] is True]
    print(f"  FALSE pairs: {len(false_pairs)}, TRUE pairs: {len(true_pairs)}")

    covered_by_witness = 0
    uncovered_false = []
    witness_usage = Counter()
    for p in false_pairs:
        seps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
        if seps:
            covered_by_witness += 1
            for s in seps:
                witness_usage[s] += 1
        else:
            uncovered_false.append(p)

    coverage_pct = 100 * covered_by_witness / len(false_pairs) if false_pairs else 0
    print(f"  Witness coverage of FALSE pairs: {covered_by_witness}/{len(false_pairs)} ({coverage_pct:.1f}%)")
    print(f"  Uncovered FALSE pairs: {len(uncovered_false)}")
    if uncovered_false:
        for u in uncovered_false[:10]:
            print(f"    {u['id']}: E1_id={u['eq1_id']}, E2_id={u['eq2_id']}")
            print(f"      E1={u['eq1_norm']}")
            print(f"      E2={u['eq2_norm']}")
            print(f"      E1 mask={mask_to_str(masks[u['eq1_id']])}, E2 mask={mask_to_str(masks[u['eq2_id']])}")
    print(f"  Witness usage in separating FALSE pairs:")
    for name, count in witness_usage.most_common():
        print(f"    {name}: {count}")

    # Step 6: Cheatsheet sizing analysis
    print("\n[Step 6] Cheatsheet sizing analysis ...")
    unique_ids_sorted = sorted(unique_eq_ids)
    # How many bytes for a compact witness table?
    # Format: "EqID:MASK\n" where ID is 1-indexed, MASK is 11 chars
    sample_lines = []
    for eid in unique_ids_sorted[:5]:
        line = f"{eid}:{mask_to_str(masks[eid])}"
        sample_lines.append(line)
    entry_size = max(len(l) for l in sample_lines) + 1  # +1 for newline
    total_table_bytes = sum(len(f"{eid}:{mask_to_str(masks[eid])}") + 1 for eid in unique_ids_sorted)
    print(f"  Unique equations: {len(unique_ids_sorted)}")
    print(f"  Witness table size (all benchmark eqs): {total_table_bytes} bytes")
    print(f"  Budget remaining for instructions: {10240 - total_table_bytes} bytes")
    print(f"  Sample entries:")
    for l in sample_lines:
        print(f"    {l}")

    # Phase 2 preview: per-benchmark breakdown
    print("\n[Bonus] Per-benchmark accuracy breakdown ...")
    by_file = defaultdict(lambda: {"total": 0, "false": 0, "witness_covered": 0, "true": 0})
    for p in mapped:
        bf = p["_benchmark_file"]
        by_file[bf]["total"] += 1
        if p["answer"] is True:
            by_file[bf]["true"] += 1
        else:
            by_file[bf]["false"] += 1
            seps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
            if seps:
                by_file[bf]["witness_covered"] += 1
    for bf in sorted(by_file):
        d = by_file[bf]
        cov = 100 * d["witness_covered"] / d["false"] if d["false"] > 0 else 100.0
        print(f"  {bf}: {d['total']} problems, TRUE={d['true']}, FALSE={d['false']}, witness_coverage={cov:.0f}%")

    # Save analysis artifact
    artifact_path = ROOT / "data" / "exports" / "v21_analysis.json"
    artifact = {
        "equation_count": len(equations),
        "unique_benchmark_equations": len(unique_eq_ids),
        "unique_benchmark_equation_ids": unique_ids_sorted,
        "witness_masks": {eid: mask_to_str(masks[eid]) for eid in unique_ids_sorted},
        "false_pair_witness_coverage": coverage_pct,
        "uncovered_false_count": len(uncovered_false),
        "uncovered_false_pairs": [
            {"id": u["id"], "eq1_id": u["eq1_id"], "eq2_id": u["eq2_id"]}
            for u in uncovered_false
        ],
        "witness_table_bytes": total_table_bytes,
    }
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\n  Analysis artifact saved to {artifact_path}")

    print("\n" + "=" * 72)
    print("Phase 1 complete.")
    print("=" * 72)


if __name__ == "__main__":
    main()
