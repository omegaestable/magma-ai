"""Render the repaired 7701 skeleton (R1..R4) into gen/fix7701/ via leangen.emit(rules_override=...).
The original (false) skeleton gen/rec7701.lean is left untouched."""
import sys, os, json
HERE = 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
from rules7701fix import rules4
# the generator's own R1..R3 (from chk7701.py) must be exactly the first three rules
src = open(HERE + '/gen/chk7701.py', encoding='utf-8').read()
ns = {}
exec('rules = ' + src.split('rules = ')[1].split('\nC = ')[0], ns)
assert ns['rules'] == rules4[:3], 'transcription of R1..R3 differs from chk7701.py'
print('R1..R3 identical to the generator\'s; adding R4')
import leangen
res = leangen.emit(7701, HERE + '/gen/fix7701', rules_override=rules4)
print(json.dumps(res))
