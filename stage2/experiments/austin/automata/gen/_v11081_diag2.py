"""Reproduce and diagnose the producer-fuzz-v2 failures of a named rule set."""
import sys, time, collections, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from _v11081_rs import SETS

law = normalise(parse_eq(catalog()[11081]))
A, B = law[1]
NAME = sys.argv[1] if len(sys.argv) > 1 else 'w123'
rules = SETS[NAME]
show = lambda t: 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i + 1
    return 0


byb = collections.defaultdict(list)
for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                 ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                 ('deep3', lambda C: cf.deep_tests(C, law, 5000, 300, 3)),
                 ('deep9', lambda C: cf.deep_tests(C, law, 5000, 300, 9)),
                 ('fuzz3', lambda C: fz.fuzz(C, law, rules, 20000, seed=103)),
                 ('clos3', lambda C: fz.closure_fuzz(C, law, 20000, seed=203)),
                 ('crit3', lambda C: fz.critical_fuzz(C, law, 20000, seed=303)),
                 ('fuzz4', lambda C: fz.fuzz(C, law, rules, 20000, seed=104)),
                 ('clos4', lambda C: fz.closure_fuzz(C, law, 20000, seed=204)),
                 ('crit4', lambda C: fz.critical_fuzz(C, law, 20000, seed=304)),
                 ('fuzz7', lambda C: fz.fuzz(C, law, rules, 20000, seed=107)),
                 ('clos7', lambda C: fz.closure_fuzz(C, law, 20000, seed=207)),
                 ('crit7', lambda C: fz.critical_fuzz(C, law, 20000, seed=307))):
    C = cf.Closed(law, rules)
    mk(C)
    for (u, v) in list(C.memo.keys()):
        b = branch(C, u, v)
        if b and len(byb[b]) < 400:
            byb[b].append((u, v))
random.seed(20260829)
POOL = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))]
BIG = []
while len(BIG) < 8:
    t = rand_term(random.choice([4, 4, 5]))
    if 12 <= size(t) <= 130:
        BIG.append(t)
POOL += BIG
found = []
for b, prs in sorted(byb.items()):
    for (u, v) in prs:
        for slot in ('zy', 'yx', 'xy', 'zx', 'yz'):
            for t in POOL:
                C = cf.Closed(law, rules)
                s = ({'x': t, 'y': v, 'z': u} if slot == 'zy' else
                     {'x': v, 'y': u, 'z': t} if slot == 'yx' else
                     {'x': u, 'y': v, 'z': t} if slot == 'xy' else
                     {'x': v, 'y': t, 'z': u} if slot == 'zx' else
                     {'x': t, 'y': u, 'z': v})
                try:
                    got = C.op(C.evp(A, s), C.evp(B, s))
                except RecursionError:
                    continue
                if got != s['x']:
                    found.append((b, slot, s, got))
print('FAILURES', len(found))
found.sort(key=lambda f: size(f[2]['x']) + size(f[2]['y']) + size(f[2]['z']))
for (b, slot, s, got) in found[:2]:
    x, y, z = s['x'], s['y'], s['z']
    C = cf.Closed(law, rules)
    a = C.op(y, x); bb = C.op(x, a); c = C.op(z, y); d = C.op(bb, c); r = C.op(y, d)
    print('--- b=%d slot=%s |x|=%d |y|=%d |z|=%d' % (b, slot, size(x), size(y), size(z)))
    print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
    print('  A=op(y,x) br%d sz%d  B=op(x,A) br%d sz%d  C=op(z,y) br%d sz%d  D=op(B,C) br%d sz%d  TOP br%d'
          % (branch(C, y, x), size(a), branch(C, x, a), size(bb), branch(C, z, y), size(c),
             branch(C, bb, c), size(d), branch(C, y, d)))
    print('  got sz%d  want sz%d  equal=%s' % (size(r), size(x), r == x))
    print('  C free? ', c == ('J', z, y), '  D free?', d == ('J', bb, c))

import json
json.dump([[list(map(str,[])) or None] for _ in []], open('x','w')) if False else None
import pickle
pickle.dump([f[2] for f in found[:3]], open(HERE + '/gen/_v11081_fail.pkl','wb'))
print('dumped', len(found[:3]))
