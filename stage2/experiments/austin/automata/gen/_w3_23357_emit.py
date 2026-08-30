"""Emit the 5-rule (a5) 23357 package into gen/rep23357c/."""
import sys, os
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import leangen
import importlib.util
G = D + '/gen/'
spec = importlib.util.spec_from_file_location('_w3_23357_sets2', G + '_w3_23357_sets2.py')
S = importlib.util.module_from_spec(spec)
name = sys.argv[1] if len(sys.argv) > 1 else 'a5'
out = sys.argv[2] if len(sys.argv) > 2 else G + 'rep23357c'
sys.argv = [sys.argv[0]]
spec.loader.exec_module(S)
print(leangen.emit(23357, out, rules_override=S.SETS[name]))
print('bytes', os.path.getsize(os.path.join(out, 'rec23357.lean')))
