# -*- coding: utf-8 -*-
"""10218 oracles: FORCED FIRING (each rule's own precondition, placed at every chain product) and
LEVEL-k DESCENT (deep nesting + large junk).  Model: gen/rep10218/ (6 rules).

law (not dualized):  x = y * ((x*y) * ((z*x)*y))
chain:  t1 = op x y   t2 = op z x   t3 = op t2 y   t4 = op t1 t3   t5 = op y t4  ( = x )
"""
import sys, os, itertools, collections, importlib.util, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[10218]))
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'gen', 'rep10218', 'chk10218.py'))
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}; exec(compile(src, spec.origin, 'exec'), ns); rules = ns['rules']
WH = {}
class W(cf.Closed):
    def op(self, u, v):
        k = (u, v)
        if k in self.memo: return self.memo[k]
        r = super().op(u, v)
        if r != ('J', u, v) and k not in WH:
            for i, rl in enumerate(rules):
                s = cf.Closed(law, rules); s.memo = self.memo
                if s.check(rl[0], u, v): WH[k] = i; break
            else: WH[k] = -1
        return r
C = W(law, rules)
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
op = C.op

# ---- v-constructors: V_k(u, params) returns a v on which rule k is meant to fire -------------
def V1(u, P, Q): return J(J(P, u), J(J(Q, P), u))                      # enc(P,u,Q); result P
def V2(u, A, B, Cc, Q):
    P = J(J(A, B), Cc)                                                 # tg P, tg (a1 P)
    S = op(B, P)                                                       # a2 (a1 P) = B
    return J(J(P, u), J(S, u))                                         # result P
def V3u(A1, A2, P, A3): return J(J(A1, J(A2, P)), A3)                  # the u for rule 3
def V3(u, P): return J(J(P, u), op(a2(a1(u)), u))                      # result P
def V4pair(A, B, Cc, A1, A3):
    P = J(J(A, B), Cc); Wv = op(B, P); u = J(J(A1, Wv), A3)
    return u, J(J(P, u), op(a2(a1(u)), u))                             # result P
def V5(u, P, Q): return J(op(P, u), J(J(Q, P), u))                     # result P
def V6pair(A1, R, A3):
    u = J(J(A1, R), A3)
    return u, J(op(R, u), J(op(a2(a1(R)), R), u))                      # result R

base = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2)), J(J(g(0), g(1)), g(2))]
JUNK = [g(7), J(g(7), J(g(8), J(g(9), g(7)))), V1(g(5), g(6), g(7)),
        J(J(J(g(5), g(6)), J(g(7), g(8))), J(g(9), g(5)))]            # LARGE JUNK pool

def cell(x, y, z):
    t1 = op(x, y); t2 = op(z, x); t3 = op(t2, y); t4 = op(t1, t3); t5 = op(y, t4)
    m = []
    for a, val in (((x, y), t1), ((z, x), t2), ((t2, y), t3), ((t1, t3), t4), ((y, t4), t5)):
        m.append('F' if val == J(*a) else 'R%d' % (WH.get(a, -1) + 1))
    return tuple(m), t5

tab = collections.Counter(); bad = []; n = 0
def run(x, y, z, tag):
    global n
    try:
        m, t5 = cell(x, y, z)
    except RecursionError:
        return
    n += 1; tab[(tag,) + m] += 1
    if t5 != x: bad.append((tag, x, y, z, m, t5))

# ---- FORCED FIRING: put each rule's firing shape at t1 (u=x,v=y), t2 (u=z,v=x), t3 (u=t2,v=y) --
for P, Q, u in itertools.product(base[:5], base[:4], base[:4]):
    for j, (y, x, z) in enumerate([(V1(u, P, Q), u, Q), (V5(u, P, Q), u, Q)]):
        run(x, y, z, 'force-t1-R%d' % (1 if j == 0 else 5))          # v=y, u=x
    for zz in base[:4]:                                               # v=x, u=z : t2 decodes
        run(V1(zz, P, Q), base[0], zz, 'force-t2-R1')
        run(V5(zz, P, Q), base[0], zz, 'force-t2-R5')
for A, B, Cc, Q in itertools.product(base[:4], repeat=4):
    for u in base[:3]:
        run(u, V2(u, A, B, Cc, Q), Q, 'force-t1-R2')
        run(V2(u, A, B, Cc, Q), base[0], u, 'force-t2-R2')
for A1, A2v, P, A3 in itertools.product(base[:4], repeat=4):
    u = V3u(A1, A2v, P, A3)
    run(u, V3(u, P), base[0], 'force-t1-R3')
    run(V3(u, P), base[0], u, 'force-t2-R3')
for A, B, Cc, A1 in itertools.product(base[:3], repeat=4):
    for A3 in base[:3]:
        u, v = V4pair(A, B, Cc, A1, A3)
        run(u, v, base[0], 'force-t1-R4'); run(v, base[0], u, 'force-t2-R4')
for A1, R, A3 in itertools.product(base[:4], repeat=3):
    u, v = V6pair(A1, R, A3)
    run(u, v, base[0], 'force-t1-R6'); run(v, base[0], u, 'force-t2-R6')
# t3 = op t2 y : choose x,z first, compute t2, then build y so that rule k fires at (t2,y)
for x, z, P, Q in itertools.product(base[:4], base[:4], base[:4], base[:3]):
    t2 = op(z, x)
    run(x, V1(t2, P, Q), z, 'force-t3-R1')
    run(x, V5(t2, P, Q), z, 'force-t3-R5')
print('forced firing: %d assignments, %d law failures' % (n, len(bad)), flush=True)

# ---- LEVEL-k DESCENT: y encodes x, whose payload is itself an encoding, k levels deep; large junk
n0 = n
for k in (1, 2, 3, 4):
    for q in JUNK:
        for x0 in base[:3]:
            P = x0
            for _ in range(k):
                P = V1(g(4), P, q)           # P is an encoding whose decoder-role is g4
            for zz in base[:3]:
                run(P, V1(P, P, q), zz, 'descent-%d' % k)
                run(P, V1(g(4), P, q), zz, 'descent-%d-alt' % k)
                run(x0, V1(x0, P, q), zz, 'descent-%d-junk' % k)
print('descent+junk: %d more assignments, %d law failures total' % (n - n0, len(bad)), flush=True)
print()
print('CELL CENSUS (tag, t1..t5):')
for k, c in sorted(tab.items(), key=lambda kv: (kv[0][0], -kv[1]))[:40]:
    print('  %-18s %-30s %d' % (k[0], str(k[1:]), c))
print()
print('LAW FAILURES', len(bad))
for tag, x, y, z, m, r in bad[:4]:
    print('  [%s] %s' % (tag, str(m)))
    print('    x =', show(x)[:200]); print('    y =', show(y)[:200])
    print('    z =', show(z)[:200]); print('    got =', show(r)[:200])
