"""_z8485_variants.py -- does the counterexample kill only variant f, or the whole extraction?

Runs the _z8485_break.py instance through closedform.Closed for every rule set on file:
the full 83-rule extraction (with and without `exist`), and every hand-built variant a..i.
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
sys.setrecursionlimit(200000)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

G = lambda i: ('g', i)
J = lambda a, b: ('J', a, b)

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def instance(z0, A, Cc, zz, y):
    X1 = J(A, J(Cc, z0)); c = J(z0, X1)
    z = J(c, J(J(J(zz, c), c), c)); x = J(X1, c)
    return x, y, z

cat = catalog(); law = normalise(parse_eq(cat[8485]))
mn = {}
exec(open(os.path.join(HERE, '_x8485_min.py'), encoding='utf-8').read().split("if __name__")[0], mn)
VAR = mn['VARIANTS']

sets = {}
X = cf.Extractor(law)
sets['FULL(noexist)'] = X.rules(exist=False)
try:
    sets['FULL(exist)'] = X.rules(exist=True)
except Exception as e:
    print('exist extraction failed:', e)
for k in sorted(VAR): sets['variant ' + k] = VAR[k]

cases = [(G(0), G(0), G(0), G(0), G(0)),
         (G(0), G(1), G(2), G(3), G(5)),
         (G(1), G(0), G(2), G(1), J(G(0), G(1)))]

for name, R in sets.items():
    bad = 0; det = []
    for cs in cases:
        x, y, z = instance(*cs)
        C = cf.Closed(law, R)
        try:
            r = C.op(C.op(x, C.op(C.op(C.op(z, x), y), y)), None) if False else \
                C.op(y, C.op(x, C.op(C.op(C.op(z, x), y), y)))
        except RecursionError:
            det.append('recursion'); bad += 1; continue
        if r != x:
            bad += 1; det.append('FAIL')
        else:
            det.append('ok')
    print('%-16s %2d rules   %s' % (name, len(R), det), flush=True)
