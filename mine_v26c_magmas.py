#!/usr/bin/env python3
"""
mine_v26c_magmas.py — Mine counterexample magmas for all v26b FP pairs.

Reads 3 result JSONs (normal, hard3, hard2), extracts FP pairs,
brute-forces all 2-elem (16) + 3-elem (19,683) magmas, does greedy
set cover, safety-checks against all TRUE pairs.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
from collections import defaultdict
from distill import check_equation, first_failing_assignment, parse_equation_tree, eval_tree, _collect_tree_vars, WITNESS_LIBRARY

ROOT = Path(__file__).resolve().parent

# Result files from v26b evaluation
RESULT_FILES = [
    ROOT / "results" / "sim_normal_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_105355.json",
    ROOT / "results" / "sim_hard3_balanced50_true10_false40_rotation0012_20260413_161807_v26b_gpt-oss-120b_20260413_120531.json",
    ROOT / "results" / "sim_hard2_v26b_gpt-oss-120b_20260412_223354.json",
]

def load_results(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", data.get("rows", []))

def test_sep(table, eq1, eq2) -> bool:
    """True if table satisfies eq1 but NOT eq2."""
    if not check_equation(eq1, table):
        return False
    return not check_equation(eq2, table)

def generate_all_magmas(size: int):
    cells = size * size
    for vals in itertools.product(range(size), repeat=cells):
        yield [list(vals[i*size:(i+1)*size]) for i in range(size)]

def main():
    # 1. Collect FPs and TRUEs from all result files
    all_fps = []
    all_trues = []
    
    for rf in RESULT_FILES:
        if not rf.exists():
            print(f"SKIP: {rf.name} not found")
            continue
        rows = load_results(rf)
        tag = rf.stem.split("_")[1]  # normal/hard3/hard2
        print(f"\n{rf.name}:")
        fp_count = 0
        true_count = 0
        for r in rows:
            gt = r["ground_truth"] if "ground_truth" in r else r.get("answer")
            pred = r["predicted"] if "predicted" in r else r.get("verdict")
            pid = r.get("id", r.get("problem_id", "?"))
            eq1 = r.get("equation1", r.get("eq1", ""))
            eq2 = r.get("equation2", r.get("eq2", ""))
            
            if gt is True:
                all_trues.append({"id": pid, "equation1": eq1, "equation2": eq2, "tag": tag})
                true_count += 1
            elif gt is False and pred is True:
                all_fps.append({"id": pid, "equation1": eq1, "equation2": eq2, "tag": tag})
                fp_count += 1
        print(f"  FPs: {fp_count}, TRUEs: {true_count}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_fps)} FP pairs, {len(all_trues)} TRUE pairs")
    print(f"{'='*60}")
    
    # 2. Quick check: which library witnesses catch which FPs?
    print(f"\n--- Library Witness Coverage ---")
    for w in WITNESS_LIBRARY:
        caught = []
        for fp in all_fps:
            if test_sep(w["table"], fp["equation1"], fp["equation2"]):
                caught.append(fp["id"])
        if caught:
            print(f"  {w['name']:6s} ({w['rule']:25s}): catches {len(caught)} FPs")
            for c in caught[:5]:
                print(f"         {c}")
            if len(caught) > 5:
                print(f"         ... and {len(caught)-5} more")
    
    # 3. Mine all 2-elem + 3-elem magmas
    all_results = {}  # key -> {table, caught, size}
    
    for size in [2, 3]:
        total = size ** (size * size)
        print(f"\nMining {size}-elem ({total:,} magmas)...")
        count = 0
        report = max(1, total // 10)
        for table in generate_all_magmas(size):
            count += 1
            if count % report == 0:
                print(f"  {count:,}/{total:,} ({100*count//total}%)")
            caught = set()
            for fp in all_fps:
                if test_sep(table, fp["equation1"], fp["equation2"]):
                    caught.add(fp["id"])
            if caught:
                key = str(table)
                if key not in all_results or len(caught) > len(all_results[key]["caught"]):
                    all_results[key] = {"table": table, "caught": caught, "size": size}
        
        this_size = [r for r in all_results.values() if r["size"] == size]
        if this_size:
            best = max(this_size, key=lambda r: len(r["caught"]))
            print(f"  Best {size}-elem: catches {len(best['caught'])}/{len(all_fps)}")
        else:
            print(f"  No {size}-elem separates any FP")
    
    # 4. Greedy set cover
    print(f"\n{'='*60}")
    print("GREEDY SET COVER")
    print(f"{'='*60}")
    covered = set()
    selected = []
    ranked = sorted(all_results.values(), key=lambda r: -len(r["caught"]))
    
    while ranked:
        best = max(ranked, key=lambda r: len(r["caught"] - covered))
        marginal = len(best["caught"] - covered)
        if marginal == 0:
            break
        covered |= best["caught"]
        selected.append({
            "table": best["table"],
            "size": best["size"],
            "marginal": marginal,
            "total_catch": len(best["caught"]),
            "caught_ids": sorted(best["caught"]),
            "cumulative": len(covered),
        })
        print(f"  #{len(selected)}: {best['table']} (size={best['size']}) "
              f"+{marginal} new → {len(covered)}/{len(all_fps)} total")
        ranked = [r for r in ranked if r is not best]
    
    uncovered = set(fp["id"] for fp in all_fps) - covered
    print(f"\nCovered: {len(covered)}/{len(all_fps)}")
    if uncovered:
        print(f"UNCOVERED ({len(uncovered)}):")
        for uid in sorted(uncovered):
            fp = next(f for f in all_fps if f["id"] == uid)
            print(f"  {uid} [{fp['tag']}]: {fp['equation1']} → {fp['equation2']}")
    
    # 5. Safety check selected magmas against TRUE pairs
    print(f"\n{'='*60}")
    print(f"SAFETY CHECK (against {len(all_trues)} TRUE pairs)")
    print(f"{'='*60}")
    
    for i, s in enumerate(selected):
        table = s["table"]
        flags = []
        for tp in all_trues:
            if test_sep(table, tp["equation1"], tp["equation2"]):
                flags.append(tp["id"])
        s["false_flags"] = len(flags)
        s["false_flag_ids"] = flags
        status = "SAFE" if not flags else f"UNSAFE ({len(flags)} flags)"
        print(f"  #{i+1} {table} → {status}")
        if flags:
            for fid in flags[:3]:
                print(f"    flags: {fid}")
    
    # 6. Per-tag breakdown
    print(f"\n{'='*60}")
    print("PER-TAG COVERAGE")
    print(f"{'='*60}")
    for tag in ["normal", "hard3", "hard2"]:
        tag_fps = [fp for fp in all_fps if fp["tag"] == tag]
        tag_covered = [fp for fp in tag_fps if fp["id"] in covered]
        print(f"  {tag:8s}: {len(tag_covered)}/{len(tag_fps)} FPs covered by set cover")
        tag_uncovered = [fp for fp in tag_fps if fp["id"] not in covered]
        if tag_uncovered:
            for fp in tag_uncovered:
                print(f"    MISS: {fp['id']}: {fp['equation1'][:40]}... → {fp['equation2'][:40]}...")
    
    # 7. Focus: what covers the 8 normal FPs specifically?
    print(f"\n{'='*60}")
    print("NORMAL FP DETAIL (target: 100%)")
    print(f"{'='*60}")
    normal_fps = [fp for fp in all_fps if fp["tag"] == "normal"]
    for fp in normal_fps:
        catchers = []
        for key, r in all_results.items():
            if fp["id"] in r["caught"]:
                catchers.append((r["size"], r["table"]))
        catchers.sort(key=lambda x: (x[0], str(x[1])))
        n2 = sum(1 for c in catchers if c[0] == 2)
        n3 = sum(1 for c in catchers if c[0] == 3)
        print(f"\n  {fp['id']}:")
        print(f"    E1: {fp['equation1']}")
        print(f"    E2: {fp['equation2']}")
        print(f"    Separable by: {n2} 2-elem, {n3} 3-elem magmas")
        if catchers:
            # Show best (smallest size, then first)
            best = catchers[0]
            print(f"    Best: {best[1]} (size={best[0]})")
        else:
            print(f"    *** NOT SEPARABLE by any 2/3-elem magma ***")
    
    # 8. Save
    output = {
        "fp_count": len(all_fps),
        "true_count": len(all_trues),
        "covered_count": len(covered),
        "uncovered_ids": sorted(uncovered),
        "set_cover": [
            {
                "table": s["table"],
                "size": s["size"],
                "marginal": s["marginal"],
                "total_catch": s["total_catch"],
                "caught_ids": s["caught_ids"],
                "cumulative": s["cumulative"],
                "false_flags": s["false_flags"],
                "false_flag_ids": s.get("false_flag_ids", []),
            }
            for s in selected
        ],
        "per_tag": {},
        "normal_fp_detail": [],
    }
    for tag in ["normal", "hard3", "hard2"]:
        tag_fps = [fp for fp in all_fps if fp["tag"] == tag]
        tag_cov = [fp for fp in tag_fps if fp["id"] in covered]
        output["per_tag"][tag] = {"total": len(tag_fps), "covered": len(tag_cov)}
    
    for fp in normal_fps:
        catchers = []
        for key, r in all_results.items():
            if fp["id"] in r["caught"]:
                catchers.append({"size": r["size"], "table": r["table"]})
        catchers.sort(key=lambda x: (x["size"], str(x["table"])))
        output["normal_fp_detail"].append({
            "id": fp["id"],
            "equation1": fp["equation1"],
            "equation2": fp["equation2"],
            "n_catchers_2elem": sum(1 for c in catchers if c["size"] == 2),
            "n_catchers_3elem": sum(1 for c in catchers if c["size"] == 3),
            "best": catchers[0] if catchers else None,
        })
    
    out_path = ROOT / "results" / "v26c_magma_mining.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
