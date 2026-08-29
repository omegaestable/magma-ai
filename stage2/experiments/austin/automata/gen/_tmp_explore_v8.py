import sys, os, itertools
sys.path.insert(0, r'c:\Users\nacho\Documents\GitHub\magma-ai\stage2\experiments\austin\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 6912
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = cf.Extractor(law)
nodes = [('A',) + path for path, _ in cf.positions(X.A)] + [('B',) + path for path, _ in cf.positions(X.B)]
modes = ['free','lazy','struct','vdec']
print("nodes", nodes)

# find all base combos with used_lazy having >=1 elements, print them, and search bigger cap2
allrules = X.rules(exist=False, level2=True, cap2=10000)
print("total rules with cap2=10000:", len(allrules))
tags = sorted(set(r[2] for r in allrules))
print(len(tags), "distinct tags")
