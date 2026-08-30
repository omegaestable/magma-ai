"""Reproduce the producer-fuzz failures of a 11081 rule subset and diagnose them.

usage: python gen/_v11081_diag.py [1,2,4,5,8,9]
"""
import sys, os, time, collections, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
src = open(HERE + '/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
IDX = [int(t) for t in (sys.argv[1] if len(sys.argv) > 1 else '1,2,4,5,8,9').split(',')]
rules = [allrules[i - 1] for i in IDX]
A, B = law[1]


def branch(C, u, v, rl=None):
    for i, (conds, x, tag) in enumerate(rl if rl is not None else C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i + 1
    return 0


def show(t, d=0):
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(%s.%s)' % (show(t[1]), show(t[2]))


byb = collections.defaultdict(list)
PER = 400
for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                 ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                 ('deep3', lambda C: cf.deep_tests(C, law, 4000, 300, 3)),
                 ('fuzz3', lambda C: fz.fuzz(C, law, rules, 15000, seed=103)),
                 ('clos3', lambda C: fz.closure_fuzz(C, law, 15000, seed=203)),
                 ('crit3', lambda C: fz.critical_fuzz(C, law, 15000, seed=303)),
                 ('fuzz4', lambda C: fz.fuzz(C, law, rules, 15000, seed=104)),
                 ('clos4', lambda C: fz.closure_fuzz(C, law, 15000, seed=204)),
                 ('crit4', lambda C: fz.critical_fuzz(C, law, 15000, seed=304)),
                 ('fuzz5', lambda C: fz.fuzz(C, law, rules, 15000, seed=105)),
                 ('clos5', lambda C: fz.closure_fuzz(C, law, 15000, seed=205)),
                 ('crit5', lambda C: fz.critical_fuzz(C, law, 15000, seed=305))):
    C = cf.Closed(law, rules)
    mk(C)
    for (u, v) in list(C.memo.keys()):
        b = branch(C, u, v)
        if b and len(byb[b]) < PER:
            byb[b].append((u, v))
print('firing pairs per branch:', {k: len(v) for k, v in sorted(byb.items())}, flush=True)

random.seed(11)
pool = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))] + [rand_term(3) for _ in range(10)]
found = []
for b, prs in sorted(byb.items()):
    for (u, v) in prs:
        for slot in ('zy', 'yx', 'xy'):
            for t in pool:
                C = cf.Closed(law, rules)
                if slot == 'zy':
                    s = {'x': t, 'y': v, 'z': u}
                elif slot == 'yx':
                    s = {'x': v, 'y': u, 'z': t}
                else:
                    s = {'x': u, 'y': v, 'z': t}
                try:
                    got = C.op(C.evp(A, s), C.evp(B, s))
                except RecursionError:
                    continue
                if got != s['x']:
                    found.append((b, slot, s, got))
print('FAILURES:', len(found), flush=True)
found.sort(key=lambda f: size(f[2]['x']) + size(f[2]['y']) + size(f[2]['z']))
CF = cf.Closed(law, allrules)
for (b, slot, s, got) in found[:4]:
    x, y, z = s['x'], s['y'], s['z']
    C = cf.Closed(law, rules)
    a = C.op(y, x); bb = C.op(x, a); c = C.op(z, y); d = C.op(bb, c); r = C.op(y, d)
    print('--- collected-branch %d slot %s  |x|=%d |y|=%d |z|=%d' % (b, slot, size(x), size(y), size(z)))
    print('   x =', show(x))
    print('   y =', show(y))
    print('   z =', show(z))
    print('   A=op(y,x) br%d sz%d   B=op(x,A) br%d sz%d   C=op(z,y) br%d sz%d   D=op(B,C) br%d sz%d   TOP=op(y,D) br%d'
          % (branch(C, y, x), size(a), branch(C, x, a), size(bb), branch(C, z, y), size(c),
             branch(C, bb, c), size(d), branch(C, y, d)))
    print('   got  =', show(r), ' want =', show(x))
    C24 = cf.Closed(law, allrules)
    a2_ = C24.op(y, x); b2_ = C24.op(x, a2_); c2_ = C24.op(z, y); d2_ = C24.op(b2_, c2_); r2_ = C24.op(y, d2_)
    print('   24-rule model: TOP branch R%d  result matches x: %s' % (branch(C24, y, d2_), r2_ == x))
    print('   24-rule branches: A=R%d B=R%d C=R%d D=R%d' % (branch(C24, y, x), branch(C24, x, a2_),
                                                            branch(C24, z, y), branch(C24, b2_, c2_)))
    # which of the 24 rules would fire at the failing top pair, in the 6-rule model's terms
    C6 = cf.Closed(law, rules)
    C6.op(y, x); C6.op(x, C6.op(y, x))
    cand = []
    for i, (conds, xx, tag) in enumerate(allrules):
        if C6.check(conds, y, d) and C6.ev(xx, y, d) is not None:
            cand.append(i + 1)
    print('   rules of the 24 that fire at the failing TOP pair (evaluated in the 6-rule model):', cand)
