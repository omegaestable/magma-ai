"""Grow a rule subset for 11081 until BOTH the standard validator and the producer fuzz are clean.

Producer fuzz: collect pairs (u,v) at which some rule of the CURRENT subset fires, plant them at the
(z,y) and (y,x) slots of the law, and test the law.  On a failure, ask the FULL 24-rule set which of
its rules fires at the failing top pair, and add the first one missing from the subset.
"""
import sys, collections, time, random, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
A, B = law[1]
PER = 120


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i + 1
    return 0


def collect(rules, seeds=(3, 5)):
    byb = collections.defaultdict(list)
    for sd in seeds:
        for mk in (lambda C: cf.deep_tests(C, law, 2000, 120, sd),
                   lambda C: fz.fuzz(C, law, rules, 8000, seed=sd + 100),
                   lambda C: fz.closure_fuzz(C, law, 8000, seed=sd + 200),
                   lambda C: fz.critical_fuzz(C, law, 8000, seed=sd + 300)):
            C = cf.Closed(law, rules)
            mk(C)
            for (u, v) in list(C.memo.keys()):
                b = branch(C, u, v)
                if b and len(byb[b]) < PER:
                    byb[b].append((u, v))
    return byb


random.seed(11)
POOL = [('g', 0), ('g', 1), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))] + [rand_term(3) for _ in range(6)]


def pfuzz(rules):
    """returns (n_tests, list of failing assignments)"""
    byb = collect(rules)
    fails = []
    n = 0
    for b, prs in sorted(byb.items()):
        for (u, v) in prs:
            for slot in ('zy', 'yx'):
                for t in POOL:
                    C = cf.Closed(law, rules)
                    s = {'x': t, 'y': v, 'z': u} if slot == 'zy' else {'x': v, 'y': u, 'z': t}
                    try:
                        got = C.op(C.evp(A, s), C.evp(B, s))
                    except RecursionError:
                        continue
                    n += 1
                    if got != s['x']:
                        fails.append((b, slot, s))
    return n, fails, {k: len(v) for k, v in sorted(byb.items())}


cur = sorted(int(t) for t in sys.argv[1].split(',')) if len(sys.argv) > 1 else [1, 2, 4, 8, 9]
CF = cf.Closed(law, allrules)
for it in range(14):
    rules = [allrules[i - 1] for i in cur]
    t0 = time.time()
    rf = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    rreal = [f for f in rf if f[1] != 'recursion']
    n, fails, hist = pfuzz(rules)
    print('iter %d subset %s : validator %d fails, producer-fuzz %d/%d fails, branch hist %s (%.0fs)'
          % (it, cur, len(rreal), len(fails), n, hist, time.time() - t0), flush=True)
    if not rreal and not fails:
        print('CLEAN'); break
    add = collections.Counter()
    for (b, slot, s) in fails[:10]:
        C = cf.Closed(law, rules)
        x, y, z = s['x'], s['y'], s['z']
        a = C.op(y, x); bb = C.op(x, a); c = C.op(z, y); d = C.op(bb, c)
        CF2 = cf.Closed(law, allrules)
        for i, (conds, xx, tag) in enumerate(allrules):
            if i + 1 in cur:
                continue
            if CF2.check(conds, y, d) and CF2.ev(xx, y, d) is not None:
                add[i + 1] += 1
        # also the sub-products, in case the hole is lower down
        for (p, q) in ((x, a), (bb, c)):
            for i, (conds, xx, tag) in enumerate(allrules):
                if i + 1 in cur:
                    continue
                if CF2.check(conds, p, q) and CF2.ev(xx, p, q) is not None:
                    add[i + 1] += 0   # record but do not prefer
    for (s0, r0, kind, sd) in rreal[:6]:
        CF2 = cf.Closed(law, allrules)
        try:
            CF2.op(CF2.evp(A, s0), CF2.evp(B, s0))
        except RecursionError:
            continue
        for i in CF2.fired:
            if i + 1 not in cur:
                add[i + 1] += 1
    print('   candidates:', dict(add.most_common()), flush=True)
    if not add:
        print('   NO candidate rule explains the failures; STOP'); break
    best = max(add.items(), key=lambda kv: (kv[1], -kv[0]))[0]
    cur = sorted(cur + [best])
    print('   adding R%d' % best, flush=True)
print('FINAL', cur)
json.dump(cur, open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x11081_pgrow.json', 'w'))
