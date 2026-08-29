import sys
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = cf.Extractor(law)
r_all = X.rules(exist=False)
kept4 = [r_all[0], r_all[1], r_all[10], r_all[3]]
print('rule tags:', [r[2] for r in kept4])
res = leangen.emit(EQ, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep12087', rules_override=kept4)
print(res)
