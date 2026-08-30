# -*- coding: utf-8 -*-
"""Reproduce and verify the level-2 descent failure of 21864's rule sets (variant B)."""
import sys, os, json, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
import _x21864_rules as RR

law = normalise(parse_eq(catalog()[21864]))
T8 = RR.GEN[:5] + [RR.R4c, RR.R5c, RR.RA, RR.R6d, RR.R6e, RR.RB, RR.RB2, RR.RD]
SETS = {'gen9': RR.GEN, 'ship11': [r for i, r in enumerate(T8) if i not in {2, 8}], 't8_13': T8}
J = lambda a, b: ('J', a, b)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

d = json.load(open(os.path.join(HERE, '_p2_deep321864_bad.json')))
tup = lambda t: tuple(tup(c) if isinstance(c, list) else c for c in t)
x, y, z = tup(d['x']), tup(d['y']), tup(d['z'])
print('instance from', d['set'], 'levels', d['levels'])
print('  x = %s   (size %d)' % (show(x), size(x)))
print('  y = %s   (size %d)' % (show(y), size(y)))
print('  z = %s   (size %d)' % (show(z), size(z)))
print()
for nm, rules in SETS.items():
    C = cf.Closed(law, rules)                     # FRESH evaluator, no shared memo
    P = C.op(z, x); u = C.op(y, P); Q = C.op(x, y); v = C.op(x, Q); top = C.op(u, v)
    def tag(a, b, r): return 'FREE' if r == J(a, b) else 'DEC'
    print('%-7s cycles=%d' % (nm, C.cycles))
    print('   P = op(z,x) = %-58s [%s]' % (show(P)[:58], tag(z, x, P)))
    print('   u = op(y,P) = %-58s [%s]' % (show(u)[:58], tag(y, P, u)))
    print('   Q = op(x,y) = %-58s [%s]' % (show(Q)[:58], tag(x, y, Q)))
    print('   v = op(x,Q) = %-58s [%s]' % (show(v)[:58], tag(x, Q, v)))
    print('   top         = %-58s %s' % (show(top)[:58], 'OK' if top == x else '**LAW FAILS**'))
    if top != x:
        print('   want x      = %s' % show(x)[:58])
        okr = [i + 1 for i, q in enumerate(rules) if C.check(q[0], u, v)]
        print('   rules whose guard holds on the top pair:', okr or 'NONE -> the top product is FREE')
    print()
