"""Coincidence-targeted check of the 5837 rule set (single process, time-capped).
Pool = generators, their products, `inner(a,b) = a*((b*a)*a)` (the part of an encoding after the payload)
and `enc(p,u,w) = p*(u*((w*u)*u))` (so that u*enc = p by the law), all evaluated in the model; then the law
is tested on every triple (x,y,z) of the level-1 pool, and on triples whose y (and z) are level-2 encodings.
Prints the distinct failures with the last-step shape."""
import sys, os, time, random, itertools
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[5837]))
rules = [([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('TG', ('A1', ('A2', ('A2', ('V',))))), ('EQ', ('U',), ('A2', ('A1', ('A2', ('A2', ('V',)))))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',)))))], ('A1', ('V',)), 'free'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',))))), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A1', ('A2', ('A2', ('V',)))))], ('A1', ('V',)), 'B110l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A2', ('A2', ('V',)))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A1', ('A2', ('U',))))], ('A1', ('V',)), 'B11l,B110l')]
C = cf.Closed(law, rules)
A, B = law[1]

def g(n): return ('g', n)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))
def op(a, b): return C.op(a, b)
def inner(a, b): return op(a, op(op(b, a), a))            # a*((b*a)*a)
def enc(p, u, w): return op(p, inner(u, w))               # p*(u*((w*u)*u)); law: u*enc = p

def lawval(x, y, z):
    q1 = op(z, y); q2 = op(q1, y); q3 = op(y, q2); q4 = op(x, q3); return op(y, q4), (q1, q2, q3, q4)

t0 = time.time()
base = [g(0), g(1), g(2)]
P1 = list(base)
for a in base:
    for b in base:
        for t in (op(a, b), inner(a, b)):
            if t not in P1: P1.append(t)
for a in base:
    for b in base:
        for c in base:
            t = enc(a, b, c)
            if t not in P1: P1.append(t)
print('level-1 pool', len(P1))
fails = {}
def test(x, y, z, tag):
    if max(size(x), size(y), size(z)) > 200: return
    r, q = lawval(x, y, z)
    if r != x:
        key = (show(x), show(y), show(z))
        if key not in fails:
            fails[key] = (tag, show(r), [show(t) for t in q])
n = 0
for x in P1:
    for y in P1:
        for z in P1:
            test(x, y, z, 'L1'); n += 1
print('level-1 triples', n, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
# level 2: y (and z) encodings built from level-1 terms
random.seed(5837)
P2 = []
for _ in range(400):
    p, u, w = random.choice(P1), random.choice(P1), random.choice(P1)
    for t in (enc(p, u, w), inner(p, u)):
        if t not in P2 and t not in P1 and size(t) <= 150: P2.append(t)
print('level-2 pool', len(P2))
n2 = 0
for y in P2:
    for x in base + P1[3:12]:
        for z in P1:
            test(x, y, z, 'L2y'); n2 += 1
        for z in P2[:60]:
            test(x, y, z, 'L2yz'); n2 += 1
    if time.time() - t0 > 240: print('time cap hit'); break
print('level-2 triples', n2, 'fails total', len(fails), 'secs', round(time.time() - t0, 1))
for i, (k, v) in enumerate(list(fails.items())[:12]):
    print('FAIL[%s] x=%s\n   y=%s\n   z=%s\n   result=%s\n   q1..q4=%s' % (v[0], k[0], k[1], k[2], v[1], ' | '.join(v[2])))
print('distinct failing triples:', len(fails))
