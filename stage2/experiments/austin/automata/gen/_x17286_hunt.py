"""_x17286_hunt.py -- how bad is the hole?  collect failures over many seeds and classify."""
import sys, os, itertools, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
RULES = cf.Extractor(law).rules(exist=False)
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)


def show(t, cap=40):
    if size(t) > cap: return '<sz%d>' % size(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1], 9999), show(t[2], 9999))


def evalchain(C, x, y, z):
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    cell = ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q)))
    return top, cell, (A, P, Q, B)


# ---- 1. the diagonal x=y=z over all one-and-two-generator terms up to size 11
def terms(maxsz, gens):
    out = {1: [g(i) for i in range(gens)]}
    for n in range(2, maxsz + 1):
        cur = []
        for a in range(1, n):
            b = n - 1 - a
            if b < 1: continue
            for t1 in out.get(a, ()):
                for t2 in out.get(b, ()):
                    cur.append(J(t1, t2))
        out[n] = cur
    return [t for n in sorted(out) for t in out[n]]


for gens, mx in ((1, 13), (2, 9)):
    T = terms(mx, gens)
    bad = []
    for w in T:
        C = cf.Closed(law, RULES)
        try:
            top, cell, _ = evalchain(C, w, w, w)
        except RecursionError:
            continue
        if top != w: bad.append((w, cell))
    print('diagonal x=y=z, %d gens, sz<=%d: %d terms, %d fails' % (gens, mx, len(T), len(bad)))
    for w, cell in bad[:6]:
        print('    cell=%s w=%s sz=%d' % (cell, show(w), size(w)))

# ---- 2. random deep tests over many seeds, closed model
tot = 0; fails = []
for sd in range(20, 40):
    C = cf.Closed(law, RULES)
    t, f = cf.deep_tests(C, law, 1500, 60, sd)
    tot += t
    for s, r in f:
        fails.append((sd, s, r))
print('deep tests: %d run, %d fails' % (tot, len(fails)))
seen = {}
for sd, s, r in fails:
    if r == 'recursion':
        seen['recursion'] = seen.get('recursion', 0) + 1; continue
    key = (s['x'] == s['y'], s['x'] == s['z'], s['y'] == s['z'])
    C = cf.Closed(law, RULES)
    try:
        top, cell, _ = evalchain(C, s['x'], s['y'], s['z'])
    except RecursionError:
        cell = '?'
    k = (key, cell)
    seen[k] = seen.get(k, 0) + 1
for k in sorted(seen, key=str): print('   ', k, seen[k])

# a couple of representative failing instances
shown = 0
for sd, s, r in fails:
    if r == 'recursion': continue
    if shown >= 4: break
    shown += 1
    print('  FAIL seed=%d x==y:%s x==z:%s y==z:%s' % (sd, s['x'] == s['y'], s['x'] == s['z'], s['y'] == s['z']))
    for k in ('x', 'y', 'z'):
        print('     %s = %s (sz %d)' % (k, show(s[k]), size(s[k])))
    F = fm.Free(law)
    try:
        sA = F.op(s['y'], s['x']); sP = F.op(s['x'], s['z']); sQ = F.op(s['z'], sP)
        sB = F.op(s['z'], sQ); stop = F.op(sA, sB)
        print('     SEM ok=%s conflicts=%d' % (stop == s['x'], len(F.conflicts)))
    except Exception as e:
        print('     SEM ERR', repr(e)[:80])
