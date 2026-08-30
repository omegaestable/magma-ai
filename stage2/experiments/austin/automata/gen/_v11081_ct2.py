"""CASE TREE v2 for law 11081 -- adds the two wave-3 validation requirements added mid-shift:

(1) VARY THE JUNK VARIABLE.  11081 is  x = y * ((x * (y*x)) * (z*y)) ; `z` occurs once, only in `z*y`,
    so z is the law's junk variable, and inside an encoding the junk slot is `a1 (a2 v)` (rule K1 pins
    only `a2 (a2 v) = u`).  Both are now filled with LARGE terms.
(2) EACH RULE AT EVERY CHAIN PRODUCT.  encK1/encK2a/encK2b build a term that decodes to p under key u
    BY THAT RULE; each is planted at every slot of the chain (x, y, z) and at the B/C/D positions.

usage: python gen/_v11081_ct2.py <setname> [--verbose]
"""
import sys, os, collections, itertools, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from _v11081_rs import SETS

law = normalise(parse_eq(catalog()[11081]))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'w123'
rules = SETS[NAME]
print('rule set', NAME)
for r in rules:
    print('  ', cf.show_rule(r))

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
a1_ = lambda t: t[1] if t[0] == 'J' else t
a2_ = lambda t: t[2] if t[0] == 'J' else t
show = lambda t: 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i + 1
    return 0


mark = lambda C, u, v: ('D%d' % branch(C, u, v)) if branch(C, u, v) else '.'
C0 = cf.Closed(law, rules)

# ---- the three rule-specific encodings: op u (encKk p u ...) = p, fired by rule k ----
encK1 = lambda p, u, w: J(J(p, C0.op(u, p)), J(w, u))                      # a2 v = J w u
encK2a = lambda p, u: J(J(p, C0.op(u, p)), C0.op(a1_(a2_(a1_(u))), u))     # a2 v = op (a1(a2(a1 u))) u
encK2b = lambda p, u: J(J(p, C0.op(u, p)), C0.op(a2_(a2_(u)), u))          # a2 v = op (a2(a2 u)) u

SMALL = [g(0), g(1), g(2), J(g(0), g(1)), J(J(g(0), g(1)), g(2))]
# LARGE junk: deliberately big, structurally varied terms
BIG = [rand_term(4) for _ in range(4)] + [rand_term(5) for _ in range(3)]
random.seed(20260829)
BIG = [t for t in BIG if 15 <= size(t) <= 120] or [rand_term(4) for _ in range(4)]
JUNK = SMALL + BIG
print('junk pool sizes:', sorted(size(t) for t in JUNK))

cells = collections.defaultdict(list)
fails = []
tested = 0


def probe(x, y, z, note):
    global tested
    if size(x) + size(y) + size(z) > 1400:
        return
    C = cf.Closed(law, rules)
    try:
        a = C.op(y, x); b = C.op(x, a); c = C.op(z, y); d = C.op(b, c); r = C.op(y, d)
    except RecursionError:
        return
    tested += 1
    key = (mark(C, y, x), mark(C, x, a), mark(C, z, y), mark(C, b, c))
    cells[key].append((note, mark(C, y, d)))
    if r != x:
        fails.append((note, key, x, y, z, r))


# ---------- (1) large junk in every slot ----------
for w in JUNK:                                   # junk slot of an encoding
    for kk in SMALL[:3]:
        y1 = encK1(g(0), kk, w)                  # C = op(kk, y1) decodes, junk = w
        for zz in [kk] + JUNK[:3] + BIG[:2]:
            for x in SMALL[:3] + [encK1(g(1), y1, w)]:
                probe(x, y1, zz, 'junk-enc')
for z in JUNK:                                   # the law's own junk variable, large
    for y in SMALL[:3] + [encK1(g(0), g(1), g(2)), encK1(g(0), g(1), BIG[0])]:
        for x in SMALL[:3] + [encK1(g(1), y, BIG[0]), encK1(g(1), y, g(0))]:
            probe(x, y, z, 'junk-z')

# ---------- (2) every rule at every chain product ----------
KEYS = [encK1(q, k, w) for q in SMALL[:2] for k in SMALL[:2] for w in SMALL[:2] + BIG[:1]]
ENCS = []
for p in SMALL[:3]:
    for u in SMALL[:3]:
        for w in SMALL[:2] + BIG[:1]:
            ENCS.append(('K1', p, u, encK1(p, u, w)))
    for u in KEYS:
        ENCS.append(('K2a', p, u, encK2a(p, u)))
        ENCS.append(('K2b', p, u, encK2b(p, u)))
ENCS = [(t, p, u, v) for (t, p, u, v) in ENCS if size(v) <= 300]
hit = collections.Counter()
for (t, p, u, v) in ENCS:
    C = cf.Closed(law, rules)
    hit[(t, branch(C, u, v))] += 1
print('encoding builders: (tag, branch that actually fires) ->', dict(hit))

# plant each encoding at x, y and z, with the matching key in the other slots
for (t, p, u, v) in ENCS:
    for other in SMALL[:3] + [u, p]:
        probe(v, u, other, 'enc-at-x:' + t)      # x = v: A = op(y,x) may decode
        probe(other, v, u, 'enc-at-y:' + t)      # y = v: C = op(z,y) may decode
        probe(other, u, v, 'enc-at-z:' + t)      # z = v
        probe(v, other, u, 'enc-at-x2:' + t)
# force B and D: B = J x (op y x), C = op z y ; plant an encoding whose key is B or C
for (t, p, u, v) in ENCS[:40]:
    for x in SMALL[:3] + [u]:
        C = cf.Closed(law, rules)
        a = C.op(u, x); b = C.op(x, a)
        # z chosen so that C = op z u is a term whose payload chain forces D to look at B
        for zz in SMALL[:3] + [b, J(p, C.op(b, p))]:
            probe(x, u, zz, 'BD:' + t)
        # y = a1 x style (the D-forcing shape)
        if x[0] == 'J':
            for zz in SMALL[:2] + [J(p, C.op(b, p))]:
                probe(x, a1_(x), zz, 'BDa:' + t)

print('\ntested %d constructed instances, %d law failures' % (tested, len(fails)))
print('%-4s %-4s %-4s %-4s  %s' % ('A', 'B', 'C', 'D', 'count / TOP marks / notes'))
for k in sorted(cells, key=lambda k: -len(cells[k])):
    tops = collections.Counter(t for _, t in cells[k])
    notes = collections.Counter(n.split(':')[0] for n, _ in cells[k])
    print('%-4s %-4s %-4s %-4s  %5d  TOP=%-22s %s' % (k[0], k[1], k[2], k[3], len(cells[k]),
                                                      str(dict(tops)), dict(notes)))
fails.sort(key=lambda f: size(f[2]) + size(f[3]) + size(f[4]))
for (note, key, x, y, z, r) in fails[:3]:
    print('\nLAW FAILS note=%s cell=%s sizes x=%d y=%d z=%d' % (note, key, size(x), size(y), size(z)))
    print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z)); print('  got =', show(r))
