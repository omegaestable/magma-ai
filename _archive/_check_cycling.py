#!/usr/bin/env python3
"""Check which magma+FP pairs work with CYCLING assignment (cheatsheet simulation)."""
import json, itertools
from pathlib import Path
from distill import parse_equation_tree, eval_tree, _collect_tree_vars

ROOT = Path(__file__).resolve().parent

RESULT_FILES = [
    ROOT / "results" / "sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_105355.json",
    ROOT / "results" / "sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_120531.json",
    ROOT / "results" / "sim_hard2_v26b_gpt-oss-120b_20260412_223354.json",
]

# Candidate magmas from mining
MAGMAS = {
    "XOR": {"table": [[0,1],[1,0]], "size": 2},
    "NOTA": {"table": [[1,1],[0,0]], "size": 2},
    "NAND": {"table": [[1,1],[1,0]], "size": 2},
    "AND": {"table": [[0,0],[0,1]], "size": 2},
    "OR": {"table": [[0,1],[1,1]], "size": 2},
    "XNOR": {"table": [[1,0],[0,1]], "size": 2},
    "LP": {"table": [[0,0],[1,1]], "size": 2},
    "RP": {"table": [[0,1],[0,1]], "size": 2},
    "C0": {"table": [[0,0],[0,0]], "size": 2},
    "C1": {"table": [[1,1],[1,1]], "size": 2},
    "T3R": {"table": [[1,2,0],[1,2,0],[1,2,0]], "size": 3},
    "T3L": {"table": [[1,1,1],[2,2,2],[0,0,0]], "size": 3},
    "Z3A": {"table": [[0,1,2],[1,2,0],[2,0,1]], "size": 3},
    "NEGSUM": {"table": [[0,2,1],[2,1,0],[1,0,2]], "size": 3},
    "SPARSE": {"table": [[0,0,0],[0,0,0],[0,2,0]], "size": 3},
    "SC2": {"table": [[0,1,2],[0,1,2],[1,0,2]], "size": 3},
    "SC3": {"table": [[0,0,0],[2,1,1],[1,2,2]], "size": 3},
    "SC4": {"table": [[0,0,1],[0,0,0],[0,0,0]], "size": 3},
}

def get_cycling_assignment(eq1: str, eq2: str, domain_size: int) -> dict:
    """Assign vars by first appearance across E1 then E2, cycling 0,1,2,..."""
    import re
    combined = eq1 + " " + eq2
    seen = []
    for ch in re.findall(r'\b([a-z])\b', combined):
        if ch not in seen:
            seen.append(ch)
    return {v: i % domain_size for i, v in enumerate(seen)}

def check_separation_cycling(eq1: str, eq2: str, table, domain_size: int) -> dict:
    """Check if magma separates pair using cycling assignment."""
    assignment = get_cycling_assignment(eq1, eq2, domain_size)
    
    lhs1, rhs1 = parse_equation_tree(eq1)
    lhs2, rhs2 = parse_equation_tree(eq2)
    
    e1l = eval_tree(lhs1, assignment, table)
    e1r = eval_tree(rhs1, assignment, table)
    
    if e1l != e1r:
        return {"e1_holds": False, "separates": False}
    
    e2l = eval_tree(lhs2, assignment, table)
    e2r = eval_tree(rhs2, assignment, table)
    
    return {
        "e1_holds": True,
        "separates": e2l != e2r,
        "assignment": assignment,
        "e1_vals": (e1l, e1r),
        "e2_vals": (e2l, e2r),
    }

def check_separation_universal(eq1: str, eq2: str, table) -> bool:
    """Universal check: E1 holds for all assignments, E2 fails for at least one."""
    from distill import check_equation
    if not check_equation(eq1, table):
        return False
    return not check_equation(eq2, table)

def main():
    # Load FPs
    all_fps = []
    for rf in RESULT_FILES:
        if not rf.exists(): continue
        data = json.load(open(rf, encoding="utf-8"))
        tag = rf.stem.split("_")[1]
        for r in data["results"]:
            gt = r["ground_truth"] if "ground_truth" in r else r.get("answer")
            pred = r["predicted"] if "predicted" in r else r.get("verdict")
            if gt is False and pred is True:
                all_fps.append({"id": r["id"], "eq1": r["equation1"], "eq2": r["equation2"], "tag": tag})
    
    # Load TRUEs for safety
    all_trues = []
    for rf in RESULT_FILES:
        if not rf.exists(): continue
        data = json.load(open(rf, encoding="utf-8"))
        tag = rf.stem.split("_")[1]
        for r in data["results"]:
            gt = r["ground_truth"] if "ground_truth" in r else r.get("answer")
            if gt is True:
                all_trues.append({"id": r["id"], "eq1": r["equation1"], "eq2": r["equation2"], "tag": tag})
    
    print(f"FPs: {len(all_fps)}, TRUEs: {len(all_trues)}")
    
    # For each magma, check cycling-assignment separation for each FP
    print(f"\n{'='*80}")
    print("CYCLING-ASSIGNMENT SEPARATION (what cheatsheet can actually catch)")
    print(f"{'='*80}")
    
    for mname, minfo in MAGMAS.items():
        table = minfo["table"]
        size = minfo["size"]
        cycling_catches = []
        universal_catches = []
        cycling_flags = []  # false flags on TRUE pairs
        
        for fp in all_fps:
            result = check_separation_cycling(fp["eq1"], fp["eq2"], table, size)
            if result["separates"]:
                cycling_catches.append(fp["id"])
            if check_separation_universal(fp["eq1"], fp["eq2"], table):
                universal_catches.append(fp["id"])
        
        for tp in all_trues:
            result = check_separation_cycling(tp["eq1"], tp["eq2"], table, size)
            if result["separates"]:
                cycling_flags.append(tp["id"])
        
        if not cycling_catches and not universal_catches:
            continue
        
        nc = [x for x in cycling_catches if x.startswith("normal")]
        h3c = [x for x in cycling_catches if x.startswith("hard3")]
        h2c = [x for x in cycling_catches if x.startswith("hard2")]
        
        print(f"\n{mname} (size={size}, table={table}):")
        print(f"  Cycling catches: {len(cycling_catches)} (N={len(nc)} H3={len(h3c)} H2={len(h2c)})")
        print(f"  Universal catches: {len(universal_catches)}")
        print(f"  Cycling FALSE-FLAGS on TRUE: {len(cycling_flags)}")
        if nc:
            print(f"  Normal catches: {nc}")
        if h3c:
            print(f"  Hard3 catches: {h3c}")
        if h2c:
            print(f"  Hard2 catches: {h2c}")
        if cycling_flags:
            print(f"  *** FALSE FLAGS: {cycling_flags} ***")
        
        # Show pairs caught universally but missed by cycling
        missed = set(universal_catches) - set(cycling_catches)
        if missed:
            normal_missed = [x for x in missed if x.startswith("normal")]
            if normal_missed:
                print(f"  *** NORMAL missed by cycling: {normal_missed} ***")
    
    # Now find optimal set for normal using cycling-only
    print(f"\n{'='*80}")
    print("NORMAL FP OPTIMAL COVERAGE (cycling only)")
    print(f"{'='*80}")
    
    normal_fps = [fp for fp in all_fps if fp["tag"] == "normal"]
    for fp in normal_fps:
        catchers = []
        for mname, minfo in MAGMAS.items():
            result = check_separation_cycling(fp["eq1"], fp["eq2"], minfo["table"], minfo["size"])
            if result["separates"]:
                catchers.append(mname)
        print(f"  {fp['id']}: caught by cycling: {catchers if catchers else '*** NONE ***'}")

if __name__ == "__main__":
    main()
