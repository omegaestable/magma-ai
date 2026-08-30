"""_x17286_fail.py -- reproduce and print the 1 failure the full validator found on 17286."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(20000)
import closedform as cf, revalidate as rv, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
orig = normalise(parse_eq(catalog()[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = (('x', leangen.dual_pat(orig[1])) if dualized else orig)
RULES = cf.Extractor(law).rules(exist=False)
seeds = [EQ * 7 + 3, EQ * 7 + 14]

J = lambda a, b: ('J', a, b)


def show(t, cap=40):
    if size(t) > cap: return '<sz%d>' % size(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1], 999), show(t[2], 999))


fails = rv.run_tests(law, RULES, seeds, 3000, 12000)
print('fails:', len(fails))
for s, r, kind, sd in fails:
    print('kind=%s seed=%s got=%s' % (kind, sd, r if isinstance(r, str) else show(r)))
    for k in sorted(s):
        print('   %s = %s   (sz %d)' % (k, show(s[k]), size(s[k])))
    if isinstance(r, str):
        continue
    C = cf.Closed(law, RULES)
    x, y, z = s['x'], s['y'], s['z']
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    print('   A=%s dec=%s' % (show(A), A != J(y, x)))
    print('   P=%s dec=%s' % (show(P), P != J(x, z)))
    print('   Q=%s dec=%s' % (show(Q), Q != J(z, P)))
    print('   B=%s dec=%s' % (show(B), B != J(z, Q)))
    print('   top=%s  want %s' % (show(top), show(x)))
    F = fm.Free(law)
    try:
        sA = F.op(y, x); sP = F.op(x, z); sQ = F.op(z, sP); sB = F.op(z, sQ); stop = F.op(sA, sB)
        print('   SEMANTIC top=%s  ok=%s conflicts=%d' % (show(stop), stop == x, len(F.conflicts)))
    except Exception as e:
        print('   SEMANTIC ERR', repr(e)[:120])
