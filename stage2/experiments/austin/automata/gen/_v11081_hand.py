"""Hand-designed small rule sets for 11081, validated to the wave-3 standard.

The intended semantics of the free model for  x = y * ((x * (y*x)) * (z*y)) :
    op u v = a1 (a1 v)   when   v = J (J p A) C   with   A = op u p   and   C = "op z u for some z"
The `A = op u p` half is  OPEQ(op(u, a1(a1 v)), a2(a1 v))  -- definitional at the law's top product.
The `C` half is the existential; the two computable readings are
    (X1)  C free:     tg C = 2  and  a2 C = u
    (X2)  C decoded:  tg u = 2, tg (a1 u) = 2  and  C = a1 (a1 u)

usage: python gen/_v11081_hand.py <name> [stage]
"""
import sys, os, time, collections, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
A, B = law[1]

U = ('U',)
V = ('V',)


def a1(e):
    return ('A1', e)


def a2(e):
    return ('A2', e)


P = a1(a1(V))          # the payload  v.1.1
AA = a2(a1(V))         # the A slot   v.1.2
CC = a2(V)             # the C slot   v.2

CORE = [('TG', V), ('TG', a1(V)), ('OPEQ', ('OP', U, P), AA)]
X1 = (CORE + [('TG', CC), ('EQ', U, a2(CC))], P, 'Cfree')
X2 = (CORE + [('TG', U), ('TG', a1(U)), ('EQ', CC, a1(a1(U)))], P, 'Cdec')
# tighter variant of X2: additionally demand that the canonical z reproduces C
X2b = (CORE + [('TG', U), ('TG', a1(U)), ('TG', a2(a1(U))),
               ('OPEQ', ('OP', a1(a2(a1(U))), U), CC)], P, 'Cdec-canon')
# X2 plus the demand that u is itself in encoded form (a1 u = J _ _)
X2c = (CORE + [('TG', U), ('TG', a1(U)), ('TG', a1(a1(U))), ('EQ', CC, a1(a1(U)))], P, 'Cdec-J')

SETS = {
    'x12': [X1, X2],
    'x1': [X1],
    'x12b': [X1, X2b],
    'x12c': [X1, X2c],
    'x12b2': [X1, X2b, X2],
}
NAME = sys.argv[1] if len(sys.argv) > 1 else 'x12'
rules = SETS[NAME]
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'all'
print('rule set', NAME, flush=True)
for r in rules:
    print('  ', cf.show_rule(r), flush=True)

t0 = time.time()
if STAGE in ('all', '1'):
    f = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    real = [q for q in f if q[1] != 'recursion']
    print('STAGE1 run_tests: %d fails (%d real)  %.0fs' % (len(f), len(real), time.time() - t0), flush=True)
    for q in real[:5]:
        print('   FAIL', q[2], q[3], {k: size(v) for k, v in q[0].items()}, flush=True)
    if real:
        print('ABORT'); sys.exit(0)

if STAGE in ('all', '2'):
    for sd in (7, 11, 13, 17):
        C = cf.Closed(law, rules)
        t, fl = cf.deep_tests(C, law, 20000, 600, sd)
        real = [q for q in fl if q[1] != 'recursion']
        print('STAGE2 deep20000 seed %d: tested %d fails %d (real %d)  %.0fs'
              % (sd, t, len(fl), len(real), time.time() - t0), flush=True)
        if real:
            print('ABORT'); sys.exit(0)

if STAGE in ('all', '3'):
    def branch(C, u, v):
        for i, (conds, x, tag) in enumerate(C.rules):
            if C.check(conds, u, v) and C.ev(x, u, v) is not None:
                return i + 1
        return 0

    byb = collections.defaultdict(list)
    PER = 400
    for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                     ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                     ('deep3', lambda C: cf.deep_tests(C, law, 4000, 300, 3)),
                     ('fuzz3', lambda C: fz.fuzz(C, law, rules, 15000, seed=103)),
                     ('clos3', lambda C: fz.closure_fuzz(C, law, 15000, seed=203)),
                     ('crit3', lambda C: fz.critical_fuzz(C, law, 15000, seed=303)),
                     ('fuzz4', lambda C: fz.fuzz(C, law, rules, 15000, seed=104)),
                     ('clos4', lambda C: fz.closure_fuzz(C, law, 15000, seed=204)),
                     ('crit4', lambda C: fz.critical_fuzz(C, law, 15000, seed=304)),
                     ('fuzz5', lambda C: fz.fuzz(C, law, rules, 15000, seed=105)),
                     ('clos5', lambda C: fz.closure_fuzz(C, law, 15000, seed=205)),
                     ('crit5', lambda C: fz.critical_fuzz(C, law, 15000, seed=305))):
        C = cf.Closed(law, rules)
        mk(C)
        for (u, v) in list(C.memo.keys()):
            b = branch(C, u, v)
            if b and len(byb[b]) < PER:
                byb[b].append((u, v))
    print('STAGE3 firing pairs per branch:', {k: len(v) for k, v in sorted(byb.items())},
          '%.0fs' % (time.time() - t0), flush=True)
    random.seed(11)
    pool = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
            ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))] + [rand_term(3) for _ in range(10)]
    fails = collections.Counter()
    shown = 0
    tests = 0
    for b, prs in sorted(byb.items()):
        for (u, v) in prs:
            for slot in ('zy', 'yx', 'xy'):
                for t in pool:
                    C = cf.Closed(law, rules)
                    if slot == 'zy':
                        s = {'x': t, 'y': v, 'z': u}
                    elif slot == 'yx':
                        s = {'x': v, 'y': u, 'z': t}
                    else:
                        s = {'x': u, 'y': v, 'z': t}
                    try:
                        got = C.op(C.evp(A, s), C.evp(B, s))
                    except RecursionError:
                        continue
                    tests += 1
                    if got != s['x']:
                        fails[(b, slot)] += 1
                        shown += 1
                        if shown <= 3:
                            print('   LAW FAILS b=%d slot=%s |x|=%d |y|=%d |z|=%d'
                                  % (b, slot, size(s['x']), size(s['y']), size(s['z'])), flush=True)
    print('STAGE3 producer-fuzz tests %d  failures %s  TOTAL %d  %.0fs'
          % (tests, dict(fails), sum(fails.values()), time.time() - t0), flush=True)
print('DONE %.0fs' % (time.time() - t0))
