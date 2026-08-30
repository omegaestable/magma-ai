"""23354: complete the rule matrix.

The four generated rules are  u-side x v-side  combinations:
   u-side U1 (structural): tg(a1 u)=2, a1(a1 u)=a2 u, a2(a1 u)=a1 v     "u = J (J (a2 u) p) (a2 u)"
   u-side U2 (recursive) : op(a2 u, a1 v) = a1 u                        "u is an A-value with payload p"
   v-side V1 (structural): tg(a2 v)=2, a1(a2 v)=a1 v                    "v = J p (J p _)"
   v-side V2 (struct-dec): tg(a1 v)=2, tg(a1(a1 v))=2,
                           a1(a1(a1 v))=a2(a1 v), a2(a1(a1 v))=a2 v     "a2 v is the payload of a1 v"
   v-side V3 (recursive) : tg(a1 v)=2, op(a2(a1 v), a2 v) = a1(a1 v)
   R1=U1xV1  R2=U1xV2  R3=U2xV1  R4=U1xV3     -- missing: U2xV2, U2xV3
Every rule returns a1 v.
"""
import sys, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules4 = ns['rules']

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e); A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e); EQc = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b); OP = lambda a, b: ('OP', a, b)

U2 = [TG(U), TG(V), OPEQ(OP(A2(U), A1(V)), A1(U))]
V2 = [TG(A1(V)), TG(A1(A1(V))), EQc(A1(A1(A1(V))), A2(A1(V))), EQc(A2(A1(A1(V))), A2(V))]
V3 = [TG(A1(V)), OPEQ(OP(A2(A1(V)), A2(V)), A1(A1(V)))]

R5 = (U2 + V2, A1(V), 'U2xV2')
R6 = (U2 + V3, A1(V), 'U2xV3')
rules6 = rules4 + [R5, R6]
for r in rules6: print(cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules6, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real), 'secs', round(time.time() - t0, 1))
for f in real[:5]:
    print('  FAIL', f[2], f[3], {k: str(v)[:80] for k, v in f[0].items()})
if not real:
    for sd in (911, 912, 913):
        C = cf.Closed(law, rules6)
        t, ff = cf.deep_tests(C, law, 20000, 300, sd)
        rf = [xx for xx in ff if xx[1] != 'recursion']
        print('deep20k seed', sd, 'tested', t, 'real fails', len(rf), 'cycles', C.cycles, flush=True)
