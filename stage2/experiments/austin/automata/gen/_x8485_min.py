"""_x8485_min.py : minimal rule sets for law 8485 built on the full-chain guard.

R4's guard  op(op(op(z, v.1), u), u) == v.2  verifies the WHOLE chain, so it subsumes R2/R3
(whose only job is to locate z at v.1.2.1.2 = x.2.1.2 when P = op z x decoded).  The measured
holes are the cells where P is FREE and Q and/or R decoded; then z sits inside u:
   Q dec, R free : u = J(Q, J(J(J(z2,Q),P),P))  -> P = u.2.2, z = u.2.2.1
   R dec, Q free : u = J(R, J(J(J(z2,R),Q),Q))  -> Q = u.2.2 = J(P,u), z = u.2.2.1.1
Usage: python -u gen/_x8485_min.py <variant> [full]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
import fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
from collections import Counter

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
R1, R2, R3, R4 = rules

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b)
TG = lambda e: ('TG', e)
OPEQ = lambda a, b: ('OPEQ', a, b)


def prefixes(e):
    out = []
    while e[0] in ('A1', 'A2'):
        out.append(TG(e[1])); e = e[1]
    return list(reversed(out))


def chain_rule(zexpr, tag):
    x = A1(V)
    conds = [TG(V)] + prefixes(zexpr) + [OPEQ(OP(OP(OP(zexpr, x), U), U), A2(V))]
    seen = []
    for c in conds:
        if c not in seen:
            seen.append(c)
    return (seen, x, tag)


ZX = A2(A1(A2(A1(V))))            # z = x.2.1.2 = v.1.2.1.2   (P decoded)
ZU22 = A1(A2(A2(U)))          # z = u.2.2.1               (Q decoded, P free)
ZU221 = A1(A1(A2(A2(U))))     # z = u.2.2.1.1             (R decoded, Q free, P free)
ZU212 = A1(A2(A1(A2(U))))     # z = u.2.1.2.1

C4 = chain_rule(ZX, 'zP@x212')
N1 = chain_rule(ZU22, 'zP@u22')
N2 = chain_rule(ZU221, 'zP@u221')
N3 = chain_rule(ZU212, 'zP@u212')

# gen/_x8485_paths.py: on every one of the 11 measured top-pair failures of variant 'a' the guard
# op (op (op w (a1 v)) u) u = a2 v holds with w at v.1.2.2 = a2 (a2 (a1 v)) -- i.e. z = x.2.2.
# That is where z sits when the LAST step of the decoding that produced P = op z x was free
# (a2 x = J c z), which is the case the generated rule set never enumerated.
ZX22 = A2(A2(A1(V)))          # z = x.2.2 = v.1.2.2
N4 = chain_rule(ZX22, 'zP@x22')

VARIANTS = {
    'a': [R1, C4, N1, N2],
    'b': [R1, C4, N1, N2, N3],
    'c': [R1, R2, R3, R4, N1, N2],
    'd': [R1, C4, N1],
    'e': [R1, C4, N2],
    'f': [R1, N4, N1, N2],
    'g': [R1, C4, N4, N1, N2],
    'h': [R1, N4],
    'i': [R1, N4, N1],
}


def quick(name, R):
    print('variant %s : %d rules' % (name, len(R)), flush=True)
    for r in R:
        print('   ', cf.show_rule(r))
    tot = 0
    for ms, gg in ((9, 1), (5, 2)):
        t0 = time.time()
        n, f = sc.exhaustive(cf.Closed(law, R), law, ms, gg, limit=25)
        tot += len(f)
        print('exh%d/%d tested %d fails %d  %.1fs' % (ms, gg, n, len(f), time.time() - t0), flush=True)
    return tot


if __name__ == '__main__':
    name = sys.argv[1]
    R = VARIANTS[name]
    quick(name, R)
    if 'full' in sys.argv:
        t0 = time.time()
        fails = rv.run_tests(law, R, [3, 4, 5], 3000, 12000)
        real = [f for f in fails if f[1] != 'recursion']
        print('run_tests fails %d (value %d) %s  %.1fs'
              % (len(fails), len(real),
                 dict(Counter((('rec' if f[1] == 'recursion' else 'val') + ':' + f[2]) for f in fails)),
                 time.time() - t0), flush=True)
        for f in real[:4]:
            print('   FAIL', f[2], f[3], {k: size(v) for k, v in f[0].items()}, flush=True)
