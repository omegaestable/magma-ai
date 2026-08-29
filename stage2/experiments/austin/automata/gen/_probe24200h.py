import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
import freemodel as fm
from freemodel import normalise, catalog, rand_term, size
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

pool = [('g', i) for i in range(3)]
random.seed(11)
hist = {}
n_examples = {}
for depth in (0,1,2,3):
    inst = fz.instances(rules, pool, 40, depth, C)
    for u, v in inst:
        which, res = which_rule(u, v)
        hist[which] = hist.get(which, 0) + 1
        if which is not None and which not in n_examples:
            n_examples[which] = (u, v, res)
    for u, v in inst:
        for t in (u, v):
            if size(t) <= 60 and t not in pool: pool.append(t)
    if len(pool) > 800: pool = pool[:800]

print("rule-firing histogram at generic Call1(u,v) via targeted rule-shaped instances:")
for k in sorted(hist, key=lambda x: (x is None, x)):
    print(' ', (k+1 if k is not None else 'NONE(free)'), hist[k], 'tag=', (rules[k][2] if k is not None else ''))
print()
print("which rule INDICES actually fire (excluding None):", sorted((k+1) for k in hist if k is not None))
