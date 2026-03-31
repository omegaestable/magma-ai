"""Per-benchmark-file coverage analysis for non-counting witnesses."""
import sys, json, glob, os
sys.path.insert(0, '.')
from v21_data_infrastructure import load_equations, compute_witness_masks, build_equation_map, normalize_eq
from v21_verify_structural_rules import rule_LP, rule_RP, rule_C0, rule_AND, rule_OR

eqs = load_equations()
masks = compute_witness_masks(eqs)
eq_map = build_equation_map(eqs)

NON_COUNTING = [0, 1, 2, 5, 6]  # LP, RP, C0, AND, OR

def check_sep(m1, m2, bits):
    for b in bits:
        if (m1 >> b) & 1 and not ((m2 >> b) & 1):
            return True
    return False

bench_files = sorted(glob.glob('data/benchmark/*.jsonl'))
total_t = total_f = total_nc = 0

print(f"{'Benchmark':<65s} {'T':>3s} {'F':>3s} {'Fcov':>4s} {'Acc':>5s}")
print("-" * 85)

for bf in bench_files:
    problems = [json.loads(l) for l in open(bf) if l.strip()]
    name = os.path.basename(bf).replace('.jsonl', '')
    t = f = nc = 0
    for p in problems:
        ans = p['answer'] if isinstance(p['answer'], bool) else p['answer'].lower() == 'true'
        if ans:
            t += 1
        else:
            f += 1
            e1n = normalize_eq(p['equation1'])
            e2n = normalize_eq(p['equation2'])
            id1 = eq_map.get(e1n)
            id2 = eq_map.get(e2n)
            if id1 is not None and id2 is not None:
                if check_sep(masks[id1], masks[id2], NON_COUNTING):
                    nc += 1
    correct = t + nc
    total = t + f
    acc = correct / total * 100 if total else 0
    total_t += t; total_f += f; total_nc += nc
    print(f"  {name:<63s} {t:3d} {f:3d} {nc:4d} {acc:5.0f}%")

print("-" * 85)
grand = total_t + total_f
gc = total_t + total_nc
print(f"  {'TOTAL':<63s} {total_t:3d} {total_f:3d} {total_nc:4d} {gc/grand*100:5.1f}%")
print()
print(f"Non-counting (LP/RP/C0/AND/OR) covers {total_nc}/{total_f} FALSE = {total_nc/total_f*100:.1f}%")
print(f"Overall strategy accuracy: {gc}/{grand} = {gc/grand*100:.1f}%")
