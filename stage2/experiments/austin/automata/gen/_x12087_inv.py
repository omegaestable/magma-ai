"""Empirical check of the two invariants the 12087 law proof needs.

SU : op u v != J u v  ->  sz u < sz v
INJ: op u v != J u v  and  op u' v = op u v  ->  u = u'
"""
import sys, os, random
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized', dualized, 'law', law)

which = sys.argv[1] if len(sys.argv) > 1 else 'rep'
if which == 'rep':
    src = open('gen/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    rules = ns['rules']
else:
    src = open(which, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    rules = ns['rules']
print('nrules', len(rules))
for r in rules:
    print('  ', cf.show_rule(r))

C = cf.Closed(law, rules)
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
A, B = law[1]
NV = 3
terms = []
for i in range(4000):
    terms.append(rand_term(random.randint(1, 4), 3))
# drive the memo with law evaluations
for i in range(6000):
    s = {'x': random.choice(terms), 'y': random.choice(terms), 'z': random.choice(terms)}
    try:
        C.evp(law[1], s)
    except RecursionError:
        pass
# and with random pairs
for i in range(20000):
    try:
        C.op(random.choice(terms), random.choice(terms))
    except RecursionError:
        pass

print('memo entries', len(C.memo))
su_bad = []
byv = {}
for (u, v), r in C.memo.items():
    dec = r != ('J', u, v)
    if dec:
        if not (size(u) < size(v)):
            su_bad.append((u, v, r))
        byv.setdefault(v, []).append((u, r))
print('SU violations', len(su_bad))
for b in su_bad[:5]:
    print('  ', size(b[0]), size(b[1]), b[0], b[1], b[2])

inj_bad = []
for v, lst in byv.items():
    seen = {}
    for u, r in lst:
        if r in seen and seen[r] != u:
            inj_bad.append((v, seen[r], u, r))
        seen[r] = u
print('INJ violations (among decoded, same v)', len(inj_bad))
for b in inj_bad[:5]:
    print('  v=', b[0], 'u1=', b[1], 'u2=', b[2], 'r=', b[3])

# also: cross-check the stronger claim used in the crux -- decoded op p v = op q v => p = q
cross = 0
for v, lst in byv.items():
    for u, r in lst:
        # q with op q v == r but q free-producing? already covered
        pass
print('cycles', C.cycles)
