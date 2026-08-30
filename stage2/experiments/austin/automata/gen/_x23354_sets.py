"""23354: validate several rule sets and check Rfree / Ffree for each."""
import sys, time, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); R = ns['rules']
U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e); A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e); EQc = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b); OP = lambda a, b: ('OP', a, b)
U2c = [TG(U), TG(V), OPEQ(OP(A2(U), A1(V)), A1(U))]
V2c = [TG(A1(V)), TG(A1(A1(V))), EQc(A1(A1(A1(V))), A2(A1(V))), EQc(A2(A1(A1(V))), A2(V))]
V3c = [TG(A1(V)), OPEQ(OP(A2(A1(V)), A2(V)), A1(A1(V)))]
R5 = (U2c + V2c, A1(V), 'U2xV2'); R6 = (U2c + V3c, A1(V), 'U2xV3')

SETS = {
    'S4  (R1 R2 R3 R4)': R,
    'S6  (+U2xV2 +U2xV3)': R + [R5, R6],
    'S5a (R1 R2 R3 R4 U2xV2)': R + [R5],
    'S5b (R1 R2 R3 R4 U2xV3)': R + [R6],
    'S3  (R1 R2 R4)': [R[0], R[1], R[3]],
}

MAX = 9
terms = {1: [('g', i) for i in range(2)]}
for n in range(3, MAX + 1, 2):
    acc = []
    for a in range(1, n - 1):
        b = n - 1 - a
        for t1 in terms.get(a, []):
            for t2 in terms.get(b, []): acc.append(('J', t1, t2))
    terms[n] = acc
P = [t for n in sorted(terms) for t in terms[n]]

for name, rs in SETS.items():
    t0 = time.time()
    f = rv.run_tests(law, rs, [3, 4], 2000, 8000)
    real = [q for q in f if q[1] != 'recursion']
    C = cf.Closed(law, rs)
    rf = ff = 0
    for a in P:
        for b in P:
            try:
                W = C.op(b, a)                     # op(y,x) with y=b, x=a
                if C.op(W, b) != ('J', W, b): rf += 1
                F = C.op(a, b)                     # op(x,z) with x=a, z=b
                if C.op(a, F) != ('J', a, F): ff += 1
            except RecursionError: pass
    print('%-26s run_tests real fails %4d | Rfree violations %d | Ffree violations %d | %.0fs'
          % (name, len(real), rf, ff, time.time() - t0), flush=True)
