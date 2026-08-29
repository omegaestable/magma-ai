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

def all_trees(depth, gens):
    if depth == 0:
        for g in gens: yield g
        return
    for g in gens: yield g
    for a in all_trees(depth-1, gens):
        for b in all_trees(depth-1, gens):
            yield ('J', a, b)

gens = [('g', 0), ('g', 1), ('g', 2)]
deep_trees = list(all_trees(3, gens))
random.seed(1)
sample = deep_trees + [rand_term(random.choice([2,3,4,5])) for _ in range(4000)]

# find x's that admit a P1(y,x)-style decode (tg x=2, tg a1x=2) -- build the T1-decoded case:
# T1_dec = a1(a1 x); test Call2': op(a1(a1 x), x)
count_decode_case = 0
hits2 = {}
tested = 0
for x in sample:
    if tg(x) != 2 or tg(a1(x)) != 2:
        continue
    u = a1(a1(x)); v = x
    w, r = which_rule(u, v)
    tested += 1
    if w is not None:
        hits2[w] = hits2.get(w, 0) + 1
print("Call2' (u=a1(a1 x), v=x) with tg(x)=2,tg(a1x)=2: tested", tested, "hits", {k+1: c for k, c in hits2.items()})

# now let's directly check: whenever P1(y,x) truly holds (found via search), what's a2(a1 y) vs a1(a1 x); then compute T1, T2, and final for a FULL (x,y,z) instance and see rule at final.
found = []
for y in deep_trees:
    for x in deep_trees:
        conds = rules[0][0]
        if C.check(conds, y, x):
            found.append((y, x))
        if len(found) >= 6: break
    if len(found) >= 6: break
print("found P1(y,x) witnesses:", len(found))
for y, x in found[:6]:
    t1 = C.op(y, x)
    print("  y=", y, "x=", x, "T1=", t1, "a1(a1 x)=", a1(a1(x)))
    z = ('g', 9)
    t2 = C.op(t1, x)
    t3 = C.op(x, z)
    t4 = C.op(t3, z)
    w5, final = which_rule(t2, t4)
    print("   T2=", t2, "T3=", t3, "T4=", t4, "final rule=", (w5+1 if w5 is not None else None), "final=", final, "expected x=", x, "MATCH" if final == x else "MISMATCH")
