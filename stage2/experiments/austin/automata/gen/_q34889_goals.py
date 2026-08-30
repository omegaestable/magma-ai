"""Find generator triples refuting each goal of 34889 in the quotient model (served op = flipped)."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qmod
qmod.UNARY = []
from qmod import E, sz, show, terms_upto
from q34889 import M, J
from laws import parse_eq
from freemodel import catalog, pvars

Mo = M()
def served(a, b):      # the magma the certificate serves:  a <> b  =  op b a
    return Mo.op(b, a)

cat = catalog()
GOALS = [22818, 17522, 30591]
pool = [('g', 0), ('g', 1), ('g', 2), E, J(('g',0),('g',1)), J(('g',0),E), J(E,('g',0))]
for gid in GOALS:
    g = parse_eq(cat[gid])
    print('goal %d : %s   parsed %s' % (gid, cat[gid], g))
    vs = sorted(set(pvars(g[0]) + pvars(g[1])))
    def ev(p, s):
        if isinstance(p, str): return s[p]
        return served(ev(p[0], s), ev(p[1], s))
    found = []
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals))
        if ev(g[0], s) != ev(g[1], s):
            found.append((dict(s), ev(g[0], s), ev(g[1], s)))
            if len(found) >= 3: break
    for s, l, r in found:
        print('   REFUTED by', ' '.join('%s=%s' % (k, show(v)) for k, v in sorted(s.items())),
              ' lhs=%s  rhs=%s' % (show(l), show(r)))
    if not found: print('   *** NOT REFUTED on this pool')
