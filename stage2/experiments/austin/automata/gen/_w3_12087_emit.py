"""Emit 5-rule skeletons for 12087 (candidates A and B) and report byte sizes."""
import sys, os, json
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
R = X.rules(exist=False)
which = sys.argv[1] if len(sys.argv) > 1 else 'A'
IDX = {'A': [0,1,3,5,10], 'B': [0,1,3,6,10], 'F': list(range(13)), 'S7': [0,1,2,3,5,8,10], 'S6': [0,1,2,3,5,10]}[which]
rules = [R[i] for i in IDX]
out = 'gen/_w3_12087_%s' % which
res = leangen.emit(EQ, out, rules_override=rules)
print(json.dumps(res))
p = os.path.join(out, 'rec%d.lean' % EQ)
txt = open(p, encoding='utf-8').read()
print(p, len(txt.encode('utf-8')), 'bytes')
i = txt.index('/-- THE LAW')
print('head bytes (up to THE LAW):', len(txt[:i].encode('utf-8')))
