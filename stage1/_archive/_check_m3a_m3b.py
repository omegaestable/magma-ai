#!/usr/bin/env python3
"""Check if v26d's M3A and M3B magmas are admissible in the locked ledger."""
import json

d = json.load(open("results/v26_recovery/magma_audit_locked.json"))

# M3A from v26d: M[0]={1,0,0}  M[1]={2,1,2}  M[2]={1,2,0}
M3A = [[1,0,0],[2,1,2],[1,2,0]]
# M3B from v26d: a*b=2 if a=2 or b=2, else 0
M3B = [[0,0,2],[0,0,2],[2,2,2]]
# Top greedy winner
TOP1 = [[2,1,2],[2,2,2],[2,2,2]]

for name, table in [("M3A", M3A), ("M3B", M3B), ("TOP1", TOP1)]:
    found = False
    for c in d["candidates"]:
        if c["table"] == table:
            print(f"{name} {table}:")
            print(f"  classification: {c['classification']}")
            print(f"  universal_caught: {len(c['universal_caught_ids'])} {c['universal_caught_ids']}")
            print(f"  cycling_caught: {len(c['cycling_caught_ids'])} {c['cycling_caught_ids']}")
            print(f"  universal_true_flags: {c['universal_true_flags']}")
            print(f"  cycling_true_flags: {c['cycling_true_flags']}")
            found = True
            break
    if not found:
        print(f"{name} {table}: NOT FOUND in candidates (no signal)")

# Also check what v26e's COUNT2 structural test maps to
# Count how many FPs each structural family catches
print("\n--- Overlap with T3R (b+1 mod 3) ---")
T3R = [[1,2,0],[1,2,0],[1,2,0]]
for c in d["candidates"]:
    if c["table"] == T3R:
        print(f"  T3R: {c['classification']}, universal={c['universal_caught_ids']}")
        break

# T3L (a+1 mod 3)
T3L = [[1,1,1],[2,2,2],[0,0,0]]
for c in d["candidates"]:
    if c["table"] == T3L:
        print(f"  T3L: {c['classification']}, universal={c['universal_caught_ids']}")
        break

# Check what fraction of FPs is covered by the v26d magma set (T3R + T3L + M3A + M3B)
v26d_magmas = [T3R, T3L, M3A, M3B]
v26d_covered = set()
for table in v26d_magmas:
    for c in d["candidates"]:
        if c["table"] == table:
            v26d_covered.update(c["universal_caught_ids"])
            break
print(f"\nv26d total admissible coverage (T3R+T3L+M3A+M3B): {len(v26d_covered)}/{d['false_positive_count']}")
print(f"  IDs: {sorted(v26d_covered)}")

# Compare with greedy cover
greedy_covered = set(d["admissible_covered_ids"])
print(f"Greedy cover: {len(greedy_covered)}/{d['false_positive_count']}")
missed_by_v26d = greedy_covered - v26d_covered
print(f"In greedy but not in v26d: {sorted(missed_by_v26d)}")
missed_by_greedy = v26d_covered - greedy_covered
print(f"In v26d but not in greedy: {sorted(missed_by_greedy)}")
