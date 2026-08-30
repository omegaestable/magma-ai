"""Full-standard revalidation of the REPAIRED 8-rule set for law 5837.

Standard (DEEP_SESSION_6 testing protocol item 1):
  rv.run_tests(law, rules, [3,4,5], 3000, 12000) == []   (exhaustive small + deep + fuzz + closure + critical)
  cf.deep_tests(C, law, 20000, 300, seed) clean on two further seeds.
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 5837
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', cat[EQ], 'dualized', dualized, 'normalised', law)

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

R1 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ_(U, A2(A1(A2(A2(V))))), EQ_(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R2p = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R3 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
q = A1(U); xx = A1(q)
common = [EQ_(V, U), TG(U), TG(A2(U)), EQ_(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ_(xx, A2(A1(A2(q)))), EQ_(xx, A2(A2(q)))], xx, 'R4a')
R4b = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(q)))], xx, 'R4b')
R4bp = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), OPEQ(OP(xx, xx), A1(A2(q)))], xx, 'R4bp')
R4c = (common + [TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A2(q)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(xx)))], xx, 'R4c')
rules = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]
for r in rules:
    print(cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
kinds = {}
for s, r, kind, sd in fails:
    k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
    kinds[k] = kinds.get(k, 0) + 1
print('run_tests fails', len(fails), kinds, 'secs', round(time.time() - t0, 1), flush=True)
for s, r, kind, sd in fails[:5]:
    print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()},
          'got', 'recursion' if r == 'recursion' else size(r))

for sd in (777, 4242, 20260829):
    C = cf.Closed(law, rules)
    tested, f = cf.deep_tests(C, law, 20000, 300, sd)
    print('deep_tests seed', sd, 'tested', tested, 'fails', len(f), 'secs', round(time.time() - t0, 1), flush=True)
print('fired counts', cf.Closed(law, rules).fired if False else '')
