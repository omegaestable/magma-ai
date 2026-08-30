"""_x8485_rep.py : candidate repairs for law 8485,  x = y * (x * (((z * x) * y) * y)).

Chain of the law, given op(u,v) with u = y:
    P = op(z,x)   Q = op(P,u)   R = op(Q,u)   v = op(x,R)
Shipped rules cover (root free) x (R free,Q free,P free) [R1], (P dec) [R2], (Q dec,P dec) [R3],
and (R dec, P dec) via the full-chain guard [R4].  The holes measured by gen/_x8485_probe.py are the
"P FREE with Q and/or R decoded" cells: z then sits inside u, not inside x.

Where z is when the encoding u is the free shape of the reading that produced the decoded node:
  Q dec:   u = J(Q, J(J(J(z2,Q),P),P))  ->  P = u.2.2 = u.2.1.2, z = P.1
  R dec:   u = J(R, J(J(J(z2,R),Q),Q))  ->  Q = u.2.2 ; if Q free = J(P,u), P = u.2.2.1, z = P.1
So three extra z-paths, each used with R4's full-chain guard.
Usage: python gen/_x8485_rep.py [--emit]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
from collections import Counter

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b)
TG = lambda e: ('TG', e)
EQ_ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)


def prefixes(e):
    """TG guards for every J-accessor prefix of e (innermost first)."""
    out = []
    while e[0] in ('A1', 'A2'):
        out.append(TG(e[1]))
        e = e[1]
    return list(reversed(out))


def chain_rule(zexpr, tag):
    x = A1(V)
    conds = [TG(V)] + prefixes(zexpr) + [OPEQ(OP(OP(OP(zexpr, x), U), U), A2(V))]
    seen = []
    for c in conds:
        if c not in seen:
            seen.append(c)
    return (seen, x, tag)


# z locations
Z_P_at_u22 = A1(A2(A2(U)))          # P = u.2.2   (Q decoded, or R&Q decoded)
Z_P_at_u221 = A1(A1(A2(A2(U))))     # P = u.2.2.1 (R decoded, Q free)
Z_P_at_u212 = A1(A2(A1(A2(U))))     # P = u.2.1.2 (Q decoded, alt occurrence)

N1 = chain_rule(Z_P_at_u22, 'zP@u22')
N2 = chain_rule(Z_P_at_u221, 'zP@u221')
N3 = chain_rule(Z_P_at_u212, 'zP@u212')

CANDS = {
    'shipped': rules,
    'shipped+N1': rules + [N1],
    'shipped+N1+N2': rules + [N1, N2],
    'shipped+N1+N2+N3': rules + [N1, N2, N3],
}


def validate(name, R, seeds=(3, 4, 5)):
    t0 = time.time()
    fails = rv.run_tests(law, R, list(seeds), 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    print('%-20s nrules=%2d  fails=%3d (value %3d)  %s  %.1fs'
          % (name, len(R), len(fails), len(real),
             dict(Counter((('rec' if f[1] == 'recursion' else 'val') + ':' + f[2]) for f in fails)),
             time.time() - t0), flush=True)
    return fails


if __name__ == '__main__':
    for r in (N1, N2, N3):
        print(cf.show_rule(r))
    print()
    only = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else None
    for name, R in CANDS.items():
        if only and name != only:
            continue
        validate(name, R)
