#!/usr/bin/env python3
"""
mine_v26d_magmas.py — Mine counterexample magmas for ALL current FPs.

Reads v26 result JSONs across normal, hard3, hard2.
Extracts all FP pairs and TRUE pairs.
Brute-forces all 2-elem (16) + 3-elem (19,683) magmas.
PRIMARY: universal separation (admissible witnesses).
INFORMATIONAL: cycling-assignment separation (NOT admissible, shown for context only).
Greedy set cover uses ONLY admissible (universal) magmas.
"""
from __future__ import annotations
import itertools, json, re, sys
from pathlib import Path
from collections import defaultdict

# Import from distill.py
from distill import (
    check_equation, first_failing_assignment,
    parse_equation_tree, eval_tree, _collect_tree_vars,
)

ROOT = Path(__file__).resolve().parent

# v26c normal + hard3, v26b hard2
RESULT_FILES = [
    ROOT / "results" / "sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b_20260413_133809.json",
    ROOT / "results" / "sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26c_gpt-oss-120b_20260413_145405.json",
    ROOT / "results" / "sim_hard2_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_123558.json",
]


def load_results(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", data.get("rows", []))


def test_sep_universal(table, eq1, eq2) -> bool:
    """True if table satisfies eq1 universally but NOT eq2 universally."""
    if not check_equation(eq1, table):
        return False
    return not check_equation(eq2, table)


def cycling_assignment(variables: list[str], size: int) -> dict[str, int]:
    """Assign 1st distinct var=0, 2nd=1, 3rd=2, 4th=0, ..."""
    return {v: i % size for i, v in enumerate(variables)}


def get_ordered_vars(eq1: str, eq2: str) -> list[str]:
    """Get variables in first-appearance order across both equations."""
    text = eq1 + " " + eq2
    seen = set()
    ordered = []
    for ch in text:
        if ch.isalpha() and ch not in seen:
            seen.add(ch)
            ordered.append(ch)
    return ordered


def eval_eq_with_assignment(eq: str, assignment: dict, table: list[list[int]]) -> tuple[int, int]:
    """Evaluate both sides of an equation with a specific assignment. Returns (lhs_val, rhs_val)."""
    lhs, rhs = parse_equation_tree(eq)
    return eval_tree(lhs, assignment, table), eval_tree(rhs, assignment, table)


def test_sep_cycling(table, eq1: str, eq2: str) -> bool:
    """True if with cycling assignment: eq1 holds AND eq2 fails."""
    size = len(table)
    variables = get_ordered_vars(eq1, eq2)
    assignment = cycling_assignment(variables, size)
    
    lhs1, rhs1 = eval_eq_with_assignment(eq1, assignment, table)
    if lhs1 != rhs1:
        return False  # eq1 doesn't hold → can't separate
    
    lhs2, rhs2 = eval_eq_with_assignment(eq2, assignment, table)
    return lhs2 != rhs2  # eq2 fails → separation!


def test_safety_cycling(table, eq1: str, eq2: str) -> bool:
    """Check if cycling assignment produces a FALSE FLAG on a TRUE pair.
    Returns True if this magma falsely separates a TRUE pair (BAD)."""
    size = len(table)
    variables = get_ordered_vars(eq1, eq2)
    assignment = cycling_assignment(variables, size)
    
    lhs1, rhs1 = eval_eq_with_assignment(eq1, assignment, table)
    if lhs1 != rhs1:
        return False  # eq1 fails → no separation, not a flag
    
    lhs2, rhs2 = eval_eq_with_assignment(eq2, assignment, table)
    return lhs2 != rhs2  # TRUE pair would be flagged as FALSE → BAD


def generate_all_magmas(size: int):
    cells = size * size
    for vals in itertools.product(range(size), repeat=cells):
        yield [list(vals[i*size:(i+1)*size]) for i in range(size)]


def describe_magma(table: list[list[int]]) -> str:
    """Try to find a simple verbal rule for a magma."""
    size = len(table)
    # Check if it's a*b = constant
    flat = [table[i][j] for i in range(size) for j in range(size)]
    if len(set(flat)) == 1:
        return f"a*b = {flat[0]}"
    
    # Check a*b = a (left projection)
    if all(table[i][j] == i for i in range(size) for j in range(size)):
        return "a*b = a"
    
    # Check a*b = b (right projection)
    if all(table[i][j] == j for i in range(size) for j in range(size)):
        return "a*b = b"
    
    # Check a*b = (a+b) mod size
    if all(table[i][j] == (i+j) % size for i in range(size) for j in range(size)):
        return f"a*b = (a+b) mod {size}"
    
    # Check a*b = (a+1) mod size (left shift, ignore b)
    if all(table[i][j] == (i+1) % size for i in range(size) for j in range(size)):
        return f"a*b = (a+1) mod {size} [T3L]"
    
    # Check a*b = (b+1) mod size (right shift, ignore a)
    if all(table[i][j] == (j+1) % size for i in range(size) for j in range(size)):
        return f"a*b = (b+1) mod {size} [T3R]"
    
    # Check a*b = (a*b) mod size (regular multiplication)
    if all(table[i][j] == (i*j) % size for i in range(size) for j in range(size)):
        return f"a*b = a×b mod {size}"
    
    # Check for XOR pattern (size=2)
    if size == 2 and table == [[0,1],[1,0]]:
        return "a*b = a XOR b"
    
    # Check a*b = max(a,b) or min(a,b)
    if all(table[i][j] == max(i,j) for i in range(size) for j in range(size)):
        return "a*b = max(a,b)"
    if all(table[i][j] == min(i,j) for i in range(size) for j in range(size)):
        return "a*b = min(a,b)"
    
    # Describe sparsely: how many non-zero entries?
    nonzero = sum(1 for i in range(size) for j in range(size) if table[i][j] != 0)
    if nonzero <= 2:
        entries = []
        for i in range(size):
            for j in range(size):
                if table[i][j] != 0:
                    entries.append(f"{table[i][j]} if a={i},b={j}")
        return "0 except " + "; ".join(entries)
    
    return str(table)


def main():
    # 1. Collect FPs and TRUEs
    all_fps = []
    all_trues = []
    
    for rf in RESULT_FILES:
        if not rf.exists():
            print(f"SKIP: {rf.name} not found")
            continue
        rows = load_results(rf)
        # tag from filename: normal / hard3 / hard2
        name = rf.stem
        if "normal" in name:
            tag = "normal"
        elif "hard3" in name:
            tag = "hard3"
        elif "hard2" in name:
            tag = "hard2"
        else:
            tag = "unknown"
        
        fp_count = 0
        true_count = 0
        for r in rows:
            gt = r["ground_truth"] if "ground_truth" in r else r.get("answer")
            pred = r["predicted"] if "predicted" in r else r.get("verdict")
            pid = r.get("id", r.get("problem_id", "?"))
            eq1 = r.get("equation1", r.get("eq1", ""))
            eq2 = r.get("equation2", r.get("eq2", ""))
            
            if gt is True:
                all_trues.append({"id": pid, "eq1": eq1, "eq2": eq2, "tag": tag})
                true_count += 1
            elif gt is False and pred is True:
                all_fps.append({"id": pid, "eq1": eq1, "eq2": eq2, "tag": tag})
                fp_count += 1
        print(f"{tag:8s}: {fp_count} FP, {true_count} TRUE  ({rf.name})")
    
    print(f"\nTOTAL: {len(all_fps)} FP pairs, {len(all_trues)} TRUE pairs")
    
    # 2. Mine all 2-elem + 3-elem magmas
    # Track: universal separation AND cycling-assignment separation
    uni_results = {}   # table_key -> {table, caught: set, size}
    cyc_results = {}   # table_key -> {table, caught: set, size, flags: set}
    
    for size in [2, 3]:
        total = size ** (size * size)
        print(f"\nMining {size}-elem ({total:,} magmas)...")
        count = 0
        report = max(1, total // 10)
        
        for table in generate_all_magmas(size):
            count += 1
            if count % report == 0:
                print(f"  {count:,}/{total:,} ({100*count//total}%)")
            
            key = str(table)
            uni_caught = set()
            cyc_caught = set()
            cyc_flags = set()
            
            # Test against FPs
            for fp in all_fps:
                if test_sep_universal(table, fp["eq1"], fp["eq2"]):
                    uni_caught.add(fp["id"])
                if test_sep_cycling(table, fp["eq1"], fp["eq2"]):
                    cyc_caught.add(fp["id"])
            
            # Test cycling safety against TRUE pairs
            if cyc_caught:
                for tp in all_trues:
                    if test_safety_cycling(table, tp["eq1"], tp["eq2"]):
                        cyc_flags.add(tp["id"])
            
            if uni_caught:
                uni_results[key] = {"table": table, "caught": uni_caught, "size": size}
            if cyc_caught:
                cyc_results[key] = {
                    "table": table, "caught": cyc_caught, "size": size,
                    "flags": cyc_flags, "n_flags": len(cyc_flags),
                }
        
        # Summary per size
        uni_this = [r for r in uni_results.values() if r["size"] == size]
        cyc_this = [r for r in cyc_results.values() if r["size"] == size]
        if uni_this:
            best = max(uni_this, key=lambda r: len(r["caught"]))
            print(f"  Best {size}-elem (universal): catches {len(best['caught'])}/{len(all_fps)}")
        if cyc_this:
            safe_cyc = [r for r in cyc_this if r["n_flags"] == 0]
            if safe_cyc:
                best = max(safe_cyc, key=lambda r: len(r["caught"]))
                print(f"  Best {size}-elem (cycling, SAFE): catches {len(best['caught'])}/{len(all_fps)}")
            else:
                best = min(cyc_this, key=lambda r: (r["n_flags"], -len(r["caught"])))
                print(f"  Best {size}-elem (cycling, min flags={best['n_flags']}): catches {len(best['caught'])}/{len(all_fps)}")
    
    # 3. PRIMARY: Greedy set cover — UNIVERSAL (admissible) magmas only
    print(f"\n{'='*60}")
    print("GREEDY SET COVER (UNIVERSAL / ADMISSIBLE — primary)")
    print(f"{'='*60}")
    
    uni_ranked = list(uni_results.values())
    print(f"  {len(uni_ranked)} magmas with universal separation signal")
    
    covered = set()
    selected = []
    
    while uni_ranked:
        best = max(uni_ranked, key=lambda r: len(r["caught"] - covered))
        marginal = len(best["caught"] - covered)
        if marginal == 0:
            break
        covered |= best["caught"]
        desc = describe_magma(best["table"])
        entry = {
            "table": best["table"],
            "size": best["size"],
            "marginal": marginal,
            "total_catch": len(best["caught"]),
            "caught_ids": sorted(best["caught"]),
            "cumulative": len(covered),
            "description": desc,
        }
        selected.append(entry)
        print(f"  #{len(selected)}: {best['table']} ({desc})")
        print(f"         +{marginal} new → {len(covered)}/{len(all_fps)} total")
        print(f"         catches: {sorted(best['caught'] - (covered - best['caught']))}")
        uni_ranked = [r for r in uni_ranked if r is not best]
    
    uncovered = set(fp["id"] for fp in all_fps) - covered
    print(f"\nADMISSIBLE COVERED: {len(covered)}/{len(all_fps)}")
    
    # 4. INFORMATIONAL: Cycling-assignment cover (NOT admissible — shown for context)
    print(f"\n{'='*60}")
    print("CYCLING-ASSIGNMENT COVER (INFORMATIONAL ONLY — NOT ADMISSIBLE)")
    print(f"{'='*60}")
    print("  WARNING: Cycling-assignment magmas are NOT mathematically sound.")
    print("  They may produce false separations on unseen TRUE pairs.")
    print("  Use ONLY for understanding coverage gaps, NOT for cheatsheet magmas.")
    
    safe_cyc = [r for r in cyc_results.values() if r["n_flags"] == 0]
    cyc_covered = set()
    cyc_selected = []
    
    while safe_cyc:
        best = max(safe_cyc, key=lambda r: len(r["caught"] - cyc_covered))
        marginal = len(best["caught"] - cyc_covered)
        if marginal == 0:
            break
        cyc_covered |= best["caught"]
        desc = describe_magma(best["table"])
        cyc_selected.append({
            "table": best["table"],
            "size": best["size"],
            "marginal": marginal,
            "description": desc,
            "admissible": False,
        })
        print(f"  #{len(cyc_selected)}: {best['table']} ({desc}) [NOT ADMISSIBLE]")
        print(f"         +{marginal} new → {len(cyc_covered)}/{len(all_fps)} total")
        safe_cyc = [r for r in safe_cyc if r is not best]
    
    cyc_extra = cyc_covered - covered
    print(f"\nCycling extra (beyond admissible): {len(cyc_extra)} pairs")
    print(f"  These pairs CANNOT be safely caught with 3-element universal magmas.")
    
    # 5. Per-tag breakdown (admissible cover)
    print(f"\n{'='*60}")
    print("PER-TAG COVERAGE (admissible / universal)")
    print(f"{'='*60}")
    for tag in ["normal", "hard3", "hard2"]:
        tag_fps = [fp for fp in all_fps if fp["tag"] == tag]
        tag_cov = [fp for fp in tag_fps if fp["id"] in covered]
        tag_uncov = [fp for fp in tag_fps if fp["id"] not in covered]
        print(f"  {tag:8s}: {len(tag_cov)}/{len(tag_fps)} covered")
        for fp in tag_uncov:
            print(f"    MISS: {fp['id']}: {fp['eq1'][:50]} → {fp['eq2'][:50]}")
    
    # 6. Uncovered detail
    if uncovered:
        print(f"\n{'='*60}")
        print(f"UNCOVERED ({len(uncovered)} pairs — need 4+ element magma)")
        print(f"{'='*60}")
        for uid in sorted(uncovered):
            fp = next(f for f in all_fps if f["id"] == uid)
            print(f"  {uid:20s} [{fp['tag']:8s}]: {fp['eq1']}")
            print(f"  {'':20s}           → {fp['eq2']}")
    
    # 7. Top 10 ADMISSIBLE magmas by universal catch count
    print(f"\n{'='*60}")
    print("TOP 10 ADMISSIBLE (UNIVERSAL) MAGMAS")
    print(f"{'='*60}")
    top10 = sorted(
        uni_results.values(),
        key=lambda r: -len(r["caught"])
    )[:10]
    for i, r in enumerate(top10):
        desc = describe_magma(r["table"])
        tags = defaultdict(int)
        for cid in r["caught"]:
            fp = next(f for f in all_fps if f["id"] == cid)
            tags[fp["tag"]] += 1
        tag_str = ", ".join(f"{t}:{n}" for t, n in sorted(tags.items()))
        print(f"  #{i+1}: {r['table']} ({desc})")
        print(f"       catches {len(r['caught'])}: {tag_str}")
        print(f"       ids: {sorted(r['caught'])}")
    
    # 8. Save
    output = {
        "fp_count": len(all_fps),
        "true_count": len(all_trues),
        "admissible_covered": len(covered),
        "cycling_covered_informational": len(cyc_covered),
        "uncovered_ids": sorted(uncovered),
        "admissible_set_cover": [
            {
                "table": s["table"],
                "size": s["size"],
                "marginal": s["marginal"],
                "total_catch": s["total_catch"],
                "caught_ids": s["caught_ids"],
                "cumulative": s["cumulative"],
                "description": s["description"],
                "admissible": True,
            }
            for s in selected
        ],
        "cycling_extra_ids_informational": sorted(cyc_extra),
        "top10_admissible": [
            {
                "table": r["table"],
                "size": r["size"],
                "catch_count": len(r["caught"]),
                "caught_ids": sorted(r["caught"]),
                "description": describe_magma(r["table"]),
                "admissible": True,
            }
            for r in top10
        ],
        "per_tag": {},
    }
    for tag in ["normal", "hard3", "hard2"]:
        tag_fps = [fp for fp in all_fps if fp["tag"] == tag]
        tag_cov = [fp for fp in tag_fps if fp["id"] in covered]
        output["per_tag"][tag] = {"total": len(tag_fps), "covered": len(tag_cov)}
    
    out_path = ROOT / "results" / "v26d_magma_mining.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
