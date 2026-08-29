import sys, os, random, itertools
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

def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def tg(t): return 2 if t[0] == 'J' else 1

def which_rule(u, v):
    for i, (conds, xexp, tag) in enumerate(rules):
        if C.check(conds, u, v):
            r = C.ev(xexp, u, v)
            if r is not None:
                return i, r
    return None, ('J', u, v)

# DELIBERATE construction attempting to trigger rule2 at Call1 (u=y, v=x):
# rule2 conds: tg(y)=2, tg(a1 y)=2, a2(a1 y)=a2(y), tg(x)=2, OPEQ(op(a2(a1 y), a2 x), a1 x)
# construct y = J(J(p,q), q)  [so a1 y=J(p,q), a2(a1 y)=q, a2 y=q -> matches self-ref cond]
# then pick b = a2 x freely, compute w = op(q,b), set x = J(w, b)  -> a1 x = w = op(q,b) matches OPEQ.
hits = []
tests = 0
for p_ in [('g',0),('g',1),('g',2), ('J',('g',0),('g',1))]:
    for q in [('g',0),('g',1),('g',2), ('J',('g',0),('g',2))]:
        y = ('J', ('J', p_, q), q)
        # sanity: check y matches rule2's non-opeq structural prefix
        for b in [('g',0),('g',1),('g',2),('J',('g',1),('g',2))]:
            w = C.op(q, b)
            x = ('J', w, b)
            tests += 1
            which, res = which_rule(y, x)
            if which is not None:
                hits.append((which+1, p_, q, b, y, x, res))

print("targeted rule2-construction tests:", tests, "fires:", len(hits))
for h in hits[:10]:
    print("  rule", h[0], "y=", h[4], "x=", h[5], "res=", h[6])

# also try constructing for rules 3,9,10 etc using similar "self-consistent" ideas generically:
# rule 9 (As): needs v deeply nested with u = a1^4(v) and a1(a1 v)=u; try v built around u.
hits9 = []
for u in [('g',0),('g',1),('g',2)]:
    for tail in [('g',0),('g',1),('g',2)]:
        v = ('J', ('J', u, tail), tail)  # a1 a1 v = u? a1 v = J(u,tail); a1(a1 v)=u
        which, res = which_rule(u, v)
        if which is not None:
            hits9.append((which+1, u, v, res))
print("rule9-ish v=J(J(u,tail),tail) at Call1(u,v) tests:", 9, "fires:", hits9)
