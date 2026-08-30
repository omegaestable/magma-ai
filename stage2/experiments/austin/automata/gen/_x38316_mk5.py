# -*- coding: utf-8 -*-
"""cand6 = the five rules that actually FIRE in the census; drop the seven that never do.
Validated removal (PLAYBOOK 3.4 step 1) -- must be re-validated with the CONSTRUCTED families,
not the fuzz that selected them (LEMMA_LIBRARY: _orch_minim's keep-set is not a certificate)."""
import sys, pprint
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
ns = {}; exec(open(D + '/gen/_x38316_rules_cand4.py', encoding='utf-8').read(), ns)
LIVE = ['V0-W1-q0', 'V0-W1-q1', 'V0-W2', 'V0-W3-q1', 'V1-s-W1q0']
rules = [r for r in ns['rules'] if r[2] in LIVE]
print('cand6:', [r[2] for r in rules])
open(D + '/gen/_x38316_rules_cand6.py', 'w', encoding='utf-8').write('rules = ' + pprint.pformat(rules, width=200) + '\n')
