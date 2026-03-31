"""Compute coverage of non-counting witnesses (LP, RP, C0, AND/OR) across all benchmarks."""
import sys
sys.path.insert(0, '.')
from v21_data_infrastructure import load_equations, compute_witness_masks, load_all_benchmarks, map_benchmark_to_ids, build_equation_map

eqs = load_equations()
masks = compute_witness_masks(eqs)
benchmarks = load_all_benchmarks()
eq_map = build_equation_map(eqs)
mapped, unmapped = map_benchmark_to_ids(benchmarks, eq_map)

# Witness bit indices (from WITNESS_NAMES order):
# 0=LP, 1=RP, 2=C0, 3=XOR, 4=Z3A, 5=AND, 6=OR, 7=XNOR, 8=A2, 9=T3L, 10=T3R
NON_COUNTING = [0, 1, 2, 5, 6]  # LP, RP, C0, AND, OR
COUNTING = [3, 4, 7]            # XOR, Z3A, XNOR
ARITHMETIC = [8, 9, 10]         # A2, T3L, T3R

def check_separation(m1, m2, bits):
    for b in bits:
        if (m1 >> b) & 1 and not ((m2 >> b) & 1):
            return True
    return False

from collections import defaultdict
by_bench = defaultdict(lambda: {'true': 0, 'false': 0, 'nc_sep': 0, 'counting_only': 0, 'arith_only': 0})

for p in mapped:
    bn = p.get('source', 'unknown')
    if p['answer'] == True:
        by_bench[bn]['true'] += 1
    else:
        by_bench[bn]['false'] += 1
        m1 = masks[p['eq1_id']]
        m2 = masks[p['eq2_id']]
        if check_separation(m1, m2, NON_COUNTING):
            by_bench[bn]['nc_sep'] += 1
        elif check_separation(m1, m2, COUNTING):
            by_bench[bn]['counting_only'] += 1
        elif check_separation(m1, m2, ARITHMETIC):
            by_bench[bn]['arith_only'] += 1

print("=" * 100)
print("COVERAGE ANALYSIS: Non-counting witnesses (LP, RP, C0, AND/OR) only")
print("Strategy: 'TRUE unless LP/RP/C0/AND/OR separates'")
print("=" * 100)
print()

total_t = total_f = total_nc = total_cnt = total_arith = 0
for bn in sorted(by_bench):
    b = by_bench[bn]
    t = b['true'] + b['false']
    correct = b['true'] + b['nc_sep']
    acc = correct / t * 100 if t else 0
    total_t += b['true']
    total_f += b['false']
    total_nc += b['nc_sep']
    total_cnt += b['counting_only']
    total_arith += b['arith_only']
    uncov = b['false'] - b['nc_sep'] - b['counting_only'] - b['arith_only']
    print(f"  {bn}")
    print(f"    T={b['true']:2d} F={b['false']:2d} | LP/RP/C0/AND/OR covers {b['nc_sep']}/{b['false']} FALSE | "
          f"counting adds {b['counting_only']} | arith adds {b['arith_only']} | uncovered={uncov} | acc={acc:.0f}%")

total = total_t + total_f
nc_correct = total_t + total_nc
print()
print(f"TOTALS: {total} problems ({total_t} TRUE, {total_f} FALSE)")
print(f"  Non-counting covers: {total_nc}/{total_f} FALSE ({total_nc/total_f*100:.1f}%)")
print(f"  Counting-only adds:  {total_cnt}/{total_f} FALSE ({total_cnt/total_f*100:.1f}%)")
print(f"  Arithmetic adds:     {total_arith}/{total_f} FALSE ({total_arith/total_f*100:.1f}%)")
uncov = total_f - total_nc - total_cnt - total_arith
print(f"  Uncoverable:         {uncov}/{total_f} ({uncov/total_f*100:.1f}%)")
print()
print(f"  Strategy accuracy:   {nc_correct}/{total} = {nc_correct/total*100:.1f}%")
print(f"  TRUE accuracy:       {total_t}/{total_t} = 100%")
print(f"  FALSE accuracy:      {total_nc}/{total_f} = {total_nc/total_f*100:.1f}%")

# Also compute: on the eval-relevant benchmarks (normal_balanced20)
print()
print("=" * 100)
print("EVAL-RELEVANT BENCHMARKS ONLY (normal_balanced20)")
print("=" * 100)
eval_t = eval_f = eval_nc = 0
for bn in sorted(by_bench):
    if 'normal_balanced20' in bn:
        b = by_bench[bn]
        eval_t += b['true']
        eval_f += b['false']
        eval_nc += b['nc_sep']
        correct = b['true'] + b['nc_sep']
        t = b['true'] + b['false']
        print(f"  {bn}: acc={correct/t*100:.0f}% (T={b['true']} F={b['false']} F_cov={b['nc_sep']})")

if eval_f > 0:
    eval_total = eval_t + eval_f
    eval_correct = eval_t + eval_nc
    print(f"\n  Eval accuracy: {eval_correct}/{eval_total} = {eval_correct/eval_total*100:.1f}%")
