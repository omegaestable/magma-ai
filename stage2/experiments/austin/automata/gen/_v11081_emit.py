"""Emit the Lean skeleton for a named 11081 rule set from _v11081_rs.py.
usage: python gen/_v11081_emit.py <setname> <outdir>"""
import sys, json
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import leangen, closedform as cf
from _v11081_rs import SETS
rules = SETS[sys.argv[1]]
for r in rules:
    print('  ', cf.show_rule(r))
print(json.dumps(leangen.emit(11081, sys.argv[2], rules_override=rules)))
