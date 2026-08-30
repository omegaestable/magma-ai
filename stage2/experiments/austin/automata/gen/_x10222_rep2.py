"""10222 repair attempt 2: variants of the appended 'unlocatable decoder' rule."""
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

CORE = [TG(V), TG(A1(V)), EQ(U, A2(A1(V))), TG(A2(V)), EQ(U, A2(A2(V)))]
VAR = {
  'Ae':      (CORE, A1(A1(V)), 'B10e'),
  'Ae_tgU':  ([TG(U)] + CORE, A1(A1(V)), 'B10e1'),
  'Ae_tgU2': ([TG(U), TG(A1(U))] + CORE, A1(A1(V)), 'B10e2'),
  'Ae_tgQ':  ([TG(U)] + CORE + [TG(A1(A2(V)))], A1(A1(V)), 'B10e3'),
}
sel = sys.argv[1:] or list(VAR)
for name in sel:
    rules = base + [VAR[name]]
    print('base+%s  nrules=%d' % (name, len(rules)), flush=True)
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        t0 = time.time()
        n, f = sc.exhaustive(C, law, ms, g, limit=25)
        print('   exh%d/%d tested=%d fails=%d (%.1fs)' % (ms, g, n, len(f), time.time() - t0), flush=True)
        for s, r in f[:2]:
            print('     FAIL', {k: str(v)[:80] for k, v in s.items()}, flush=True)
