import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
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

def all_trees(depth, gens):
    if depth == 0:
        for g in gens: yield g
        return
    for g in gens: yield g
    for a in all_trees(depth-1, gens):
        for b in all_trees(depth-1, gens):
            yield ('J', a, b)

gens = [('g', 0), ('g', 1), ('g', 2)]
small = list(all_trees(2, gens))
# find a P1(q,b) witness so op(q,b) decodes (not free)
qb = None
for q in small:
    for b in small:
        if C.check(rules[0][0], q, b):
            qb = (q, b); break
    if qb: break
print("qb witness:", qb)
q, b = qb
w = C.op(q, b)
print("w = op(q,b) =", w, "  free would be", ('J', q, b), " decoded:", w != ('J', q, b))

# now construct y = J(J(p,q), q) for various p, and x = J(w, b)
hits = []
for p_ in small[:40]:
    y = ('J', ('J', p_, q), q)
    x = ('J', w, b)
    which, res = which_rule(y, x)
    hits.append((which, p_))
from collections import Counter
print("rule histogram over p_ choices:", Counter(w for w,_ in hits))
for which, p_ in hits[:5]:
    print("  which=", (which+1 if which is not None else None), "p_=", p_)

# Also do a broader brute force: for MANY q,b that themselves are P1-decoded (search several),
# and many p_, tabulate which rule fires
qb_list = []
for q2 in small:
    for b2 in small:
        if C.check(rules[0][0], q2, b2):
            qb_list.append((q2, b2))
        if len(qb_list) >= 8: break
    if len(qb_list) >= 8: break
print("num qb witnesses:", len(qb_list))
all_hits = Counter()
for q2, b2 in qb_list:
    w2 = C.op(q2, b2)
    for p_ in small[:30]:
        y = ('J', ('J', p_, q2), q2)
        x = ('J', w2, b2)
        which, res = which_rule(y, x)
        all_hits[which] += 1
print("aggregate rule histogram:", {(k+1 if k is not None else None): v for k, v in all_hits.items()})
