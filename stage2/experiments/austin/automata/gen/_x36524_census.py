"""36524: mode + firing-rule census of the 17-rule rec36524 model, on the big exhaustive pool.

Chain (L-form  x = op y (op (op z y) (op y (op x y)))):
   t1 = op x y   t2 = op y t1   t3 = op z y   t4 = op t3 t2   t5 = op y t4  ( = x )
Records which of t1..t5 are free and which rule fires, and any law failure.
"""
import sys, os, itertools, time, collections, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 36524
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'gen', 'chk%d.py' % EQ))
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}
exec(compile(src, spec.origin, 'exec'), ns)
rules = ns['rules']
WHICH = {}
class Which(cf.Closed):
    def op(self, u, v):
        k = (u, v)
        if k in self.memo: return self.memo[k]
        r = super().op(u, v)
        if r != ('J', u, v) and k not in WHICH:
            for i, rl in enumerate(rules):
                sub = cf.Closed(law, rules); sub.memo = self.memo
                if sub.check(rl[0], u, v): WHICH[k] = i; break
            else: WHICH[k] = -1
        return r
C = Which(law, rules)
def J(a, b): return ('J', a, b)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
MS = int(sys.argv[1]) if len(sys.argv) > 1 else 9
pool = sc.terms_upto(MS, 1) + sc.terms_upto(MS - 2, 2)
pool = list(dict.fromkeys(pool))
print('rules %d pool %d' % (len(rules), len(pool)), flush=True)
tab = collections.Counter(); bad = []; n = 0; t0 = time.time()
for x, y, z in itertools.product(pool, repeat=3):
    try:
        t1 = C.op(x, y); t2 = C.op(y, t1); t3 = C.op(z, y); t4 = C.op(t3, t2); t5 = C.op(y, t4)
    except RecursionError:
        continue
    n += 1
    m = tuple('F' if a == J(*b) else 'R%d' % (WHICH.get(b, -1) + 1)
              for a, b in ((t1, (x, y)), (t2, (y, t1)), (t3, (z, y)), (t4, (t3, t2)), (t5, (y, t4))))
    tab[m] += 1
    if t5 != x: bad.append(((x, y, z), m))
print('assignments %d  FAILS %d  %.0fs' % (n, len(bad), time.time() - t0))
print('%-34s %s' % ('(t1,t2,t3,t4,t5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1])[:15]: print('  %-32s %d' % (str(k), c))
for (x, y, z), m in bad[:4]:
    print('  FAIL', m); print('    x=%s' % show(x)[:80]); print('    y=%s' % show(y)[:80]); print('    z=%s' % show(z)[:80])
