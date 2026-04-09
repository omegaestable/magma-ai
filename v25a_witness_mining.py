#!/usr/bin/env python3
"""
v25a_witness_mining.py — Deep witness analysis for v25a cheatsheet design.

Goals:
1. Map every hard3 FALSE problem to equation IDs
2. Check which of the 11 existing witnesses separate each FALSE pair
3. Find the coverage gap — which FALSE pairs have NO witness separator
4. Mine new small magmas (size 2 and 3) that fill gaps
5. Rank witnesses by coverage to pick the best ones for cheatsheet inclusion
6. Also analyze normal FALSE pairs for safety
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v21_data_infrastructure import (
    load_equations, build_equation_map, load_implications_csv,
    implication_answer, compute_witness_masks, witness_separates,
    check_equation, normalize_eq, WITNESSES, WITNESS_NAMES,
    first_failing_assignment
)

ROOT = Path(__file__).resolve().parent

# ── Load all hard3 and normal problems from fresh rotation 0003 ──
def load_benchmark(path):
    problems = []
    with open(path) as f:
        for line in f:
            problems.append(json.loads(line))
    return problems

def find_latest_benchmark(pattern):
    """Find the latest benchmark file matching a pattern."""
    candidates = sorted(ROOT.glob(f"data/benchmark/{pattern}"))
    return candidates[-1] if candidates else None

def analyze_coverage():
    print("=" * 72)
    print("v25a Witness Mining & Coverage Analysis")
    print("=" * 72)

    # Load infrastructure
    print("\n[1] Loading equations & matrix...")
    equations = load_equations()
    eq_map = build_equation_map(equations)
    matrix = load_implications_csv()
    print(f"  {len(equations)} equations, {len(matrix)}x{len(matrix[0])} matrix")

    print("\n[2] Computing witness masks (this takes ~60s)...")
    masks = compute_witness_masks(equations)
    print(f"  Done. {len(masks)} masks computed.")

    # Load benchmarks
    hard3_file = find_latest_benchmark("hard3_balanced*rotation0003*.jsonl")
    normal_file = find_latest_benchmark("normal_balanced*rotation0003*.jsonl")

    if not hard3_file or not normal_file:
        # Fallback to any hard3/normal
        hard3_file = find_latest_benchmark("hard3_balanced*.jsonl")
        normal_file = find_latest_benchmark("normal_balanced60*.jsonl")

    print(f"\n[3] Loading benchmarks...")
    print(f"  Hard3: {hard3_file.name if hard3_file else 'NOT FOUND'}")
    print(f"  Normal: {normal_file.name if normal_file else 'NOT FOUND'}")

    hard3_problems = load_benchmark(hard3_file) if hard3_file else []
    normal_problems = load_benchmark(normal_file) if normal_file else []

    # Map to equation IDs
    def map_problems(problems):
        mapped = []
        for p in problems:
            eq1 = normalize_eq(p["equation1"])
            eq2 = normalize_eq(p["equation2"])
            id1 = eq_map.get(eq1)
            id2 = eq_map.get(eq2)
            if id1 is not None and id2 is not None:
                p["eq1_id"] = id1
                p["eq2_id"] = id2
                mapped.append(p)
            else:
                print(f"  WARNING: Cannot map {p['id']}: eq1={'FOUND' if id1 is not None else 'MISSING'} eq2={'FOUND' if id2 is not None else 'MISSING'}")
        return mapped

    hard3_mapped = map_problems(hard3_problems)
    normal_mapped = map_problems(normal_problems)

    # ── Analyze hard3 FALSE pairs ──
    print(f"\n{'='*72}")
    print("HARD3 FALSE PAIR ANALYSIS")
    print(f"{'='*72}")

    hard3_false = [p for p in hard3_mapped if p["answer"] == False]
    hard3_true = [p for p in hard3_mapped if p["answer"] == True]
    print(f"\n  Total hard3 problems: {len(hard3_mapped)} (TRUE:{len(hard3_true)} FALSE:{len(hard3_false)})")

    # Check witness coverage for each FALSE pair
    covered = []
    uncovered = []
    witness_usage = Counter()

    for p in hard3_false:
        seps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
        p["separators"] = seps
        if seps:
            covered.append(p)
            for s in seps:
                witness_usage[s] += 1
        else:
            uncovered.append(p)

    print(f"\n  Witness coverage: {len(covered)}/{len(hard3_false)} ({100*len(covered)/len(hard3_false):.1f}%)")
    print(f"  Uncovered (deep gap): {len(uncovered)}/{len(hard3_false)}")

    print(f"\n  Witness usage on hard3 FALSE (existing 11 witnesses):")
    for w, count in witness_usage.most_common():
        print(f"    {w}: separates {count}/{len(hard3_false)} ({100*count/len(hard3_false):.1f}%)")

    # Which specific witnesses separate each covered pair?
    print(f"\n  Per-pair separation detail (COVERED):")
    for p in sorted(covered, key=lambda x: x["id"]):
        print(f"    {p['id']}: E1={p['equation1'][:40]:40s} -> E2={p['equation2'][:40]:40s} | sep={','.join(p['separators'])}")

    print(f"\n  Per-pair detail (UNCOVERED - deep gap):")
    for p in sorted(uncovered, key=lambda x: x["id"]):
        print(f"    {p['id']}: E1={p['equation1'][:50]:50s} -> E2={p['equation2'][:50]:50s}")

    # ── Check which witnesses v24j cheatsheet actually uses ──
    # v24j uses: LP, RP, C0, VARS (structural) + T3R (rescue)
    v24j_witnesses = {"LP", "RP", "C0", "AND", "T3R"}  # AND = VARS test
    v24j_covered = 0
    v24j_uncovered_but_coverable = []

    for p in hard3_false:
        seps = set(p.get("separators", []))
        if seps & v24j_witnesses:
            v24j_covered += 1
        elif seps:
            v24j_uncovered_but_coverable.append((p, list(seps)))

    print(f"\n  v24j effective coverage (LP/RP/C0/AND/T3R): {v24j_covered}/{len(hard3_false)} ({100*v24j_covered/len(hard3_false):.1f}%)")
    print(f"  Coverable by adding more witnesses: {len(v24j_uncovered_but_coverable)}")
    for p, seps in v24j_uncovered_but_coverable:
        print(f"    {p['id']}: needs {','.join(seps)}")

    # ── Now analyze normal FALSE for safety ──
    print(f"\n{'='*72}")
    print("NORMAL FALSE PAIR ANALYSIS")
    print(f"{'='*72}")

    normal_false = [p for p in normal_mapped if p["answer"] == False]
    print(f"  Normal FALSE pairs: {len(normal_false)}")

    normal_covered = 0
    normal_v24j_covered = 0
    normal_witness_usage = Counter()

    for p in normal_false:
        seps = witness_separates(masks, p["eq1_id"], p["eq2_id"])
        p["separators"] = seps
        if seps:
            normal_covered += 1
            for s in seps:
                normal_witness_usage[s] += 1
        if set(seps) & v24j_witnesses:
            normal_v24j_covered += 1

    print(f"  Any-witness coverage: {normal_covered}/{len(normal_false)} ({100*normal_covered/len(normal_false):.1f}%)")
    print(f"  v24j coverage: {normal_v24j_covered}/{len(normal_false)} ({100*normal_v24j_covered/len(normal_false):.1f}%)")

    # ── MINE NEW WITNESSES ──
    # Try all 2-element magmas (16 total) and 3-element magmas (19683 total)
    print(f"\n{'='*72}")
    print("MINING NEW WITNESSES (size 2 & 3)")
    print(f"{'='*72}")

    # Collect unique equations from the gap
    gap_eq_ids = set()
    for p in uncovered:
        gap_eq_ids.add(p["eq1_id"])
        gap_eq_ids.add(p["eq2_id"])

    # Also collect equations from v24j-uncovered-but-coverable
    v24j_gap_pairs = uncovered + [p for p, _ in v24j_uncovered_but_coverable]

    print(f"\n  Gap pairs to solve: {len(v24j_gap_pairs)}")

    # Mine size-2 magmas
    print(f"\n  Mining all 2-element magmas (16 total)...")
    best_size2 = mine_magmas(2, v24j_gap_pairs, equations, masks)

    # Mine size-3 magmas (19683 = 3^9)
    print(f"\n  Mining all 3-element magmas (19683 total)...")
    best_size3 = mine_magmas(3, v24j_gap_pairs, equations, masks)

    # Combine and rank
    all_candidates = best_size2 + best_size3
    all_candidates.sort(key=lambda x: -x["new_coverage"])

    print(f"\n  TOP 20 NEW WITNESS CANDIDATES:")
    print(f"  {'Rank':>4} {'Size':>4} {'NewCov':>6} {'Table':>30} {'Separates':>40}")
    for i, c in enumerate(all_candidates[:20]):
        pairs_str = ",".join(c["separates_ids"][:5])
        if len(c["separates_ids"]) > 5:
            pairs_str += f"...+{len(c['separates_ids'])-5}"
        print(f"  {i+1:4d} {c['size']:4d} {c['new_coverage']:6d} {str(c['table']):>30} {pairs_str:>40}")

    # ── GREEDY SET COVER ──
    print(f"\n{'='*72}")
    print("GREEDY WITNESS SET COVER")
    print(f"{'='*72}")

    # Start with v24j witnesses, greedily add best new witness
    remaining = set(p["id"] for p in v24j_gap_pairs)
    selected = []

    for round_i in range(5):
        if not remaining:
            break
        best = None
        best_count = 0
        for c in all_candidates:
            hits = remaining & set(c["separates_ids"])
            if len(hits) > best_count:
                best_count = len(hits)
                best = c
        if best is None or best_count == 0:
            break
        selected.append(best)
        remaining -= set(best["separates_ids"])
        print(f"  Round {round_i+1}: +{best_count} covered by {best['table']} (size {best['size']}), {len(remaining)} remaining")

    print(f"\n  Selected {len(selected)} new witnesses.")
    print(f"  Final gap: {len(remaining)} pairs uncoverable by any size ≤ 3 magma")
    if remaining:
        print(f"  Remaining gap IDs: {sorted(remaining)}")

    # ── Verify selected witnesses are SOUND ──
    print(f"\n{'='*72}")
    print("SOUNDNESS CHECK ON SELECTED WITNESSES")
    print(f"{'='*72}")

    for w in selected:
        table = w["table"]
        verify_soundness(table, equations, matrix, masks)

    # ── Also check: for hard3 TRUE pairs, do new witnesses produce false separations? ──
    print(f"\n{'='*72}")
    print("FALSE NEGATIVE RISK CHECK (hard3 TRUE pairs)")
    print(f"{'='*72}")

    for w in selected:
        fn_risk = 0
        for p in hard3_true:
            eq1_holds = check_equation(p["equation1"], w["table"])
            eq2_holds = check_equation(p["equation2"], w["table"])
            if eq1_holds and not eq2_holds:
                # This would be a FALSE separation on a TRUE pair = UNSOUND!
                fn_risk += 1
                print(f"  UNSOUND! {p['id']}: E1 holds, E2 fails on {w['table']}")
        if fn_risk == 0:
            print(f"  ✓ {w['table']}: No false separations on hard3 TRUE pairs")


def mine_magmas(size, gap_pairs, equations, masks):
    """Try all magmas of given size, find ones that separate gap pairs."""
    candidates = []
    n = size
    # Generate all n×n operation tables
    total_tables = n ** (n * n)
    checked = 0

    for values in itertools.product(range(n), repeat=n*n):
        table = [list(values[i*n:(i+1)*n]) for i in range(n)]
        checked += 1
        if checked % 5000 == 0:
            print(f"    checked {checked}/{total_tables}...")

        # Check which gap pairs this magma separates
        separates = []
        for p in gap_pairs:
            e1_holds = check_equation(p["equation1"], table)
            if e1_holds:
                e2_holds = check_equation(p["equation2"], table)
                if not e2_holds:
                    separates.append(p["id"])

        if separates:
            candidates.append({
                "table": table,
                "size": size,
                "new_coverage": len(separates),
                "separates_ids": separates,
            })

    print(f"    Done. {len(candidates)} magmas separate at least 1 gap pair.")
    return candidates


def verify_soundness(table, equations, matrix, masks):
    """Quick soundness check: no TRUE implication should be separated by this witness."""
    # Check a sample of TRUE implications
    # Full check would be 22M pairs — sample 100k
    import random
    random.seed(42)
    n = len(equations)
    violations = 0
    checked = 0
    sample_size = 50000

    for _ in range(sample_size):
        i = random.randint(0, n-1)
        j = random.randint(0, n-1)
        if i == j:
            continue
        gt = implication_answer(matrix, i, j)
        if gt is True:
            # E1 holds and E2 holds — witness should NOT separate
            # (i.e., if E1 holds, E2 must also hold)
            e1_holds = check_equation(equations[i], table)
            if e1_holds:
                e2_holds = check_equation(equations[j], table)
                if not e2_holds:
                    violations += 1
                    if violations <= 3:
                        print(f"  VIOLATION: Eq{i} → Eq{j} is TRUE but witness separates!")
        checked += 1

    print(f"  Table {table}: {violations} violations in {checked} sampled TRUE pairs")
    return violations == 0


if __name__ == "__main__":
    analyze_coverage()
