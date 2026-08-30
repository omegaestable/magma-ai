"""Print the 13 extracted rules in readable form + emit candidate rule subsets."""
import sys, os, json
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
rules13 = X.rules(exist=False)
def se(e):
    t = e[0]
    if t == 'U': return 'u'
    if t == 'V': return 'v'
    if t == 'A1': return se(e[1]) + '.1'
    if t == 'A2': return se(e[1]) + '.2'
    if t == 'OP': return 'op(%s, %s)' % (se(e[1]), se(e[2]))
    if t == 'J': return 'J(%s, %s)' % (se(e[1]), se(e[2]))
    if t == 'F': return 'F%d' % e[1]
    return str(e)
def sc(c):
    if c[0] == 'TG': return 'J?%s' % se(c[1])
    if c[0] == 'EQ': return '%s = %s' % (se(c[1]), se(c[2]))
    if c[0] == 'OPEQ': return '%s == %s' % (se(c[1]), se(c[2]))
    return str(c)
for i, (conds, res, tag) in enumerate(rules13):
    print('R%-2d [%s]' % (i, tag))
    print('     ' + ' & '.join(sc(c) for c in conds) + '  ->  ' + se(res))
json.dump([list(r) for r in rules13], open('gen/_w3_12087_rules13.json', 'w'))
