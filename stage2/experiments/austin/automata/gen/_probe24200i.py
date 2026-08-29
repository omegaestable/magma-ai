import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
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
qb = None
for q in small:
    for b in small:
        if C.check(rules[0][0], q, b):
            qb = (q, b); break
    if qb: break
q, b = qb
w = C.op(q, b)
print("q=", q, "b=", b, "w=", w)

hits = []
for p_ in small[:60]:
    y = ('J', ('J', p_, q), q)
    x = ('J', w, b)
    which1, T1 = which_rule(y, x)
    which2, T2 = which_rule(T1, x)
    hits.append((which1, which2, p_))
from collections import Counter
c1 = Counter(w for w,_,_ in hits)
c2 = Counter(w for _,w,_ in hits)
print("Call1 rule dist:", {(k+1 if k is not None else None):v for k,v in c1.items()})
print("Call2 rule dist (T2=op(T1,x)):", {(k+1 if k is not None else None):v for k,v in c2.items()})
for which1, which2, p_ in hits[:5]:
    print("  Call1rule", which1+1 if which1 is not None else None, "Call2rule", which2+1 if which2 is not None else None, "p_=", p_)
