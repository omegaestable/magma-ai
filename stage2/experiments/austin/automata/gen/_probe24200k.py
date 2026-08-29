import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

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

random.seed(99)
pool = [('g', i) for i in range(4)]
# grow pool with rule-shaped y,x AND their T1 values, to bias toward T1 being "interesting"
for depth in range(4):
    inst = fz.instances(rules, pool, 50, depth, C)
    for u, v in inst:
        t1 = C.op(u, v)
        for t in (u, v, t1):
            if size(t) <= 80 and t not in pool: pool.append(t)
    if len(pool) > 2000: pool = pool[:2000]
print("pool size", len(pool))

bad = 0; tested = 0
for _ in range(60000):
    y = random.choice(pool); x = random.choice(pool)
    if random.random() < 0.3:
        y = rand_term(random.choice([1,2,3,4,5]))
    if random.random() < 0.3:
        x = rand_term(random.choice([1,2,3,4,5]))
    try:
        t1 = C.op(y, x)
        t2 = C.op(t1, x)
    except RecursionError:
        continue
    tested += 1
    if t2 != ('J', t1, x):
        bad += 1
        if bad <= 5:
            print("COUNTEREXAMPLE: y=", y, "x=", x, "T1=", t1, "T2=", t2)
print("T2-free check: tested", tested, "counterexamples", bad)
