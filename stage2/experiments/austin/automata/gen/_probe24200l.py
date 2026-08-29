import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import revalidate as rv
import smallcheck as sc
import leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 24200
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
print("dualized:", dualized)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk%d.py' % EQ)
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print("fails:", len(fails))
if fails:
    print(fails[:3])
