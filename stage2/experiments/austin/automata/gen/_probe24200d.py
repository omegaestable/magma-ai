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
random.seed(2)
sample_z = deep_trees + [rand_term(random.choice([2,3,4,5])) for _ in range(4000)]

# Call4' : T3 decoded as a1(a1 z); check op(a1(a1 z), z) always free?
tested = 0; hits4 = {}
for z in sample_z:
    if tg(z) != 2 or tg(a1(z)) != 2: continue
    u = a1(a1(z)); v = z
    w, r = which_rule(u, v)
    tested += 1
    if w is not None: hits4[w] = hits4.get(w, 0) + 1
print("Call4' (u=a1(a1 z), v=z): tested", tested, "hits", {k+1: c for k, c in hits4.items()})

# find P1(x,z) witnesses (x decodes T3 via rule1)
foundxz = []
for x in deep_trees:
    for z in deep_trees:
        if C.check(rules[0][0], x, z):
            foundxz.append((x, z))
        if len(foundxz) >= 4: break
    if len(foundxz) >= 4: break
print("P1(x,z) witnesses:", len(foundxz))

# Now test all 4 combinations using actual y,x,z instances:
# combo A: T1 free, T3 free (baseline) -- already known -> rule1
# combo B: T1 decode (P1(y,x)), T3 free
# combo C: T1 free, T3 decode (P1(x,z))
# combo D: T1 decode AND T3 decode simultaneously (need y,x s.t. P1(y,x), and SAME x,z s.t. P1(x,z))

# reuse P1(y,x) witnesses from before
foundyx = []
for y in deep_trees:
    for x in deep_trees:
        if C.check(rules[0][0], y, x):
            foundyx.append((y, x))
        if len(foundyx) >= 4: break
    if len(foundyx) >= 4: break

def run(y, x, z, label):
    t1 = C.op(y, x)
    t2 = C.op(t1, x)
    t3 = C.op(x, z)
    t4 = C.op(t3, z)
    w5, final = which_rule(t2, t4)
    ok = final == x
    print(label, "T1free?", t1 == ('J', y, x), "T3free?", t3 == ('J', x, z), "final rule", (w5+1 if w5 is not None else None), "MATCH" if ok else "MISMATCH")

from freemodel import size
# combo B: use a P1(y,x) witness for x fixed, arbitrary z not related
if foundyx:
    y, x = foundyx[0]
    z = ('g', 55)
    run(y, x, z, "combo B (T1 decode, T3 free)")

# combo C: use P1(x,z) witness
if foundxz:
    x, z = foundxz[0]
    y = ('g', 66)
    run(y, x, z, "combo C (T1 free, T3 decode)")

# combo D: need x such that BOTH exist: some y with P1(y,x) AND some z with P1(x,z). Search.
comboD_found = None
for y, x1 in foundyx:
    for x2, z in foundxz:
        if x1 == x2:
            comboD_found = (y, x1, z); break
    if comboD_found: break
if comboD_found is None:
    # try to construct explicitly: pick x, then find y with P1(y,x) and z with P1(x,z) by search
    for x in deep_trees:
        if tg(x) != 2 or tg(a1(x)) != 2: continue
        yy = None; zz = None
        for y in deep_trees:
            if C.check(rules[0][0], y, x): yy = y; break
        if yy is None: continue
        for z in deep_trees:
            if C.check(rules[0][0], x, z): zz = z; break
        if zz is None: continue
        comboD_found = (yy, x, zz); break
print("combo D witness found:", comboD_found is not None)
if comboD_found:
    y, x, z = comboD_found
    run(y, x, z, "combo D (T1 decode, T3 decode)")
