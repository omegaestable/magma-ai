"""Repaired free model for law 12234  x = y * (((z * x) * y) * (x * y)).
Encoder accessor:  oc t = t.2.2 if sz t.1 < sz t.2.2 else t.1.2   (the free half of an encoding is the big one).
Usage: python gen/rep12234.py [N deep] [N pool-coincidence]
"""
import sys, random, time
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.setrecursionlimit(20000)
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
law = normalise(parse_eq(catalog()[12234]))

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def isJ(t): return t[0] == 'J'
def a1(t): return t[1] if isJ(t) else t
def a2(t): return t[2] if isJ(t) else t
def oc(t): return a2(a2(t)) if size(a1(t)) < size(a2(a2(t))) else a2(a1(t))
def msr(a, b):
    m = max(size(a), size(b)); return m * m + size(a) + size(b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

class Model:
    def __init__(self): self.memo = {}; self.fired = {}
    def op(self, u, v):
        key = (u, v); r = self.memo.get(key)
        if r is not None: return r
        def call(a, b): return self.op(a, b) if msr(a, b) < msr(u, v) else J(u, v)
        k = 0; res = None
        if isJ(v) and isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v)) and isJ(a2(v)) and a2(a1(a1(v))) == a1(a2(v)) and u == a2(a2(v)):
            k, res = 1, a2(a1(a1(v)))
        elif isJ(v) and isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v)) and a2(v) == call(a2(a1(a1(v))), u):
            k, res = 2, a2(a1(a1(v)))
        elif isJ(v) and isJ(a1(v)) and u == a2(a1(v)) and isJ(a2(v)) and u == a2(a2(v)) and a1(a1(v)) == call(oc(a1(a2(v))), a1(a2(v))):
            k, res = 3, a1(a2(v))
        elif isJ(v) and isJ(a1(v)) and u == a2(a1(v)) and isJ(u) and a2(v) == call(oc(u), u) and a1(a1(v)) == call(oc(oc(u)), oc(u)):
            k, res = 4, oc(u)
        elif isJ(v) and isJ(a2(v)) and u == a2(a2(v)) and isJ(u) and a1(v) == call(oc(u), u) and isJ(oc(u)) and a1(a2(v)) == a2(oc(u)):
            k, res = 5, a1(a2(v))
        elif isJ(v) and isJ(a2(v)) and u == a2(a2(v)) and isJ(u) and a1(v) == call(oc(u), u) and oc(u) == call(oc(a1(a2(v))), a1(a2(v))):
            k, res = 6, a1(a2(v))
        else:
            res = J(u, v)
        if k: self.fired[k] = self.fired.get(k, 0) + 1
        self.memo[key] = res
        return res
    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))
    def enc(self, x, y, z):
        return self.evp(law[1], {'x': x, 'y': y, 'z': z})
    def encD(self, w, u, q):
        return self.op(self.op(self.op(q, w), u), self.op(w, u))

M = Model()
# 1. the old counterexample
Ap = J(g(4), g(2)); z = J(J(J(g(3), g(0)), Ap), J(g(0), Ap)); x = J(g(0), J(g(2), z)); y = g(1)
print('old CE now:', 'OK' if M.enc(x, y, z) == x else 'STILL FAILS')
# 2. the generator's deep tests
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
t0 = time.time()
tested, fails = cf.deep_tests(M, law, N, 600, 11)
print('deep_tests', tested, 'fails', len(fails), 'in %.0fs' % (time.time() - t0), 'fired', M.fired)
for s, r in fails[:3]:
    print({k: show(v) for k, v in s.items()}, '->', show(r) if isinstance(r, tuple) else r)
# 3. pool-coincidence tests: small pools so encoders/payloads coincide often
N2 = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
fails2 = []; t0 = time.time(); done = 0
for seed in range(1, 9):
    random.seed(seed)
    pool = [g(i) for i in range(3)] + [rand_term(2) for _ in range(4)]
    for it in range(N2 // 8):
        a, b, c = (random.choice(pool) for _ in range(3))
        if max(size(a), size(b), size(c)) > 90:
            pool = [t for t in pool if size(t) <= 40] or [g(0)]
            continue
        A = M.op(c, a); B = M.op(A, b); C = M.op(a, b); D = M.op(B, C); R = M.op(b, D)
        done += 1
        if R != a: fails2.append(((a, b, c), R)); break
        for t in (A, B, C, D):
            if size(t) <= 60 and random.random() < 0.5: pool.append(t)
        if len(pool) > 24: pool.pop(random.randrange(len(pool)))
        # also: y encodes by x, or by A, or by (q*x): the derailments the rules must handle
        if random.random() < 0.3:
            w, q = random.choice(pool), random.choice(pool)
            enc = M.encD(w, a, q)
            if size(enc) <= 60: pool.append(enc)
    if fails2: break
print('pool tests', done, 'fails', len(fails2), 'in %.0fs' % (time.time() - t0), 'fired', M.fired)
for (a, b, c), r in fails2[:3]:
    print('x =', show(a)); print('y =', show(b)); print('z =', show(c)); print('->', show(r))
# 4. goal refutation at generators
gx, gy, gz = g(2), g(0), g(1)
rhs = M.op(M.op(gy, M.op(gz, gy)), M.op(M.op(gx, gx), gy))
print('goal 22818 refuted at (g2,g0,g1):', rhs != gx, show(rhs))
