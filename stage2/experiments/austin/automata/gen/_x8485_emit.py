"""_x8485_emit.py : emit the repaired 8485 skeleton (variant 'a' = R1 + the three full-chain rules).
Usage: python -u gen/_x8485_emit.py [variant]
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import importlib.util
spec = importlib.util.spec_from_file_location('_x8485_min', 'gen/_x8485_min.py')
m = importlib.util.module_from_spec(spec)
sys.modules['_x8485_min'] = m
spec.loader.exec_module(m)
import leangen, closedform as cf

name = sys.argv[1] if len(sys.argv) > 1 else 'a'
rules = m.VARIANTS[name]
for r in rules:
    print(cf.show_rule(r))
out = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep8485_%s' % name
print(leangen.emit(8485, out, rules_override=rules))
