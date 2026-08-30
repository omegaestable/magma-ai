"""Cheap exhaustive sweep of the 17-rule rec36524 model (gen/chk36524.py's rules)."""
import sys, os, itertools, time, importlib.util
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
print('rules', len(rules), 'law', law, flush=True)
C = cf.Closed(law, rules)
def J(a, b): return ('J', a, b)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
pool = sc.terms_upto(7, 1) + sc.terms_upto(5, 2)
pool = list(dict.fromkeys(pool))
print('pool', len(pool), flush=True)
bad = []; n = 0; t0 = time.time()
for x, y, z in itertools.product(pool, repeat=3):
    try:
        r = C.op(y, C.op(C.op(z, y), C.op(y, C.op(x, y))))
    except RecursionError:
        continue
    n += 1
    if r != x: bad.append((x, y, z, r))
print('assignments %d  FAILS %d  %.0fs' % (n, len(bad), time.time() - t0))
for x, y, z, r in bad[:4]:
    print('  x=%s  y=%s  z=%s' % (show(x)[:60], show(y)[:60], show(z)[:60]))
    print('    got', show(r)[:120])
