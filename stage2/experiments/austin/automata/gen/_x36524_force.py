# -*- coding: utf-8 -*-
"""36524 forcing suite.  Encoding read OFF ITS OWN R1, not guessed:

  R1 [free]  J?v & J?v.1 & u = v.1.2 & J?v.2 & u = v.2.1 & J?v.2.2 & u = v.2.2.2 -> v.2.2.1
  i.e.  tg v ∧ tg (a1 v) ∧ u = a2 (a1 v) ∧ tg (a2 v) ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) ∧
        u = a2 (a2 (a2 v))   ->   a1 (a2 (a2 v))
  so   enc(P,u,A) = J (J A u) (J u (J P u))   and   op u (enc P u A) = P.

Chain (dual L-form  x = op y (op (op z y) (op y (op x y)))):
  t1 = op x y   t2 = op y t1   t3 = op z y   t4 = op t3 t2   t5 = op y t4  ( = x )
Note t1 and t3 SHARE y, so forcing both to decode needs y to encode for both x and z.
Prints the (t1..t5, rule#) census beside the failure count -- a suite that never fires rule k has
tested nothing about rule k (gen/NOTES_10218.md).
"""
import sys, os, itertools, collections, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 36524
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'gen', 'chk36524.py')
spec = importlib.util.spec_from_file_location('chk', path)
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}; exec(compile(src, spec.origin, 'exec'), ns); rules = ns['rules']
print('law', law, '| rules', len(rules), flush=True)
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
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def enc(P, u, A): return J(J(A, u), J(u, J(P, u)))
BASE = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2))]
JUNK = [g(7), J(g(7), J(g(8), g(9))), enc(g(5), g(6), g(7)),
        J(J(g(5), g(6)), J(J(g(7), g(8)), g(9)))]
tab = collections.Counter(); bad = []; n = 0
def run(x, y, z, tag):
    global n
    try:
        t1 = op(x, y); t2 = op(y, t1); t3 = op(z, y); t4 = op(t3, t2); t5 = op(y, t4)
    except RecursionError:
        return
    n += 1
    m = tuple('F' if val == J(*a) else 'R%d' % (WH.get(a, -1) + 1)
              for a, val in (((x, y), t1), ((y, t1), t2), ((z, y), t3),
                             ((t3, t2), t4), ((y, t4), t5)))
    tab[(tag,) + m] += 1
    if t5 != x: bad.append((tag, x, y, z, m, t5))
# A. sanity: everything free
for x, y, z in itertools.product(BASE, repeat=3): run(x, y, z, 'plain')
# B. force t1 to decode: y := enc(P,x,A)  ->  t1 = P
for P, A, x, z in itertools.product(BASE[:4], BASE[:3], BASE[:3], BASE[:3]):
    run(x, enc(P, x, A), z, 't1-dec')
# C. force t3 to decode: y := enc(P,z,A)  ->  t3 = P
for P, A, z, x in itertools.product(BASE[:4], BASE[:3], BASE[:3], BASE[:3]):
    run(x, enc(P, z, A), z, 't3-dec')
# D. BOTH t1 and t3 decode: needs x = z (y encodes for one argument only)
for P, A, x in itertools.product(BASE[:4], BASE[:4], BASE[:4]):
    run(x, enc(P, x, A), x, 't1t3-dec')
# E. level-k descent: the payload is itself an encoding, k levels deep, + large junk
for k in (1, 2, 3):
    for q in JUNK:
        for x in BASE[:3]:
            P = x
            for _ in range(k): P = enc(P, g(4), q)
            for z in BASE[:3]:
                run(x, enc(P, x, q), z, 'desc-%d' % k)
                run(P, enc(P, P, q), z, 'desc-%d-b' % k)
                run(x, enc(x, x, P), z, 'desc-%d-junk' % k)
# F. the payload's own decoder differs from y (forces the deeper root rules)
for P, A, B, x in itertools.product(BASE[:3], BASE[:3], BASE[:3], BASE[:3]):
    inner = enc(P, A, B)
    run(inner, enc(inner, inner, A), x, 'deep-pay')
    run(x, enc(inner, x, A), inner, 'deep-pay2')
# G. FORCE THE DEEPER ROOT RULES: the inner product of each rule's own guard must DECODE.
#    36524's R2 [B11l] at (u,v) needs  op (a2 (a1 u)) u = a2 (a2 v)  with result a2 (a1 u);
#    R1 fires instead whenever that product is FREE, so build x with  op (a2 (a1 x)) x  decoded:
#    x := enc(V, Cc, A2) makes op Cc x = V, and then a2 (a1 x) = Cc by construction of enc.
for V, Cc, A2, A in itertools.product(BASE[:3], BASE[:3], BASE[:3], BASE[:3]):
    x = enc(V, Cc, A2)                       # a1 x = J A2 Cc  ->  a2 (a1 x) = Cc, op Cc x = V
    Wd = op(Cc, x)                           # decoded when the enc bites
    y = J(J(A, x), J(x, Wd))                 # the R2 shape at (x, y)
    for z in BASE[:3]:
        run(x, y, z, 'force-R2')
        run(x, enc(x, x, A), z, 'force-R2b')
    # and the same shape placed at t3 (u = z)
    for xx in BASE[:3]:
        run(xx, J(J(A, x), J(x, Wd)), x, 'force-R5deep')
# H. x an encoding AND y an encoding of it, two levels
for P, A, B in itertools.product(BASE[:3], BASE[:3], BASE[:3]):
    x = enc(P, A, B)
    y1 = enc(x, x, A); y2 = enc(P, x, x)
    for z in [A, B, x]:
        run(x, y1, z, 'nest-a'); run(x, y2, z, 'nest-b')
        run(P, enc(P, P, x), z, 'nest-c')
print('assignments %d, LAW FAILURES %d' % (n, len(bad)), flush=True)
print()
print('%-14s %-34s %s' % ('tag', '(t1..t5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: (kv[0][0], -kv[1])):
    print('  %-12s %-34s %d' % (k[0], str(k[1:]), c))
fired = set()
for k in tab:
    for e in k[1:]:
        if e != 'F': fired.add(e)
print()
print('RULES ACTUALLY FIRED anywhere:', sorted(fired, key=lambda s: int(s[1:])),
      ' of %d rules' % len(rules))
for tag, x, y, z, m, r in bad[:3]:
    print('  FAIL [%s] %s' % (tag, str(m)))
    print('    x =', show(x)[:200]); print('    y =', show(y)[:200]); print('    z =', show(z)[:200])
