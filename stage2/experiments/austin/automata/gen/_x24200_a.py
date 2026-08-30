import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from collections import Counter

eq = 24200
cat = catalog(); law = normalise(parse_eq(cat[eq]))
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk%d.py' % eq)
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
C = cf.Closed(law, rules)

def which_rule(u, v):
    for i, (conds, xexp, tag) in enumerate(rules):
        if C.check(conds, u, v):
            r = C.ev(xexp, u, v)
            if r is not None:
                return i, r
    return None, ('J', u, v)

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
pool = [('g', i) for i in range(4)]
for depth in range(4):
    inst = fz.instances(rules, pool, 60, depth, C)
    for u, v in inst:
        try:
            t1 = C.op(u, v)
        except RecursionError:
            continue
        for t in (u, v, t1):
            if size(t) <= 60 and t not in pool: pool.append(t)
    if len(pool) > 1500: pool = pool[:1500]
print("pool size", len(pool))

hist = Counter(); bad2 = 0; bad4 = 0; mism = 0
examples = {}
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
for _ in range(N):
    r = random.random()
    if r < 0.5:
        y = random.choice(pool); x = random.choice(pool); z = random.choice(pool)
    else:
        y = rand_term(random.choice([1,2,3,4,5]))
        x = rand_term(random.choice([1,2,3,4,5]))
        z = rand_term(random.choice([1,2,3,4,5]))
    try:
        T1 = C.op(y, x); T2 = C.op(T1, x)
        T3 = C.op(x, z); T4 = C.op(T3, z)
        w, res = which_rule(T2, T4)
    except RecursionError:
        continue
    if T2 != ('J', T1, x): bad2 += 1
    if T4 != ('J', T3, z): bad4 += 1
    f1 = (T1 == ('J', y, x)); f3 = (T3 == ('J', x, z))
    key = (f1, f3, (w + 1) if w is not None else None)
    hist[key] += 1
    if key not in examples: examples[key] = (y, x, z, T1, T3)
    if res != x: mism += 1
print("T2 not free:", bad2, " T4 not free:", bad4, " law mismatches:", mism)
for k in sorted(hist, key=lambda k: (-hist[k], str(k))):
    print("  T1free=%-5s T3free=%-5s rootrule=%-5s  n=%d" % (k[0], k[1], k[2], hist[k]))
