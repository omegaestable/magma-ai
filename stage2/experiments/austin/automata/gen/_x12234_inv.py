"""Does  sz(op u v) + sz u < sz v  hold for every decoded pair of the FULL 6-rule rec12234 model?
Also: which digest branch (L/M/N/K) holds, and is u = oc v always true?"""
import sys, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.setrecursionlimit(30000)
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x12234_leanval as LV
LeanModel, J, isJ, a1, a2, oc = LV.LeanModel, LV.J, LV.isJ, LV.a1, LV.a2, LV.oc
law = normalise(parse_eq(catalog()[12234]))

def branch(Mo, u, v, r):
    ok = []
    if isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v)) and r == a2(a1(a1(v))) \
       and (a2(v) == J(r, u) or a2(v) == Mo.op(r, u)): ok.append('L')
    if isJ(a2(v)) and u == a2(a1(v)) and u == a2(a2(v)) and r == a1(a2(v)) and a2(v) == J(r, u): ok.append('M')
    if isJ(a2(v)) and u == a2(a2(v)) and r == a1(a2(v)) and a2(v) == J(r, u): ok.append('N')
    if isJ(a1(v)) and u == a2(a1(v)) and isJ(u) and r == oc(u) and a2(v) == Mo.op(r, u): ok.append('K')
    return ','.join(ok)

Mo = LeanModel()
random.seed(4); cf.deep_tests(Mo, law, 6000, 600, 31)
for ms, gn in ((9, 1), (5, 2)): sc.exhaustive(Mo, law, ms, gn, limit=None)
pairs = list(Mo.memo.keys())
bad_inv = []; bad_dig = []; bad_oc = []; weak = []
for (u, v) in pairs:
    r = Mo.memo[(u, v)]
    if r == J(u, v): continue
    if not (size(r) + size(u) < size(v)): bad_inv.append((u, v, r))
    b = branch(Mo, u, v, r)
    if not b: bad_dig.append((u, v, r))
    if u != oc(v): bad_oc.append((u, v, r))
    if not (size(u) < size(v)): weak.append((u, v, r))
print('pairs', len(pairs), 'decoded', sum(1 for k in pairs if Mo.memo[k] != J(*k)))
print('INV(sz r + sz u < sz v) violations', len(bad_inv))
print('digest-branch violations', len(bad_dig))
print('u = oc v violations', len(bad_oc))
print('sz u < sz v violations', len(weak))
for (u, v, r) in bad_inv[:4]:
    print('   INV-FAIL u', size(u), 'v', size(v), 'r', size(r), 'branch', branch(Mo, u, v, r))
