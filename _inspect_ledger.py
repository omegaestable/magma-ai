#!/usr/bin/env python3
"""Quick inspect of the locked recovery ledger."""
import json

d = json.load(open("results/v26_recovery/magma_audit_locked.json"))
print(f"FP: {d['false_positive_count']}")
print(f"TRUE: {d['true_pair_count']}")
print(f"Admissible covered: {len(d['admissible_covered_ids'])}")
print(f"Uncovered: {len(d['admissible_uncovered_ids'])}")
print(f"Assignment-only extra: {len(d['assignment_only_extra_ids'])}")
print(f"\nUncovered FP IDs:")
for uid in d["admissible_uncovered_ids"]:
    print(f"  {uid}")
print(f"\nAssignment-only extra IDs ({len(d['assignment_only_extra_ids'])}):")
for uid in d["assignment_only_extra_ids"][:20]:
    print(f"  {uid}")
if len(d["assignment_only_extra_ids"]) > 20:
    print(f"  ... and {len(d['assignment_only_extra_ids'])-20} more")
print(f"\nGreedy cover ({len(d['greedy_cover'])} magmas):")
for g in d["greedy_cover"]:
    print(f"  {g['description']}: +{g['marginal']} -> {g['cumulative']}")
    print(f"    marginal_ids: {g['marginal_ids']}")

print(f"\nCounts by classification:")
for k, v in sorted(d["counts_by_classification"].items()):
    print(f"  {k}: {v}")
