"""Grow a MINIMAL rule subset for law 11081 that passes the full validator.

Start from a seed subset; on each failure, evaluate the failing assignment under the FULL 24-rule
model with per-pair rule tracking, and add every rule the full model used that the subset lacks.
"""
import sys, time, json, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
A, B = law[1]


def full_used(s):
    """rules the FULL model fires while evaluating the law at assignment s"""
    C = cf.Closed(law, allrules)
    try:
        C.op(C.evp(A, s), C.evp(B, s))
    except RecursionError:
        return set()
    return set(C.fired)


cur = sorted(int(t) - 1 for t in sys.argv[1].split(',')) if len(sys.argv) > 1 else [0, 1, 7]
seeds = [3, 4, 5]
for it in range(12):
    rules = [allrules[i] for i in cur]
    t0 = time.time()
    fails = rv.run_tests(law, rules, seeds, 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    print('iter %d  subset %s  -> %d real fails  (%.0fs)'
          % (it, [i + 1 for i in cur], len(real), time.time() - t0), flush=True)
    if not real:
        break
    add = collections.Counter()
    for s, r, kind, sd in real[:8]:
        for i in full_used(s):
            if i not in cur:
                add[i] += 1
    print('   candidate additions (rule -> #failing instances that use it):',
          {i + 1: n for i, n in add.most_common()}, flush=True)
    if not add:
        print('   NO new rule explains the failures; stop')
        break
    best = max(add.items(), key=lambda kv: (kv[1], -kv[0]))[0]
    cur = sorted(cur + [best])
    print('   adding R%d' % (best + 1), flush=True)

print('FINAL subset', [i + 1 for i in cur])
rules = [allrules[i] for i in cur]
f2 = rv.run_tests(law, rules, [77, 78], 3000, 12000)
print('fresh seeds [77,78]:', len([x for x in f2 if x[1] != 'recursion']), 'real fails')
C = cf.Closed(law, rules)
for sd in (777, 778):
    t, f = cf.deep_tests(C, law, 20000, 300, sd)
    print('  deep20k seed', sd, 'tested', t, 'fails', len([x for x in f if x[1] != 'recursion']), flush=True)
json.dump([i + 1 for i in cur], open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x11081_subset.json', 'w'))
