"""coinc5833.py : coincidence-targeted check of the 5833 rule set.

Hand analysis of x = y*(x*(y*((z*x)*y))): with q0 = z*x, q1 = q0*y, q2 = y*q1, q3 = x*q2, result = y*q3,
the products q0, q1 can fire a rule (q0 = a1 x when x = J x1 (J z ..) with R-shape; q1 = a1 y when y has the
R-shape on q0), q2 is always free, q3 is free by size, and the final product fires P1/P2/P3/P4 respectively.
We build every one of those shapes explicitly (several fillers, both free and non-free q0) and evaluate.
"""
import sys, os, itertools, random
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
import importlib.util
spec = importlib.util.spec_from_file_location('chk5833', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk5833.py'))
# reuse the rule list from chk5833.py without running its main body
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk5833.py'), encoding='utf-8').read()
rules_src = src[src.index('rules = '):src.index('C = cf.Closed')]
ns = {}
exec(rules_src, ns)
rules = ns['rules']
law = normalise(parse_eq(catalog()[5833]))
C = cf.Closed(law, rules)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)

def lawv(x, y, z):
    q0 = C.op(z, x); q1 = C.op(q0, y); q2 = C.op(y, q1); q3 = C.op(x, q2)
    return C.op(y, q3), (q0, q1, q2, q3)

fails = []
tested = 0
fillers = [g(0), g(1), g(2), J(g(0), g(1)), J(J(g(1), g(2)), g(0)), J(g(2), J(g(0), g(0)))]

def rshape(u, v1, w):
    """the R1 shape for op u v: v = J v1 (J u (J (J w v1) u)) -> v1"""
    return J(v1, J(u, J(J(w, v1), u)))

for x1, z, w, y1, w2, y12, z2, extra in itertools.product(fillers, fillers, fillers, fillers, fillers, fillers, fillers, fillers[:3]):
    # A2 : x has the R-shape on z, so q0 = op z x = x1
    x = rshape(z, x1, w)
    assert C.op(z, x) == x1
    for y in (y1, J(y1, J(x1, extra)), rshape(x1, y1, w2)):
        r, _ = lawv(x, y, z); tested += 1
        if r != x: fails.append(('A2/A4', x, y, z, r))
    # A3 : y has the R-shape on q0 = J z x (free product)
    xx = extra
    q0 = C.op(z, xx)
    y = rshape(q0, y1, w2)
    r, _ = lawv(xx, y, z); tested += 1
    if r != xx: fails.append(('A3', xx, y, z, r))
    # B : q1 = a1 y = J x y12 with y R-shaped on q0
    for xb in (extra, x):
        q0 = C.op(z, xb)
        y = rshape(q0, J(xb, y12), w2)
        r, _ = lawv(xb, y, z); tested += 1
        if r != xb: fails.append(('B', xb, y, z, r))
        # also y1 = J (J xb y12) ... deeper
        y = rshape(q0, J(J(xb, y12), z2), w2)
        r, _ = lawv(xb, y, z); tested += 1
        if r != xb: fails.append(('B2', xb, y, z, r))
    if len(fails) > 5: break

print('targeted tested', tested, 'fails', len(fails))
for f in fails[:5]:
    print(f)

# structured fuzz from the repo, several seeds
try:
    import fuzz as fz
    for seed in (1, 2, 3):
        C2 = cf.Closed(law, rules)
        t, f = fz.fuzz(C2, law, rules, 8000, seed=seed)
        print('fuzz seed', seed, 'tested', t, 'fails', len(f))
        for ff in f[:3]: print('  ', ff)
except Exception as e:
    print('fuzz unavailable:', repr(e))

# extra deep tests with other seeds
for seed in (23, 47):
    C3 = cf.Closed(law, rules)
    t, f = cf.deep_tests(C3, law, 1500, 120, seed)
    print('deep seed', seed, 'tested', t, 'fails', len(f))
    for ff in f[:3]: print('  ', ff)
