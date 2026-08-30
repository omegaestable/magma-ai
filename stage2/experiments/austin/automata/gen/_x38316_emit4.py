"""Emit the validated 12-rule `cand4` skeleton for 38316."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import leangen
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
ns = {}; exec(open(GEN + '_x38316_rules_cand4.py', encoding='utf-8').read(), ns)
print(leangen.emit(38316, GEN + 'rep38316b', rules_override=ns['rules']))
