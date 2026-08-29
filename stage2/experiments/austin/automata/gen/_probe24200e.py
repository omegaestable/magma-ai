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
random.seed(3)

foundyx = [(y,x) for y in deep_trees for x in deep_trees if C.check(rules[0][0], y, x)]
foundxz = [(x,z) for x in deep_trees for z in deep_trees if C.check(rules[0][0], x, z)]
print("total P1(y,x) witnesses:", len(foundyx), " P1(x,z) witnesses:", len(foundxz))

def run(y, x, z):
    t1 = C.op(y, x); t2 = C.op(t1, x); t3 = C.op(x, z); t4 = C.op(t3, z)
    w5, final = which_rule(t2, t4)
    return (t1 == ('J', y, x), t3 == ('J', x, z), (w5+1 if w5 is not None else None), final == x)

# combo D: many pairs sharing x
comboD = {}
for y, x1 in foundyx:
    for x2, z in foundxz:
        if x1 == x2:
            r = run(y, x1, z)
            comboD[r[2]] = comboD.get(r[2], 0) + 1
            if not r[3]:
                print("MISMATCH combo D", y, x1, z)
print("combo D rule histogram:", comboD)

# aliasing tests: x=y, x=z, y=z, x=y=z, using random deep terms
alias_hist = {}
mism = []
random.seed(4)
for _ in range(4000):
    t = rand_term(random.choice([1,2,3,4,5]))
    kind = random.choice(['x=y','x=z','y=z','x=y=z'])
    x = t if kind in ('x=y','x=z','x=y=z') else rand_term(random.choice([1,2,3,4]))
    y = t if kind in ('x=y','x=y=z') else (t if kind=='y=z' else rand_term(random.choice([1,2,3,4])))
    z = t if kind in ('x=z','x=y=z','y=z') else rand_term(random.choice([1,2,3,4]))
    r = run(y, x, z)
    alias_hist[(kind, r[2])] = alias_hist.get((kind, r[2]), 0) + 1
    if not r[3]:
        mism.append((kind, y, x, z))
print("alias histogram:", alias_hist)
print("mismatches:", len(mism))
for m in mism[:5]:
    print("  ", m)

# also generic random large-scale, tallying final rule distribution & confirming no rule outside {1,2,4,6} and 0 mismatches
random.seed(5)
hist = {}
mism2 = 0
for _ in range(20000):
    x = rand_term(random.choice([1,2,3,4,5,6]))
    y = rand_term(random.choice([1,2,3,4,5]))
    z = rand_term(random.choice([1,2,3,4,5]))
    r = run(y, x, z)
    hist[r[2]] = hist.get(r[2], 0) + 1
    if not r[3]: mism2 += 1
print("generic random hist:", hist, "mismatches:", mism2)
