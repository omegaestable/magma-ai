"""Is the cell (p decoded AND r decoded) reachable for 23354?
p = op y x decodes  <=> (y,x) is a decoding pair;  r = op x z decodes <=> (x,z) is one.
So collect all decoding pairs over a pool and look for an x that is the RIGHT arg of one and
the LEFT arg of another.  If such an x exists, check whether a1 (a1 z) = x (which is what the
only possible top rule, R3, demands) and evaluate the law."""
import sys, os, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 23354
law = normalise(parse_eq(catalog()[EQ]))
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
src = open(GEN + 'chk23354.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); RULES = ns['rules']
C = cf.Closed(law, RULES)
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 11
NG = int(sys.argv[2]) if len(sys.argv) > 2 else 2
by = {1: [g(i) for i in range(NG)]}
for n in range(3, MAX + 1, 2):
    by[n] = [J(s, t) for a in range(1, n - 1, 2) for s in by[a] for t in by.get(n - 1 - a, [])]
pool = [t for n in sorted(by) for t in by[n]]
print('pool %d terms (size <= %d, %d gens)' % (len(pool), MAX, NG), flush=True)

# decoding pairs, with a size cap to keep it quadratic-but-small
D = []
for u in pool:
    for v in pool:
        if size(u) + size(v) > MAX + 6: continue
        if C.op(u, v) != J(u, v): D.append((u, v))
print('decoding pairs: %d' % len(D), flush=True)
rights = {}
for u, v in D: rights.setdefault(v, []).append(u)
lefts = {}
for u, v in D: lefts.setdefault(u, []).append(v)
common = set(rights) & set(lefts)
print('terms that are BOTH a right arg and a left arg of a decoding pair: %d' % len(common), flush=True)
n_bad = 0
for x in sorted(common, key=size):
    for y in rights[x]:
        for z in lefts[x]:
            p = C.op(y, x); q = C.op(p, y); r = C.op(x, z); s = C.op(x, r); top = C.op(q, s)
            ok = (top == x)
            r3 = (r[0] == 'J' and r[1] == x)
            if not ok or n_bad < 3:
                print('  x=%s y=%s z=%s  p=%s r=%s  a1(r)==x:%s  LAW %s' % (
                    sh(x), sh(y), sh(z), sh(p), sh(r), r3, 'ok' if ok else '**FAIL**'), flush=True)
            if not ok: n_bad += 1
print('cell instances checked, failures: %d' % n_bad)
