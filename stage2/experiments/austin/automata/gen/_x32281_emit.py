"""Emit the repaired 32281 skeleton (R1, R3, R5) into gen/rep32281/."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf, revalidate as rv, leangen

WHICH = sys.argv[1] if len(sys.argv) > 1 else 'r135'
from _x32281_try1 import R1, R2
from _x32281_try2 import R3
from _x32281_try4 import R4
from _x32281_try5 import R5
SETS = {'r13': [R1, R3], 'r134': [R1, R3, R4], 'r135': [R1, R3, R5]}
rules = SETS[WHICH]
for r in rules:
    print(cf.show_rule(r))
fails = rv.run_tests(LAW, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real))
if not real:
    out = os.path.join('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen',
                       'rep32281_' + WHICH)
    print(leangen.emit(EQ, out, rules_override=rules))
