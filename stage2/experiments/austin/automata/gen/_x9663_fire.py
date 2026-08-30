"""9663: firing counts of the generated 49 rules + the failing instance. Writes gen/_x9663_fire.log."""
import sys, os, json, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, fuzz as fz, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 9663
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
LAW = orig  # not dualized

LOG = open(os.path.join(HERE, 'gen/_x9663_fire.log'), 'w', encoding='utf-8')
def p(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + '\n'); LOG.flush()

src = open(os.path.join(HERE, 'gen/chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
p('rules', len(rules))

t0 = time.time()
C = cf.Closed(LAW, rules)
t, f = cf.deep_tests(C, LAW, 4000, 300, 31)
p('deep', t, 'fails', len(f))
fz.fuzz(C, LAW, rules, 12000, seed=131)
fz.closure_fuzz(C, LAW, 12000, seed=231)
fz.critical_fuzz(C, LAW, 12000, seed=331)
n, ex = sc.exhaustive(C, LAW, 9, 1, limit=25)
p('exh9/1', n, len(ex))
n2, ex2 = sc.exhaustive(C, LAW, 5, 2, limit=25)
p('exh5/2', n2, len(ex2))
p('cycles', C.cycles, 'secs', round(time.time() - t0, 1))
p('--- firing counts ---')
for i, r in enumerate(rules):
    n = C.fired.get(i, 0)
    if n:
        p('R%-3d %-40s %8d' % (i + 1, r[2], n))
p('--- never fired ---')
p(', '.join('R%d' % (i + 1) for i in range(len(rules)) if not C.fired.get(i, 0)))
LOG.close()
