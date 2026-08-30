"""Repair candidate for law 38316 (dualized L-form  x = y*(x*((y*(z*x))*y))).

THE HOLE (found 2026-08-29): the 10-rule model in gen/rep38316.lean is FALSE.  Counterexample
(total size 35, confirmed on the 10-rule set, the 5-rule V0 subset and the SEMANTIC free model):

    z  = g2
    y  = (g0*((g2*(g1*g0))*g2))
    x  = (((g0*((g2*(g1*g0))*g2))*(g3*g2))*(g0*((g2*(g1*g0))*g2)))
    -> a = op(z,x) free, b = op(y,a) = g2 (decoded), c = op(b,y) = g0 (DECODED),
       d = op(x,c) free, and NO rule fires at the top: op(y,d) = J y d != x.

Diagnosis.  When c = op(b,y) decodes, the invariant "a2 (a2 v) = u on every decoding pair" (I2, 0
violations in 82,909 decoding pairs) puts b at a2 (a2 u), which is exactly what the V1 rule family
reads.  But
  * V1-W1 is DEAD BY CONSTRUCTION: it wants b = J u a (op(y,a) free), while b = a2(a2 u) is a proper
    subterm of u, so sz b < sz u < sz (J u a);
  * V1-W2 is the right rule for "c decoded, a free" and is GATE CUT: its guard is
    op(u, J(a2(a2 u), a1 v)) == a2(a2 u), i.e. it recomputes the b product op(y, a) with
    a = J z x, and msr(y,a) < msr(y,d) fails exactly when sz z >= sz (a1 y)  (a tie in the
    counterexample: sz a = sz d = 25).
So the repair is PLAYBOOK_REPAIR 9.1 -- express the cut guard structurally: one level of expansion
of "op(y, J b x) decodes to b" using the I2 invariant (a2 x = u) plus its own T-condition
(x = op(a1 x, u)), both of which live on pairs strictly below msr(u,v).

usage: _x38316_fix.py [set] ; sets: cand (default), cand2, all, v0
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
BY = {r[2]: r for r in ALL}

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def Jc(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQc(a, b): return ('EQ', a, b)
def OPEQ(a, b, c): return ('OPEQ', OP(a, b), c)

B = A2(A2(U))          # b, by the I2 invariant, when c = op(b,u) decoded
X = A1(V)              # the payload x
cbase = [TG(V), TG(U), TG(A2(U)),
         EQc(A2(V), A1(U)),
         OPEQ(B, U, A2(V)),                       # op(b,u) = a2 v = a1 u   (c decoded)
         ]
# "c decoded, a free": a = J b x, and op(y,a) decodes to b.  Structural expansion of that decoding:
#   I2 for (u,a):  a2 (a2 a) = a2 x = u      T for (u,a):  a2 a = x = op(a1 x, u)
W2S = (cbase + [OPEQ(B, X, Jc(B, X)),            # a = op(b,x) is free
                TG(X), EQc(A2(X), U),            # x = J (a1 x) u
                OPEQ(A1(X), U, X)],              # x = op(a1 x, u)
       X, 'V1-W2s')

# strictly weaker variant without the "a free" guard (kept as a fallback candidate)
W2S2 = (cbase + [TG(X), EQc(A2(X), U), OPEQ(A1(X), U, X)], X, 'V1-W2s2')


# ---- the fully inlined "c decoded, a free" family: five variants, one per rule that can fire at (u,a) ----
AX = A1(X)          # a1 x
common_s = cbase + [OPEQ(B, X, Jc(B, X)),        # a = op(b,x) is free  (a = J b x)
                    TG(X), EQc(A2(X), U),        # I2 for the (u,a) decoding: a2 x = u
                    OPEQ(AX, U, X)]              # T  for the (u,a) decoding: x = op(a1 x, u)
W1c = [TG(AX), EQc(A1(AX), U), OPEQ(U, A2(AX), AX)]
SW1q0 = (common_s + W1c + [OPEQ(A1(A2(AX)), B, A2(AX))], X, 'V1-s-W1q0')
SW1q1 = (common_s + W1c + [OPEQ(A2(A2(B)), B, A2(AX))], X, 'V1-s-W1q1')
SW2   = (common_s + [OPEQ(AX, B, Jc(AX, B)), OPEQ(U, Jc(AX, B), AX)], X, 'V1-s-W2')
W3c = [TG(B), OPEQ(U, A1(B), AX)]
SW3q0 = (common_s + W3c + [OPEQ(A1(A1(B)), B, A1(B))], X, 'V1-s-W3q0')
SW3q1 = (common_s + W3c + [OPEQ(A2(A2(B)), B, A1(B))], X, 'V1-s-W3q1')
SFAM = [SW1q0, SW1q1, SW2, SW3q0, SW3q1]

V0 = [BY['V0-W1-q0'], BY['V0-W1-q1'], BY['V0-W2'], BY['V0-W3-q0'], BY['V0-W3-q1']]
SETS = {
    'all': ALL,
    'v0': V0,
    'cand': V0 + [BY['V1-W3-q0'], BY['V1-W3-q1'], W2S],
    'cand2': V0 + [BY['V1-W3-q0'], BY['V1-W3-q1'], W2S2],
    'cand3': V0 + [BY['V1-W2'], BY['V1-W3-q0'], BY['V1-W3-q1'], W2S],
    'cand4': V0 + [BY['V1-W3-q0'], BY['V1-W3-q1']] + SFAM,
    'cand5': V0 + [BY['V1-W2'], BY['V1-W3-q0'], BY['V1-W3-q1']] + SFAM,
}

name = sys.argv[1] if len(sys.argv) > 1 else 'cand'
rules = SETS[name]
print('set %s: %d rules' % (name, len(rules)))
for r in rules:
    print('  %-10s %s' % (r[2], cf.show_rule(r)))

import json
json.dump([r[2] for r in rules], open(
    'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x38316_set_%s.json' % name, 'w'))
# also dump the rule list itself so other scripts can load it
import pprint
with open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x38316_rules_%s.py' % name,
          'w', encoding='utf-8') as f:
    f.write('rules = ' + pprint.pformat(rules, width=200) + '\n')

if '--check' in sys.argv:
    import time
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    print('run_tests fails %d  (%.0fs)' % (len(fails), time.time() - t0))
    from collections import Counter
    print(Counter([f[2] for f in fails]))
    for f in fails[:4]:
        print('  ', f)
