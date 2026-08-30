"""Which 40037 rule subset (if any) survives BOTH the derived hole family and the standard tests."""
import sys, os, itertools, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R
EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def enc(x, y, z): return J(x, J(z, J(J(y, x), y)))
pool = [g(0), g(1), g(2), J(g(1), g(2)), J(g(0), J(g(1), g(2)))]
HOLE = []
for x, y, D, F in itertools.product(pool, repeat=4):
    s1 = J(y, x); s2 = J(s1, y); W = J(x, J(J(D, s2), D)); z = J(s2, J(W, J(J(F, s2), F)))
    HOLE.append((x, y, z))
CELL5 = []
for y, F, Fp, Cp in itertools.product(pool, repeat=4):
    Cc = J(Cp, J(J(Fp, y), Fp)); CELL5.append((J(Cc, J(J(F, y), F)), y, Cp))
ENC = []
for a, b, c in itertools.product(pool, repeat=3):
    xe = enc(a, b, c); ENC.append((xe, c, a)); ENC.append((xe, c, b))
    ENC.append((enc(a, b, enc(a, b, c)), enc(a, b, c), c))
EXH = list(itertools.product(sc.terms_upto(7, 1) + sc.terms_upto(5, 2), repeat=3))
SETS = {'GEN[1-6]': [1, 2, 3, 4, 5, 6], 'GEN+7': list(range(1, 8)), 'GEN+7+8': list(range(1, 9)),
        '[1,2,14,10]': [1, 2, 14, 10], 'ALL': list(range(1, len(R.ALL) + 1))}
def check(rules, cases, name):
    C = cf.Closed(law, rules); bad = 0; n = 0
    for x, y, z in cases:
        try:
            t = C.op(z, C.op(x, C.op(z, C.op(C.op(y, x), y))))
        except RecursionError:
            continue
        n += 1
        if t != x: bad += 1
    return n, bad
for name, idx in SETS.items():
    rules = [R.ALL[i - 1] for i in idx]
    t0 = time.time(); out = []
    for cname, cases in (('hole', HOLE), ('cell5', CELL5), ('enc', ENC), ('exh', EXH)):
        n, bad = check(rules, cases, cname)
        out.append('%s %d/%d' % (cname, bad, n))
    print('%-14s %-60s %.0fs' % (name, '  '.join(out), time.time() - t0), flush=True)
