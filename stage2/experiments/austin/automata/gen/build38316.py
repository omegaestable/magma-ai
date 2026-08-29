"""build38316.py -- construct the 10-rule DSL translation of the validated Rec model for law 38316
(dualized L-form), validate it, and emit the Lean skeleton via leangen.emit."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import revalidate as rv
import leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def Jc(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQc(a, b): return ('EQ', a, b)
def OPEQ(a, b, c): return ('OPEQ', OP(a, b), c)

p = A1(V)        # p := a1(v)  (the result on every firing rule)
Uu = A2(V)        # U := a2(v)

Vcands = [('V0', A1(Uu)), ('V1', A2(A2(U)))]

rules = []
for vname, Vexpr in Vcands:
    condTp = OPEQ(Vexpr, U, Uu)             # op(V,u) == U
    # W1: V = J u W, W := a2(V)
    W1 = A2(Vexpr)
    condW1shape = [TG(Vexpr), EQc(A1(Vexpr), U)]
    condW1op = OPEQ(U, W1, Vexpr)            # op(u, W1) == V
    q0_1 = A1(W1); q1_1 = A2(A2(p))
    condQ0_1 = OPEQ(q0_1, p, W1)
    condQ1_1 = OPEQ(q1_1, p, W1)
    rules.append(([TG(V)] + [condTp] + condW1shape + [condW1op, condQ0_1], p, '%s-W1-q0' % vname))
    rules.append(([TG(V)] + [condTp] + condW1shape + [condW1op, condQ1_1], p, '%s-W1-q1' % vname))
    # W2: q = V; check op(V,p) == J(V,p) and op(u, J(V,p)) == V
    pairVp = Jc(Vexpr, p)
    condW2a = OPEQ(Vexpr, p, pairVp)
    condW2b = OPEQ(U, pairVp, Vexpr)
    rules.append(([TG(V), condTp, condW2a, condW2b], p, '%s-W2' % vname))
    # W3: p = J W _, W := a1(p)
    W3 = A1(p)
    condW3shape = [TG(p)]
    condW3op = OPEQ(U, W3, Vexpr)
    q0_3 = A1(W3); q1_3 = A2(A2(p))
    condQ0_3 = OPEQ(q0_3, p, W3)
    condQ1_3 = OPEQ(q1_3, p, W3)
    rules.append(([TG(V), condTp] + condW3shape + [condW3op, condQ0_3], p, '%s-W3-q0' % vname))
    rules.append(([TG(V), condTp] + condW3shape + [condW3op, condQ1_3], p, '%s-W3-q1' % vname))

print('rules', len(rules))
for r in rules:
    print(' ', r[2], cf.show_rule(r))

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails))
for f in fails[:10]:
    print(' FAIL', f)

if not fails:
    leangen.emit(EQ, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rep38316'), rules_override=rules)
    print('emitted gen/rep38316.lean')
