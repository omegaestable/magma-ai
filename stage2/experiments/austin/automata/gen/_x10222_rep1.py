"""10222 repair attempt 1: append the 'unlocatable decoder' rule for the (z*y) node.

Hole (measured): law 10222 is x = y*((x*y)*((z*y)*y)); z occurs ONLY inside the node (z*y), so when that
product decodes the decoder z is not recoverable from u -- e.g. u = g0*g0, op(z,u) = g0 for
z = (g0*g0)*((g0*g0)*g0).  Every generated rule for that node (B10l / B10s / level2 variants) locates z
inside u and therefore cannot fire.  The fix is a rule with NO guard on v.2.1 at all, appended LAST:

    J?v & J?v.1 & u = v.1.2 & J?v.2 & u = v.2.2  ->  v.1.1

python gen/_x10222_rep1.py [which]
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OP(a, b): return ('OP', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
base = X.rules(exist=False, level2=False)

# the appended rule: v = J (J p u) (J q u), q unconstrained  ->  p
Aprime = ([TG(V), TG(A1(V)), EQ(U, A2(A1(V))), TG(A2(V)), EQ(U, A2(A2(V)))], A1(A1(V)), 'B10e')

cands = {
    'base': base,
    'base+Ae': base + [Aprime],
}
for name, rules in cands.items():
    print('%s nrules=%d' % (name, len(rules)), flush=True)
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        t0 = time.time()
        n, f = sc.exhaustive(C, law, ms, g, limit=25)
        print('   exh%d/%d tested=%d fails=%d (%.1fs)' % (ms, g, n, len(f), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('     FAIL', {k: str(v)[:80] for k, v in s.items()}, flush=True)
