"""_x8485_quick.py : fast check that the candidate 8485 rules fix the measured failing instances.
Usage: python -u gen/_x8485_quick.py [variant]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
import fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
from collections import Counter
import importlib
rep = importlib.import_module('gen._x8485_rep') if False else None

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b)
TG = lambda e: ('TG', e)
EQc = lambda a, b: ('EQ', a, b)
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


N1 = chain_rule(A1(A2(A2(U))), 'zP@u22')
N2 = chain_rule(A1(A1(A2(A2(U)))), 'zP@u221')
N3 = chain_rule(A1(A2(A1(A2(U)))), 'zP@u212')

VARIANTS = {
    'shipped': rules,
    'N1': rules + [N1],
    'N12': rules + [N1, N2],
    'N123': rules + [N1, N2, N3],
}

if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'N123'
    R = VARIANTS[name]
    print('variant', name, len(R), 'rules')
    for r in R:
        print('   ', cf.show_rule(r))
    t0 = time.time()
    n, f = sc.exhaustive(cf.Closed(law, R), law, 9, 1, limit=25)
    print('exh9/1  tested %d fails %d  %.1fs' % (n, len(f), time.time() - t0), flush=True)
    t0 = time.time()
    n, f = sc.exhaustive(cf.Closed(law, R), law, 5, 2, limit=25)
    print('exh5/2  tested %d fails %d  %.1fs' % (n, len(f), time.time() - t0), flush=True)
    for sd in (3,):
        t0 = time.time()
        t, f = cf.deep_tests(cf.Closed(law, R), law, 1500, 240, sd)
        print('deep %d  tested %d fails %d  %.1fs' % (sd, t, len([q for q in f if q[1] != 'recursion']), time.time() - t0), flush=True)
        t0 = time.time()
        t, f = fz.critical_fuzz(cf.Closed(law, R), law, 6000, seed=sd + 300)
        print('crit %d  tested %d fails %d  %.1fs' % (sd, t, len([q for q in f if q[1] != 'recursion']), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('    FAIL', {k: size(v) for k, v in s.items()})
        t0 = time.time()
        t, f = fz.closure_fuzz(cf.Closed(law, R), law, 6000, seed=sd + 200)
        print('clos %d  tested %d fails %d  %.1fs' % (sd, t, len([q for q in f if q[1] != 'recursion']), time.time() - t0), flush=True)
        t0 = time.time()
        t, f = fz.fuzz(cf.Closed(law, R), law, R, 6000, seed=sd + 100)
        print('fuzz %d  tested %d fails %d  %.1fs' % (sd, t, len([q for q in f if q[1] != 'recursion']), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('    FAIL', {k: size(v) for k, v in s.items()})
