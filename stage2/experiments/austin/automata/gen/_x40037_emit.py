"""Emit the Lean skeleton for a validated 40037 rule subset.

usage: _x40037_emit.py 1,2,3,4,5,6,13,10 [outdir-suffix]
Writes gen/rep40037<suffix>/{rec40037.lean, rules40037.txt, chk40037.py} and prints emit()'s report.
"""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
idx = [int(i) for i in sys.argv[1].split(',')]
suffix = sys.argv[2] if len(sys.argv) > 2 else ''
rules = [R.ALL[i - 1] for i in idx]
for i, r in zip(idx, rules):
    print('R%d %s' % (i, cf.show_rule(r)))
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real))
assert not real, 'NOT VALIDATED'
out = os.path.join(HERE, 'gen', 'rep%d%s' % (EQ, suffix))
print(leangen.emit(EQ, out, rules_override=rules))
print('wrote', out)
print('bytes', os.path.getsize(os.path.join(out, 'rec%d.lean' % EQ)))
