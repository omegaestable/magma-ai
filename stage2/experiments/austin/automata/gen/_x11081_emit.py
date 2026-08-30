"""Emit the minimised 11081 package (rule subset given on the command line) into gen/rep11081/."""
import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
idx = [int(t) for t in sys.argv[1].split(',')]
rules = [allrules[i - 1] for i in idx]
for i, r in zip(idx, rules):
    print('R%-3d %s' % (i, cf.show_rule(r)))
out = sys.argv[2] if len(sys.argv) > 2 else \
    'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep11081'
print(json.dumps(leangen.emit(EQ, out, rules_override=rules)))
