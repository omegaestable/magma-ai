#!/usr/bin/env python3
"""
v25a_deep_analysis.py — Targeted analysis for v25a design.

1. Check which hard3 FALSE pairs are separable by the ACTUAL cheatsheet T3R and T3L magmas
2. Check full_entries.json for teorth witness data  
3. Check implications CSV codes (-3 vs -4) for gap pairs
4. Look for size-4 magma witnesses in teorth data
5. Test Z3A, Z3sub, and other simple-formula magmas
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v21_data_infrastructure import (
    load_equations, build_equation_map, load_implications_csv,
    normalize_eq, check_equation, first_failing_assignment
)

ROOT = Path(__file__).resolve().parent

def load_benchmark(path):
    problems = []
    with open(path) as f:
        for line in f:
            problems.append(json.loads(line))
    return problems

# All SIMPLE-FORMULA 3-element magmas we can teach an LLM
TEACHABLE_WITNESSES = {
    "T3R": [[1,2,0],[1,2,0],[1,2,0]],        # a*b = next(b)
    "T3L": [[1,1,1],[2,2,2],[0,0,0]],        # a*b = next(a)
    "Z3A": [[0,1,2],[1,2,0],[2,0,1]],        # a*b = (a+b) mod 3
    "Z3sub": [[0,2,1],[2,1,0],[1,0,2]],      # a*b = -(a+b) mod 3 = (6-a-b) mod 3
    "Z3R": [[0,1,2],[0,1,2],[0,1,2]],        # a*b = b (right projection on Z3)
    "Z3L": [[0,0,0],[1,1,1],[2,2,2]],        # a*b = a (left projection on Z3) 
    "Z3mul": [[0,0,0],[0,1,2],[0,2,1]],      # a*b = a*b mod 3
    "T3R2": [[2,0,1],[2,0,1],[2,0,1]],       # a*b = next(next(b)) = prev(b)
    "T3L2": [[2,2,2],[0,0,0],[1,1,1]],       # a*b = next(next(a)) = prev(a)
    "Z3_a2b": [[0,2,1],[1,0,2],[2,1,0]],     # a*b = (2a+b) mod 3
    "Z3_ab2": [[0,1,2],[2,0,1],[1,2,0]],     # a*b = (a+2b) mod 3
    "Z3_2a2b": [[0,1,2],[2,0,1],[1,2,0]],    # a*b = (2a+2b) mod 3 = -(a+b) same as Z3sub? no
}

# Actually let me recalculate Z3_2a2b:
# a=0: 2*0+2*0=0, 2*0+2*1=2, 2*0+2*2=4%3=1 -> [0,2,1]
# a=1: 2*1+2*0=2, 2*1+2*1=4%3=1, 2*1+2*2=6%3=0 -> [2,1,0]
# a=2: 2*2+2*0=4%3=1, 2*2+2*1=6%3=0, 2*2+2*2=8%3=2 -> [1,0,2]
# So Z3_2a2b = [[0,2,1],[2,1,0],[1,0,2]] which IS Z3sub. Remove duplicate.
# Z3_a2b: a+2b mod 3
# a=0: 0,2,1 -> [0,2,1]
# a=1: 1,0,2 -> [1,0,2]  
# a=2: 2,1,0 -> [2,1,0]
# So Z3_a2b = [[0,2,1],[1,0,2],[2,1,0]]. Let me check if = Z3sub...
# Z3sub was [[0,2,1],[2,1,0],[1,0,2]]. Different row order. So they're different magmas.

# Let me also add some 2-element ones
TEACHABLE_2ELEM = {
    "LP": [[0,0],[1,1]],          # a*b = a
    "RP": [[0,1],[0,1]],          # a*b = b
    "C0": [[0,0],[0,0]],          # a*b = 0
    "C1": [[1,1],[1,1]],          # a*b = 1
    "AND": [[0,0],[0,1]],         # a*b = min(a,b)
    "OR": [[0,1],[1,1]],          # a*b = max(a,b)
    "XOR": [[0,1],[1,0]],         # a*b = a+b mod 2
    "XNOR": [[1,0],[0,1]],        # a*b = 1-(a+b mod 2) 
    "A2": [[0,0],[1,0]],          # a*b = a*(1-b)
    "NAND": [[1,1],[1,0]],        # a*b = 1-min(a,b)
}

def main():
    print("=" * 72)
    print("v25a Deep Analysis")
    print("=" * 72)

    equations = load_equations()
    eq_map = build_equation_map(equations)
    matrix = load_implications_csv()

    # Load hard3 and normal benchmarks
    hard3_files = sorted(ROOT.glob("data/benchmark/hard3_balanced*rotation0003*.jsonl"))
    normal_files = sorted(ROOT.glob("data/benchmark/normal_balanced*rotation0003*.jsonl"))
    
    hard3 = load_benchmark(hard3_files[-1]) if hard3_files else []
    normal = load_benchmark(normal_files[-1]) if normal_files else []

    hard3_false = [p for p in hard3 if p["answer"] == False]
    hard3_true = [p for p in hard3 if p["answer"] == True]
    normal_false = [p for p in normal if p["answer"] == False]
    normal_true = [p for p in normal if p["answer"] == True]

    # Map to equation IDs
    for p in hard3 + normal:
        eq1 = normalize_eq(p["equation1"])
        eq2 = normalize_eq(p["equation2"])
        p["eq1_id"] = eq_map.get(eq1)
        p["eq2_id"] = eq_map.get(eq2)

    # ── SECTION 1: Check CSV codes for hard3 FALSE pairs ──
    print(f"\n{'='*72}")
    print("SECTION 1: Implication proof types for hard3 FALSE pairs")
    print(f"{'='*72}")
    
    code_counts = Counter()
    for p in hard3_false:
        if p["eq1_id"] is not None and p["eq2_id"] is not None:
            code = matrix[p["eq1_id"]][p["eq2_id"]]
            code_counts[code] += 1
            p["csv_code"] = code
            code_name = {-3: "implicit", -4: "explicit_needed", 3: "TRUE_implicit", 4: "TRUE_explicit"}.get(code, f"unknown({code})")
            print(f"  {p['id']}: code={code} ({code_name})")
    
    print(f"\n  Code distribution: {dict(code_counts)}")
    print(f"  -3 (implicit proof, might have no small witness): {code_counts.get(-3, 0)}")
    print(f"  -4 (explicit counterexample exists): {code_counts.get(-4, 0)}")

    # ── SECTION 2: Test ALL teachable witnesses ──
    print(f"\n{'='*72}")
    print("SECTION 2: Teachable witness coverage on hard3 FALSE")
    print(f"{'='*72}")

    all_witnesses = {}
    all_witnesses.update(TEACHABLE_2ELEM)
    all_witnesses.update(TEACHABLE_WITNESSES)

    witness_results = {}
    for wname, table in all_witnesses.items():
        separates = []
        for p in hard3_false:
            e1_holds = check_equation(p["equation1"], table)
            if e1_holds:
                e2_holds = check_equation(p["equation2"], table)
                if not e2_holds:
                    separates.append(p["id"])
        witness_results[wname] = separates
        if separates:
            print(f"  {wname:10s}: separates {len(separates):2d}/30  {separates}")

    # Combined coverage
    all_covered = set()
    for seps in witness_results.values():
        all_covered.update(seps)
    print(f"\n  Combined coverage (all teachable): {len(all_covered)}/30")
    print(f"  Remaining gap: {sorted(set(p['id'] for p in hard3_false) - all_covered)}")

    # ── SECTION 3: Soundness check on TRUE pairs ──
    print(f"\n{'='*72}")
    print("SECTION 3: False separation risk on hard3 TRUE pairs")
    print(f"{'='*72}")

    for wname, table in all_witnesses.items():
        fn_count = 0
        fn_ids = []
        for p in hard3_true:
            e1_holds = check_equation(p["equation1"], table)
            if e1_holds:
                e2_holds = check_equation(p["equation2"], table)
                if not e2_holds:
                    fn_count += 1
                    fn_ids.append(p["id"])
        if fn_count > 0:
            print(f"  UNSOUND {wname:10s}: {fn_count} false separations on TRUE pairs: {fn_ids}")
    print(f"  (No output = all witnesses are sound on hard3 TRUE pairs)")

    # ── SECTION 4: Same analysis on NORMAL ──
    print(f"\n{'='*72}")
    print("SECTION 4: Teachable witness coverage on normal FALSE")
    print(f"{'='*72}")

    for wname, table in all_witnesses.items():
        separates = []
        for p in normal_false:
            e1_holds = check_equation(p["equation1"], table)
            if e1_holds:
                e2_holds = check_equation(p["equation2"], table)
                if not e2_holds:
                    separates.append(p["id"])
        if separates:
            print(f"  {wname:10s}: separates {len(separates):2d}/30  {separates}")

    # Normal TRUE soundness
    print(f"\n  Normal TRUE soundness check:")
    for wname, table in all_witnesses.items():
        fn_count = 0
        for p in normal_true:
            e1_holds = check_equation(p["equation1"], table)
            if e1_holds:
                e2_holds = check_equation(p["equation2"], table)
                if not e2_holds:
                    fn_count += 1
        if fn_count > 0:
            print(f"  UNSOUND {wname}: {fn_count} false separations on normal TRUE")
    print(f"  (No output = all sound)")

    # ── SECTION 5: Check teorth full_entries.json for witness data ──
    print(f"\n{'='*72}")
    print("SECTION 5: Teorth full_entries.json witness data")
    print(f"{'='*72}")

    entries_file = ROOT / "data" / "teorth_cache" / "full_entries.json"
    if entries_file.exists():
        with open(entries_file) as f:
            entries = json.load(f)
        print(f"  Loaded {len(entries)} entries from full_entries.json")
        
        # What types of entries are there?
        entry_types = Counter()
        has_magma = 0
        for e in entries:
            if isinstance(e, dict):
                entry_types.update(e.keys())
                if "magma" in e or "table" in e or "counterexample" in e:
                    has_magma += 1
        print(f"  Entry keys: {dict(entry_types)}")
        print(f"  Entries with magma/table/counterexample: {has_magma}")
        
        # Show first few entries
        for i, e in enumerate(entries[:3]):
            print(f"  Entry {i}: {json.dumps(e)[:200]}")
    else:
        print(f"  full_entries.json not found")

    # ── SECTION 6: Check teorth smallest_magma.txt ──
    print(f"\n{'='*72}")
    print("SECTION 6: Teorth smallest_magma.txt")
    print(f"{'='*72}")

    sm_file = ROOT / "data" / "teorth_cache" / "smallest_magma.txt"
    if sm_file.exists():
        lines = sm_file.read_text().splitlines()
        print(f"  {len(lines)} lines in smallest_magma.txt")
        # Show first 10 lines
        for line in lines[:10]:
            print(f"  {line}")
        
        # Check smallest magma sizes for our hard3 FALSE equations
        # Parse format (likely: "equation_id size" or similar)
        magma_sizes = {}
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    eq_id = int(parts[0])
                    size = int(parts[1])
                    magma_sizes[eq_id] = size
                except ValueError:
                    pass
        
        if magma_sizes:
            print(f"\n  Smallest magma sizes for hard3 FALSE E1 equations:")
            for p in hard3_false[:10]:
                if p["eq1_id"] is not None:
                    size = magma_sizes.get(p["eq1_id"], "?")
                    print(f"    {p['id']}: E1 eq_id={p['eq1_id']}, smallest_magma_size={size}")
    else:
        print(f"  smallest_magma.txt not found")

    # ── SECTION 7: Greedy cover with best teachable witnesses ──
    print(f"\n{'='*72}")
    print("SECTION 7: Greedy cover - best teachable witness combo for hard3 FALSE")
    print(f"{'='*72}")

    remaining = set(p["id"] for p in hard3_false)
    selected = []
    # Sort witnesses by coverage
    ranked = sorted(witness_results.items(), key=lambda x: -len(x[1]))
    
    for round_i in range(10):
        if not remaining:
            break
        best_name = None
        best_count = 0
        best_ids = set()
        for wname, seps in ranked:
            hits = remaining & set(seps)
            if len(hits) > best_count:
                best_count = len(hits)
                best_name = wname
                best_ids = hits
        if best_name is None or best_count == 0:
            break
        selected.append((best_name, best_ids))
        remaining -= best_ids
        print(f"  Round {round_i+1}: {best_name:10s} covers +{best_count} -> {sorted(best_ids)} | {len(remaining)} remaining")

    total_covered = sum(len(ids) for _, ids in selected)
    print(f"\n  Total covered: {total_covered}/30 with {len(selected)} witnesses")
    print(f"  Witnesses needed: {[n for n, _ in selected]}")
    print(f"  Remaining uncoverable: {len(remaining)} -> {sorted(remaining)}")
    
    # ── SECTION 8: Full HF hard3 pool analysis ──
    print(f"\n{'='*72}")
    print("SECTION 8: Full HF hard3 pool coverage by T3R+T3L")
    print(f"{'='*72}")

    hf_hard3_file = ROOT / "data" / "hf_cache" / "hard3.jsonl"
    if hf_hard3_file.exists():
        hf_hard3 = load_benchmark(hf_hard3_file)
        hf_hard3_false = [p for p in hf_hard3 if p["answer"] == False]
        print(f"  Full HF hard3 pool: {len(hf_hard3)} problems ({len(hf_hard3_false)} FALSE)")
        
        t3r_table = TEACHABLE_WITNESSES["T3R"]
        t3l_table = TEACHABLE_WITNESSES["T3L"]
        
        t3r_coverage = 0
        t3l_coverage = 0
        both_coverage = 0
        
        for p in hf_hard3_false:
            t3r_sep = check_equation(p["equation1"], t3r_table) and not check_equation(p["equation2"], t3r_table)
            t3l_sep = check_equation(p["equation1"], t3l_table) and not check_equation(p["equation2"], t3l_table)
            if t3r_sep:
                t3r_coverage += 1
            if t3l_sep:
                t3l_coverage += 1
            if t3r_sep or t3l_sep:
                both_coverage += 1
        
        print(f"  T3R coverage: {t3r_coverage}/{len(hf_hard3_false)} ({100*t3r_coverage/len(hf_hard3_false):.1f}%)")
        print(f"  T3L coverage: {t3l_coverage}/{len(hf_hard3_false)} ({100*t3l_coverage/len(hf_hard3_false):.1f}%)")
        print(f"  T3R+T3L combined: {both_coverage}/{len(hf_hard3_false)} ({100*both_coverage/len(hf_hard3_false):.1f}%)")
        
        # Also check Z3A
        z3a_table = TEACHABLE_WITNESSES["Z3A"]
        z3a_coverage = 0
        all3_coverage = 0
        for p in hf_hard3_false:
            t3r_sep = check_equation(p["equation1"], t3r_table) and not check_equation(p["equation2"], t3r_table)
            t3l_sep = check_equation(p["equation1"], t3l_table) and not check_equation(p["equation2"], t3l_table)
            z3a_sep = check_equation(p["equation1"], z3a_table) and not check_equation(p["equation2"], z3a_table)
            if z3a_sep:
                z3a_coverage += 1
            if t3r_sep or t3l_sep or z3a_sep:
                all3_coverage += 1
        print(f"  Z3A coverage: {z3a_coverage}/{len(hf_hard3_false)} ({100*z3a_coverage/len(hf_hard3_false):.1f}%)")
        print(f"  T3R+T3L+Z3A: {all3_coverage}/{len(hf_hard3_false)} ({100*all3_coverage/len(hf_hard3_false):.1f}%)")
        
        # Check ALL teachable witnesses combined
        all_teachable_coverage = 0
        for p in hf_hard3_false:
            any_sep = False
            for wname, table in all_witnesses.items():
                if check_equation(p["equation1"], table) and not check_equation(p["equation2"], table):
                    any_sep = True
                    break
            if any_sep:
                all_teachable_coverage += 1
        print(f"  All teachable combined: {all_teachable_coverage}/{len(hf_hard3_false)} ({100*all_teachable_coverage/len(hf_hard3_false):.1f}%)")
        
        # FN risk check on full hard3 TRUE
        hf_hard3_true = [p for p in hf_hard3 if p["answer"] == True]
        for wname in ["T3R", "T3L", "Z3A"]:
            table = all_witnesses[wname]
            fn = sum(1 for p in hf_hard3_true 
                    if check_equation(p["equation1"], table) and not check_equation(p["equation2"], table))
            print(f"  FN risk {wname} on full hard3 TRUE: {fn}/{len(hf_hard3_true)}")
    else:
        print(f"  hf_cache/hard3.jsonl not found")

    # ── SECTION 9: Full HF normal pool analysis ──
    print(f"\n{'='*72}")
    print("SECTION 9: Full HF normal pool coverage")
    print(f"{'='*72}")

    hf_normal_file = ROOT / "data" / "hf_cache" / "normal.jsonl"
    if hf_normal_file.exists():
        hf_normal = load_benchmark(hf_normal_file)
        hf_normal_false = [p for p in hf_normal if p["answer"] == False]
        hf_normal_true = [p for p in hf_normal if p["answer"] == True]
        print(f"  Full HF normal pool: {len(hf_normal)} ({len(hf_normal_false)} FALSE, {len(hf_normal_true)} TRUE)")
        
        # Structural test simulation
        def structural_coverage(problems_false):
            """Simulate LP/RP/C0/VARS structural tests"""
            covered = 0
            for p in problems_false:
                eq1 = p["equation1"]
                eq2 = p["equation2"]
                # Check structural tests via witness library equivalents
                for wname in ["LP", "RP", "C0", "AND"]:
                    table = TEACHABLE_2ELEM[wname]
                    if check_equation(eq1, table) and not check_equation(eq2, table):
                        covered += 1
                        break
            return covered
        
        struct_cov = structural_coverage(hf_normal_false)
        print(f"  Structural (LP/RP/C0/AND) on normal FALSE: {struct_cov}/{len(hf_normal_false)} ({100*struct_cov/len(hf_normal_false):.1f}%)")
        
        # T3R + T3L on normal FALSE (marginal gain over structural)
        t3r_table = TEACHABLE_WITNESSES["T3R"]
        t3l_table = TEACHABLE_WITNESSES["T3L"]
        z3a_table = TEACHABLE_WITNESSES["Z3A"]
        
        struct_plus_t3r = 0
        struct_plus_t3r_t3l = 0
        struct_plus_all3 = 0
        for p in hf_normal_false:
            struct_sep = any(
                check_equation(p["equation1"], TEACHABLE_2ELEM[w]) and not check_equation(p["equation2"], TEACHABLE_2ELEM[w])
                for w in ["LP", "RP", "C0", "AND"]
            )
            t3r_sep = check_equation(p["equation1"], t3r_table) and not check_equation(p["equation2"], t3r_table)
            t3l_sep = check_equation(p["equation1"], t3l_table) and not check_equation(p["equation2"], t3l_table)
            z3a_sep = check_equation(p["equation1"], z3a_table) and not check_equation(p["equation2"], z3a_table)
            
            if struct_sep or t3r_sep:
                struct_plus_t3r += 1
            if struct_sep or t3r_sep or t3l_sep:
                struct_plus_t3r_t3l += 1
            if struct_sep or t3r_sep or t3l_sep or z3a_sep:
                struct_plus_all3 += 1
        
        print(f"  Struct+T3R: {struct_plus_t3r}/{len(hf_normal_false)} ({100*struct_plus_t3r/len(hf_normal_false):.1f}%)")
        print(f"  Struct+T3R+T3L: {struct_plus_t3r_t3l}/{len(hf_normal_false)} ({100*struct_plus_t3r_t3l/len(hf_normal_false):.1f}%)")
        print(f"  Struct+T3R+T3L+Z3A: {struct_plus_all3}/{len(hf_normal_false)} ({100*struct_plus_all3/len(hf_normal_false):.1f}%)")
        
        # FN risk
        for wname in ["T3R", "T3L", "Z3A"]:
            table = all_witnesses[wname]
            fn = sum(1 for p in hf_normal_true
                    if check_equation(p["equation1"], table) and not check_equation(p["equation2"], table))
            print(f"  FN risk {wname} on normal TRUE: {fn}/{len(hf_normal_true)}")

if __name__ == "__main__":
    main()
