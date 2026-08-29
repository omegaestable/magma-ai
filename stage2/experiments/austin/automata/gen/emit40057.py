"""emit40057.py : regenerate the 40057 skeleton from the repaired rule set into gen/rep40057/ (originals untouched)."""
import sys, os, json
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
from rules6_40057 import rules6
import leangen
out = 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen\\rep40057'
print(json.dumps(leangen.emit(40057, out, rules_override=rules6)))
