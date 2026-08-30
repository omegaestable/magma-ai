"""Diagnose a producer-fuzz failure of a rule subset for law 11081: print the chain and say which of the
FULL 24 rules hold structurally at the failing top pair.

usage:  python gen/_x11081_diag.py 1,2,4,8,9
"""
import sys, collections, time, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
IDX = [int(t) for t in sys.argv[1].split(',')]
rules = [allrules[i - 1] for i in IDX]
A, B = law[1]


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i + 1
    return 0


pairs = []
for mk in (lambda C: fz.critical_fuzz(C, law, 12000, seed=303),
           lambda C: fz.closure_fuzz(C, law, 12000, seed=205),
           lambda C: fz.critical_fuzz(C, law, 12000, seed=305)):
    C = cf.Closed(law, rules)
    mk(C)
    for (u, v) in list(C.memo.keys()):
        b = branch(C, u, v)
        if b:
            pairs.append((b, u, v))
print('firing pairs', len(pairs), flush=True)

random.seed(3)
pool = [('g', 0), ('J', ('g', 0), ('g', 1))]
found = None
for (b, u, v) in pairs:
    for t in pool:
        C = cf.Closed(law, rules)
        s = {'x': t, 'y': v, 'z': u}
        try:
            got = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            continue
        if got != t:
            found = (b, s, C, got)
            break
    if found:
        break

if not found:
    print('no producer-fuzz failure found')
    raise SystemExit

b, s, C, got = found
x, y, z = s['x'], s['y'], s['z']
print('FAILING: producer branch %d at (z,y);  |x|=%d |y|=%d |z|=%d, got size %d'
      % (b, size(x), size(y), size(z), size(got)))
a = C.op(y, x); bb = C.op(x, a); c = C.op(z, y); d = C.op(bb, c); r = C.op(y, d)
for nm, (p, q) in (('A=op(y,x)', (y, x)), ('B=op(x,A)', (x, a)), ('C=op(z,y)', (z, y)),
                   ('D=op(B,C)', (bb, c)), ('TOP=op(y,D)', (y, d))):
    print('  %-12s rule %s  result size %d' % (nm, branch(C, p, q) or 'free', size(C.op(p, q))))

# which of the FULL 24 rules would fire at the failing top pair, under the FULL model
CF = cf.Closed(law, allrules)
aF = CF.op(y, x); bF = CF.op(x, aF); cF = CF.op(z, y); dF = CF.op(bF, cF); rF = CF.op(y, dF)
print('under the FULL 24-rule model: law holds?', rF == x)
for nm, (p, q) in (('A', (y, x)), ('B', (x, aF)), ('C', (z, y)), ('D', (bF, cF)), ('TOP', (y, dF))):
    print('  full %-4s rule %s' % (nm, branch(CF, p, q) or 'free'))
print('rules of the FULL set that fire at the subset-model top pair (y,d):')
for i, (conds, xx, tag) in enumerate(allrules):
    if CF.check(conds, y, d) and CF.ev(xx, y, d) is not None:
        print('   R%d [%s]' % (i + 1, tag))
