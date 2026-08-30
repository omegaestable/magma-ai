"""Emit the repaired 12-rule package for 23357 into gen/rep23357/."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import leangen
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
out = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep23357b'
print(leangen.emit(23357, out, rules_override=mod.rules))
print('bytes', os.path.getsize(os.path.join(out, 'rec23357.lean')))
