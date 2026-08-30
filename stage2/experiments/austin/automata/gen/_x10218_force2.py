# -*- coding: utf-8 -*-
"""10218 FORCED FIRING, corrected.  The first attempt (gen/_x10218_force.py) was VACUOUS: every
construction fired R1, because the inner product it used was free and then P1 holds too.  A rule
R2..R6 only fires when the product inside its own guard is DECODED, so each constructor below builds
that inner product as an encoding.  The census is printed beside the failure count (coordinator).

enc(P,u,Q) = J (J P u) (J (J Q P) u)   and   op u (enc P u Q) = P     [rule R1]
"""
import sys, os, itertools, collections, importlib.util
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
C = W(law, rules); op = C.op
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def enc(P, u, Q): return J(J(P, u), J(J(Q, P), u))

base = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2))]
JUNK = [g(7), J(g(7), J(g(8), J(g(9), g(7)))), enc(g(5), g(6), g(7))]

# --- v-constructors that force each rule by making the guard's inner product DECODE -------------
def V2(u, Pp, B, Q):
    """R2: P := enc(Pp,B,Q) so op B P = Pp (decoded);  v := J (J P u) (J Pp u)."""
    P = enc(Pp, B, Q); return J(J(P, u), J(Pp, u)), P
def U3V3(A2, P, Wt, Q):
    """R3: u := enc(Wt, J A2 P, Q) so op (a2 (a1 u)) u = Wt (decoded); v := J (J P u) Wt."""
    m = J(A2, P); u = enc(Wt, m, Q); return u, J(J(P, u), Wt), P
def V5(u, P, Q, D):
    """R5: make op P u decode -> u := enc(D,P,Q2) so op P u = D;  v := J D (J (J Q P) u)."""
    return J(op(P, u), J(J(Q, P), u)), P
def U6V6(A1, Rp, Bq, Qq, A3):
    """R6: R := enc(Rp,Bq,Qq) so op (a2 (a1 R)) R = op Bq R = Rp;  u := J (J A1 R) A3,
       v := J (op R u) (J Rp u).  result a2 (a1 u) = R."""
    R = enc(Rp, Bq, Qq); u = J(J(A1, R), A3)
    return u, J(op(R, u), J(Rp, u)), R

tab = collections.Counter(); bad = []; n = 0
def cell(x, y, z):
    t1 = op(x, y); t2 = op(z, x); t3 = op(t2, y); t4 = op(t1, t3); t5 = op(y, t4)
    m = []
    for a, val in (((x, y), t1), ((z, x), t2), ((t2, y), t3), ((t1, t3), t4), ((y, t4), t5)):
        m.append('F' if val == J(*a) else 'R%d' % (WH.get(a, -1) + 1))
    return tuple(m), t5
def run(x, y, z, tag):
    global n
    try: m, t5 = cell(x, y, z)
    except RecursionError: return
    n += 1; tab[(tag,) + m] += 1
    if t5 != x: bad.append((tag, x, y, z, m, t5))

for Pp, B, Q, u in itertools.product(base[:4], base[:3], base[:3], base[:3]):
    v, P = V2(u, Pp, B, Q)
    run(u, v, Q, 'force-t1-R2'); run(v, base[0], u, 'force-t2-R2')
    for zz in base[:3]:
        t2 = op(zz, base[0])
        vv, _ = V2(t2, Pp, B, Q)
        run(base[0], vv, zz, 'force-t3-R2')
for A2, P, Wt, Q in itertools.product(base[:3], base[:4], base[:3], base[:3]):
    u, v, res = U3V3(A2, P, Wt, Q)
    run(u, v, Q, 'force-t1-R3'); run(v, base[0], u, 'force-t2-R3')
for P, Q, u in itertools.product(base[:4], base[:3], base[:3]):
    for D in base[:3]:
        uu = enc(D, P, Q)                        # op P uu = D (decoded)
        v, _ = V5(uu, P, Q, D)
        run(uu, v, Q, 'force-t1-R5'); run(v, base[0], uu, 'force-t2-R5')
for A1, Rp, Bq, Qq, A3 in itertools.product(base[:3], repeat=5):
    u, v, res = U6V6(A1, Rp, Bq, Qq, A3)
    run(u, v, Qq, 'force-t1-R6'); run(v, base[0], u, 'force-t2-R6')
# R4: the guard chain needs BOTH inner products decoded
for A, B, Cc, A1, A3 in itertools.product(base[:3], repeat=5):
    P = enc(A, B, Cc); Wv = op(B, P)             # decoded
    u = J(J(A1, Wv), A3)
    v = J(J(P, u), op(Wv, u))
    run(u, v, Cc, 'force-t1-R4'); run(v, base[0], u, 'force-t2-R4')
print('corrected forced firing: %d assignments, %d law failures' % (n, len(bad)), flush=True)
print()
print('CELL CENSUS  (tag, t1..t5)  -- check the intended rule actually fires:')
seen = collections.Counter()
for k, c in sorted(tab.items(), key=lambda kv: (kv[0][0], -kv[1])):
    seen[k[0]] += c
    print('  %-16s %-30s %d' % (k[0], str(k[1:]), c))
print()
print('LAW FAILURES', len(bad))
for tag, x, y, z, m, r in bad[:4]:
    print('  [%s] %s' % (tag, str(m)))
    print('    x =', show(x)[:220]); print('    y =', show(y)[:220])
    print('    z =', show(z)[:220]); print('    got =', show(r)[:220])
