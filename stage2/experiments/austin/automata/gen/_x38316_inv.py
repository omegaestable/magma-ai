"""Invariant probe for the 5-rule V0 model of 38316.

Collects every DECODING pair (u,v) reached while evaluating a large battery of instances and tests
candidate invariants:
  I1  sz v > sz u
  I2  the T-product op (a1 (a2 v)) u is FREE   (i.e. a2 v = J (a1 (a2 v)) u, so a2 (a2 v) = u)
  I3  tg (a2 v) = 2
  I4  sz (a1 v) < sz u        (payload smaller than the decoder argument)
"""
import sys, os, random, itertools
from collections import Counter
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
sel = sys.argv[1] if len(sys.argv) > 1 else 'V0-W1-q0,V0-W1-q1,V0-W2,V0-W3-q0,V0-W3-q1'
RULES = ALL if sel == 'all' else [r for r in ALL if r[2] in sel.split(',')]
C = cf.Closed(law, RULES)
print('rules', [r[2] for r in RULES])

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

viol = Counter(); tot = 0; ex = {}
def note(name, ok, u, v):
    if not ok:
        viol[name] += 1
        if name not in ex:
            ex[name] = (u, v)

def scan():
    global tot
    for (u, v), r in list(C.memo.items()):
        if r == ('J', u, v):
            continue
        tot += 1
        note('I1 sz v > sz u', size(v) > size(u), u, v)
        ok2 = v[0] == 'J' and v[2][0] == 'J' and v[2][2] == u
        note('I2 T-product free (a2(a2 v) = u)', ok2, u, v)
        note('I3 tg (a2 v) = 2', v[0] == 'J' and v[2][0] == 'J', u, v)
        note('I4 sz (a1 v) < sz u', v[0] == 'J' and size(v[1]) < size(u), u, v)
        note('I5 res = a1 v', r == v[1], u, v)

def ENC(u, P, Z):
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)
def CPART(y, Z, P):
    a = C.op(Z, P); b = C.op(y, a); return C.op(b, y)

G = [g(i) for i in range(3)]
terms = list(G)
for _ in range(3):
    new = list(terms)
    for a in terms:
        for b in terms:
            t = J(a, b)
            if size(t) <= 5 and t not in new: new.append(t)
    terms = new
terms = [t for t in terms if size(t) <= 5]
small = [t for t in terms if size(t) <= 3]

def ev(x, y, z):
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); C.op(y, d)
    except RecursionError:
        pass

for x, y, z in itertools.product(terms, repeat=3):
    if size(x) + size(y) + size(z) <= 11:
        ev(x, y, z)
for z, P, Z in itertools.product(small, repeat=3):
    x = ENC(z, P, Z)
    if size(x) <= 120:
        for y in small: ev(x, y, z)
for z, P, Z in itertools.product(small[:6], repeat=3):
    x1 = ENC(z, P, Z)
    if size(x1) <= 60:
        x = ENC(z, x1, Z)
        if size(x) <= 400:
            for y in small[:4]: ev(x, y, z)
for y, Z, z in itertools.product(small, repeat=3):
    x = CPART(y, Z, z)
    if size(x) <= 200: ev(x, y, z)
for w, x, z in itertools.product(terms, small, small):
    y = J(w, x)
    if size(y) <= 8: ev(x, y, z)
random.seed(3)
for _ in range(4000):
    y = random.choice(small); z = random.choice(small); P = random.choice(small); Z = random.choice(small)
    r = random.random()
    if r < 0.34: x = ENC(z, CPART(y, Z, z), P)
    elif r < 0.67: x = CPART(y, Z, ENC(z, P, Z))
    else:
        x = ENC(z, P, Z); y = J(random.choice(small), x)
    if size(x) <= 400 and size(y) <= 400: ev(x, y, z)

scan()
print('decoding pairs seen: %d' % tot)
for k in ('I1 sz v > sz u', 'I2 T-product free (a2(a2 v) = u)', 'I3 tg (a2 v) = 2',
          'I4 sz (a1 v) < sz u', 'I5 res = a1 v'):
    print('  %-36s violations %d' % (k, viol.get(k, 0)))
    if k in ex:
        u, v = ex[k]
        print('      u=%s\n      v=%s' % (sh(u), sh(v)))
