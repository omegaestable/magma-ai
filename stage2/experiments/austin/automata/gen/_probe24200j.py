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
for qq in small:
    for bb in small:
        if C.check(rules[0][0], qq, bb):
            qb = (qq, bb); break
    if qb: break
q, b = qb
w = C.op(q, b)
p_ = ('g', 7)
y = ('J', ('J', p_, q), q)
x = ('J', w, b)
z = ('g', 9)
w1, T1 = which_rule(y, x)
T2 = C.op(T1, x)
w3, T3 = which_rule(x, z)
T4 = C.op(T3, z)
w5, final = which_rule(T2, T4)
print("T1 rule", w1+1 if w1 is not None else None, "T1=", T1)
print("T2 =", T2, "  T2==J(T1,x)?", T2 == ('J', T1, x))
print("T3 rule", w3+1 if w3 is not None else None, "T3=", T3)
print("T4 =", T4, "  T4==J(T3,z)?", T4 == ('J', T3, z))
print("final rule", w5+1 if w5 is not None else None, "final=", final, "expected x=", x, "MATCH" if final==x else "MISMATCH")
print("a1(a1(x)) =", (x[1][1] if x[0]=='J' and x[1][0]=='J' else x[1]))
