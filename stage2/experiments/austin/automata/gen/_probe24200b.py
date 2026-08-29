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

def all_trees(depth, gens):
    if depth == 0:
        for g in gens: yield g
        return
    for g in gens: yield g
    for a in all_trees(depth-1, gens):
        for b in all_trees(depth-1, gens):
            yield ('J', a, b)

gens = [('g', 0), ('g', 1), ('g', 2)]
small_trees = list(all_trees(2, gens))  # depth<=2, includes leaves
print("num small trees depth<=2:", len(small_trees))

def try_call(name, build_uv, n_random=4000):
    """build_uv(y_or_other, x_or_other) -> (u,v); try many combos, report which rule fires"""
    C = cf.Closed(law, rules)
    hits = {}
    # exhaustive-ish over small trees for both params
    tested = 0
    for a in small_trees:
        for b in small_trees:
            u, v = build_uv(a, b)
            if u is None: continue
            which = None
            for i, (conds, xexp, tag) in enumerate(rules):
                if C.check(conds, u, v):
                    r = C.ev(xexp, u, v)
                    if r is not None:
                        which = i; break
            tested += 1
            if which is not None:
                hits[which] = hits.get(which, 0) + 1
    # random deeper trees too
    for _ in range(n_random):
        a = rand_term(random.choice([1,2,3,4]))
        b = rand_term(random.choice([1,2,3,4]))
        u, v = build_uv(a, b)
        if u is None: continue
        which = None
        for i, (conds, xexp, tag) in enumerate(rules):
            if C.check(conds, u, v):
                r = C.ev(xexp, u, v)
                if r is not None:
                    which = i; break
        tested += 1
        if which is not None:
            hits[which] = hits.get(which, 0) + 1
    print(name, "tested", tested, "hits(rule idx 1-based: count):", {k+1: v for k, v in hits.items()})

# Call2: u2 = J(y, x), v2 = x  (T1 forced free)
try_call("Call2 u=J(y,x) v=x", lambda y, x: (('J', y, x), x))
# Call4: u4 = J(x, z), v4 = z  (T3 forced free)
try_call("Call4 u=J(x,z) v=z", lambda x, z: (('J', x, z), z))
# Call1: u1=y, v1=x  fully free choice (already random-sampled but let's be thorough with small trees)
try_call("Call1 u=y v=x", lambda y, x: (y, x))
# Call3: u3=x, v3=z
try_call("Call3 u=x v=z", lambda x, z: (x, z))
