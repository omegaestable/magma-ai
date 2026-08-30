"""_y8485_soft.py : test PURELY STRUCTURAL (softdrop) rule sets for law 8485.

Law 8485 (L-form):  x = y * (x * (((z*x)*y)*y))
  u = y ;  v = op(x, R)  with  R = op(Q,y), Q = op(P,y), P = op(z,x).
All free:  v = J x (J (J P y) y)   with P = J z x.
R1 (generated) checks P's shape too;  SOFT drops it -> fires for ANY p in the P slot.

Usage: python -u gen/_y8485_soft.py <variant> [full]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv
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
EQc = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)

# ---- SOFT: v = J w (J (J p u) u)  ->  w      (p unconstrained) ------------------
SOFT = ([TG(V), TG(A2(V)), TG(A1(A2(V))),
         EQc(U, A2(A1(A2(V)))), EQc(U, A2(A2(V)))], A1(V), 'soft')

# ---- SOFT2: also require that the P slot is a J (weaker than R1, stronger than SOFT)
SOFT2 = ([TG(V), TG(A2(V)), TG(A1(A2(V))), TG(A1(A1(A2(V)))),
          EQc(U, A2(A1(A2(V)))), EQc(U, A2(A2(V)))], A1(V), 'soft2')

# ---- chain rules from _x8485_min.py (variant f) --------------------------------


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


ZX22 = A2(A2(A1(V)))
ZU22 = A1(A2(A2(U)))
ZU221 = A1(A1(A2(A2(U))))
N4 = chain_rule(ZX22, 'zP@x22')
N1 = chain_rule(ZU22, 'zP@u22')
N2 = chain_rule(ZU221, 'zP@u221')

VARIANTS = {
    's': [SOFT],
    's2': [SOFT2],
    's1': [R1, SOFT],
    'sf': [SOFT, N4, N1, N2],
    'f': [R1, N4, N1, N2],
}

# ---- the "read the chain from the deepest FREE node, verify the rest by op" family ----
# v = J x R.  R = op(Q,u), Q = op(P,u), P = op(z,x).
# rule_P : P read at a1(a1(a2 v))   [needs Q,R free]   verify op(op(P,u),u) = a2 v
RP = ([TG(V), TG(A2(V)), TG(A1(A2(V))),
       OPEQ(OP(OP(A1(A1(A2(V))), U), U), A2(V))], A1(V), 'rP')
# rule_Q : Q read at a1(a2 v)       [needs R free]     verify op(Q,u) = a2 v
RQ = ([TG(V), TG(A2(V)),
       OPEQ(OP(A1(A2(V)), U), A2(V))], A1(V), 'rQ')
# rule_z : z read at a1(a1(a1(a2 v))) [all free]       verify the whole chain
RZ = ([TG(V), TG(A2(V)), TG(A1(A2(V))), TG(A1(A1(A2(V)))),
       OPEQ(OP(OP(OP(A1(A1(A1(A2(V)))), A1(V)), U), U), A2(V))], A1(V), 'rZ')

VARIANTS['P'] = [RP]
VARIANTS['Q'] = [RQ]
VARIANTS['1P'] = [R1, RP]
VARIANTS['1Q'] = [R1, RQ]
VARIANTS['1PQ'] = [R1, RP, RQ]
VARIANTS['PQ'] = [RP, RQ]
VARIANTS['1Pf'] = [R1, RP, N4, N1, N2]
VARIANTS['Z'] = [RZ]
VARIANTS['1PZ'] = [R1, RP, RZ]


def quick(name, R):
    print('variant %s : %d rules' % (name, len(R)), flush=True)
    for r in R:
        print('   ', cf.show_rule(r), flush=True)
    tot = 0
    for ms, gg in ((9, 1), (5, 2)):
        t0 = time.time()
        n, f = sc.exhaustive(cf.Closed(law, R), law, ms, gg, limit=25)
        tot += len(f)
        print('exh%d/%d tested %d fails %d  %.1fs' % (ms, gg, n, len(f), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('    FAIL', {k: str(v) for k, v in s.items()}, flush=True)
    return tot


def fast(name, R, N=6000):
    tot = 0
    for sd in (3, 4, 5):
        for kind, fn in (('crit', lambda C: fz.critical_fuzz(C, law, N, seed=sd + 300)),
                         ('fuzz', lambda C: fz.fuzz(C, law, R, N, seed=sd + 100)),
                         ('clos', lambda C: fz.closure_fuzz(C, law, N, seed=sd + 200))):
            t0 = time.time()
            t, f = fn(cf.Closed(law, R))
            real = [q for q in f if q[1] != 'recursion']
            tot += len(real)
            print('%s %d tested %d fails %d (rec %d)  %.1fs'
                  % (kind, sd, t, len(real), len(f) - len(real), time.time() - t0), flush=True)
            for s, r in real[:2]:
                print('    FAIL', {k: str(v) for k, v in s.items()}, flush=True)
    print('FAST TOTAL %d' % tot, flush=True)
    return tot


if __name__ == '__main__':
    import threading
    name = sys.argv[1]
    R = VARIANTS[name]

    def work():
        sys.setrecursionlimit(20000)
        t = quick(name, R)
        if 'fast' in sys.argv:
            fast(name, R)
        if 'deep' in sys.argv:
            for sd in (3, 4, 5):
                t0 = time.time()
                n, f = cf.deep_tests(cf.Closed(law, R), law, 3000, 240, sd)
                real = [q for q in f if q[1] != 'recursion']
                print('deep %d tested %d fails %d (rec %d) %.1fs'
                      % (sd, n, len(real), len(f) - len(real), time.time() - t0), flush=True)
                for s, r in real[:2]:
                    print('    FAIL', {k: str(v) for k, v in s.items()}, flush=True)

    threading.stack_size(64 * 1024 * 1024)
    th = threading.Thread(target=work)
    th.start(); th.join()
