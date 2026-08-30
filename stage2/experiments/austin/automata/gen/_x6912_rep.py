"""Repair candidate for 6912.

Diagnosis (all 5 validator failures are ONE shape):
  x = J z z  (= op(z,z), free);  E = op(x, u) free = J x u;
  W = op(S, E) = op(x, J x u) decodes by R1 to u.2.1;   u = J (J z2 z2) (J W x);
  B = op(u, W) free = J u W = v.
Final pair (u, v) is a genuine reading with payload x = u.2.2, but the extractor's rule for it
verifies the decoding with the nested guard op(op(u.1,u).1, op(u.1,u)) whose pair (3,13) is NOT
below msr(u,v) = msr(9,11)  ->  GATE CUT.
Fix: express the guard STRUCTURALLY.  op(x, J x u) fires R1 (the first rule) exactly when
  tg u = 2, tg u.1 = 2, u.1.1 = u.1.2, tg u.2 = 2, u.2.2 = x   -> result u.2.1.
So the whole verification is a structural condition on u, and no nested op is needed.
"""
import sys, os, json, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 6912
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
base = ns['rules']

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

X = A2(A2(U))          # the payload:  x = u.2.2
W = A2(V)              # w = v.2

struct = [TG(V), EQ_(U, A1(V)),
          TG(U), TG(A1(U)), EQ_(A1(A1(U)), A2(A1(U))),
          TG(A2(U)), EQ_(W, A1(A2(U))),
          TG(X), EQ_(A1(X), A2(X))]

R15_bare = (list(struct), X, 'B1v-struct')
# with the "outer product of the encoding is free" guard: op(u, w) = v
R15_g1 = (list(struct) + [OPEQ(OP(U, W), V)], X, 'B1v-struct+g')
# additionally: op(x, u) must be free (E = J x u)
R15_g2 = (list(struct) + [OPEQ(OP(U, W), V), OPEQ(OP(X, U), ('J', X, U))], X, 'B1v-struct+gg')

VARIANTS = {'bare': base + [R15_bare], 'g1': base + [R15_g1], 'g2': base + [R15_g2]}

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'bare'
    rules = VARIANTS[which]
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    print('%s: nrules=%d run_tests fails=%d (real %d)  %.1fs' % (which, len(rules), len(fails), len(real), time.time() - t0))
    for s, r, kind, sd in fails[:6]:
        print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()}, 'got', 'recursion' if r == 'recursion' else size(r))
