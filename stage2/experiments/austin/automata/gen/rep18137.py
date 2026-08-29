"""rep18137.py [N] [seeds] : validate the REPAIRED 4-rule recursive model for law 18137 against
(a) deep law tests (cf.deep_tests, several seeds), (b) the free model on every pair the tests touched,
(c) exhaustive small pairs vs the free model, (d) the hand coincidence family that broke the skeleton."""
import sys, random, time, itertools
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, Free, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[18137]))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 3

def msr(a, b):
    m = max(size(a), size(b)); return m * m + size(a) + size(b)
def isJ(t): return t[0] == 'J'
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

class Model:
    """op u v: Sh v = (v = J z (J B z)); R1 x=u.2 | R2 x=B.1 | R3 x=J B.2 B | R4 x=op u B, each verified."""
    def __init__(self): self.memo = {}; self.fired = {}
    def gated(self, a, b, u, v):
        if msr(a, b) < msr(u, v): return self.op(a, b)
        return J(u, v)
    def enc(self, a, w, U, V):
        return isJ(w) and isJ(w[2]) and w[1] == w[2][2] and self.gated(a, w[1], U, V) == w[2][1]
    def op(self, u, v):
        k = (u, v); r = self.memo.get(k)
        if r is None:
            r = self._op(u, v); self.memo[k] = r
        return r
    def _op(self, u, v):
        if not (isJ(v) and isJ(v[2]) and v[1] == v[2][2]): return J(u, v)
        z = v[1]; B = v[2][1]
        if isJ(u) and self.gated(u[1], u[2], u, v) == u and self.gated(u[2], z, u, v) == B:
            self.fired[1] = self.fired.get(1, 0) + 1; return u[2]
        if isJ(B) and B[2] == z and self.gated(B[1], z, u, v) == B and self.enc(u, B[1], u, v):
            self.fired[2] = self.fired.get(2, 0) + 1; return B[1]
        if isJ(B) and self.gated(u, B[2], u, v) == B[1] and self.gated(J(B[2], B), z, u, v) == B:
            self.fired[3] = self.fired.get(3, 0) + 1; return J(B[2], B)
        p7 = self.gated(u, B, u, v)
        if p7 != J(u, B) and self.gated(p7, z, u, v) == B:
            self.fired[4] = self.fired.get(4, 0) + 1; return p7
        return J(u, v)
    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))

M = Model()
# (d) the hand family first
x1 = J(g(2), J(J(g(1), g(2)), g(2))); x = J(x1, J(g(1), x1)); y = J(g(3), J(g(0), g(1))); z = g(5)
s = {'x': x, 'y': y, 'z': z}
print('hand instance (skeleton hole): E == x ?', M.evp(law[1], s) == x)
# x = J x1 B family with B non-free (R3 must fire) : A0=(g0 g1), x1 encodes g1 by A0, B = J g1 x1, x = J x1 B, y = J g3 A0, z encodes B by x
A0 = J(g(0), g(1)); B = J(g(1), x1); xx = J(x1, B); yy = J(g(3), A0); zz = J(g(5), J(J(B, g(5)), g(5)))
s = {'x': xx, 'y': yy, 'z': zz}
print('R3 family: op(x,z) == B ?', M.op(xx, zz) == B, ' E == x ?', M.evp(law[1], s) == xx)
# (a) deep tests
tot_fail = 0
for seed in range(1, seeds + 1):
    t0 = time.time()
    tested, fails = cf.deep_tests(M, law, N, 600, seed)
    tot_fail += len(fails)
    print('deep seed', seed, 'tested', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1), 'fired', M.fired, 'memo', len(M.memo))
    for sf, lhs in fails[:3]:
        print('  FAIL', {k: show(v) for k, v in sf.items()}, '->', show(lhs) if isinstance(lhs, tuple) else lhs)
# (b) compare with the free model on touched pairs (bounded sizes)
F = Free(law)
pairs = [k for k in M.memo if size(k[0]) + size(k[1]) <= 60]
random.seed(7); random.shuffle(pairs)
mism = 0; checked = 0; t0 = time.time()
for (u, v) in pairs[:4000]:
    if time.time() - t0 > 240: break
    try:
        fr = F.op(u, v)
    except Exception as e:
        continue
    checked += 1
    if fr != M.memo[(u, v)]:
        mism += 1
        if mism <= 5: print('  MISMATCH u=', show(u), 'v=', show(v), 'model=', show(M.memo[(u, v)]), 'free=', show(fr))
print('free-model comparison on touched pairs: checked', checked, 'mismatches', mism, 'conflicts', len(F.conflicts), 'secs', round(time.time() - t0, 1))
# (c) exhaustive small pairs over {g0,g1}
terms = {1: [g(0), g(1)]}
for n in (3, 5, 7):
    terms[n] = []
    for a in range(1, n - 1, 2):
        b = n - 1 - a
        for ta in terms[a]:
            for tb in terms[b]:
                terms[n].append(J(ta, tb))
allt = [t for n in terms for t in terms[n]]
F2 = Free(law); M2 = Model(); mism2 = 0; nonfree = 0; t0 = time.time()
for u in allt:
    for v in allt:
        if size(u) + size(v) > 12: continue
        a = M2.op(u, v); b = F2.op(u, v)
        if a != J(u, v): nonfree += 1
        if a != b:
            mism2 += 1
            if mism2 <= 5: print('  MISMATCH u=', show(u), 'v=', show(v), 'model=', show(a), 'free=', show(b))
print('exhaustive small pairs: terms', len(allt), 'nonfree', nonfree, 'mismatches', mism2, 'secs', round(time.time() - t0, 1))
print('TOTAL law failures', tot_fail)
