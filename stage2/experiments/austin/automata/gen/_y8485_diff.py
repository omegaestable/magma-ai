# -*- coding: utf-8 -*-
"""_y8485_diff.py : is variant `f` a MINIMISATION ARTIFACT?  (the 10218 test)

10218's 6-rule minimised model is FALSE while the full 140-rule extraction evaluates the failing
instance correctly.  Variant f is a 4-rule subset of an 83-rule extraction chosen the same way, so
the direct test is: evaluate the law's chain under BOTH rule sets on the same instances and compare.

  * a variant-f failure where FULL-83 succeeds  -> MINIMISATION ARTIFACT (variant f is false)
  * a failure under both                        -> the extraction itself is false
  * no failure under either, and the two agree  -> the minimisation is not distorting on this pool

Population: exhaustive small terms + every forcing construction of gen/_y8485_force2.py, each of
which is known (by its own census) to fire the rule it targets.

Usage: python -u gen/_y8485_diff.py [N_per_kind]
"""
import sys, os, random, itertools, collections, threading, importlib.util
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
os.chdir(D)
spec = importlib.util.spec_from_file_location('_x8485_min', 'gen/_x8485_min.py')
m = importlib.util.module_from_spec(spec); sys.modules['_x8485_min'] = m
_a = sys.argv; sys.argv = ['x', 'a']
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass
sys.argv = _a
import closedform as cf
from freemodel import size, rand_term

law = m.law
VF = m.VARIANTS['f']
FULL = cf.Extractor(law).rules(exist=False)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def outcome(rules, x, y, z):
    C = cf.Closed(law, rules)
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R)
    return C.op(y, S)


def terms(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)]}
    allt = list(by[1])
    for n in range(3, maxsize + 1, 2):
        cur = []
        for a in range(1, n - 1):
            for s in by.get(a, []):
                for t in by.get(n - 1 - a, []):
                    cur.append(('J', s, t))
        by[n] = cur; allt += cur
    return allt


def work():
    sys.setrecursionlimit(20000)
    print('variant f %d rules ; FULL %d rules' % (len(VF), len(FULL)), flush=True)
    pool = []
    ts = terms(5, 2)
    for x in ts:
        for y in ts:
            for z in ts:
                pool.append(('exh', x, y, z))
    # the forcing constructions, each known non-vacuous from gen/_y8485_force2.out
    Cf = cf.Closed(law, VF)

    def enc(u, w, j):
        return Cf.op(w, Cf.op(Cf.op(Cf.op(j, w), u), u))

    rnd = random.Random(101)
    small = [rand_term(rnd.randint(1, 3), 2) for _ in range(60)]
    big = [rand_term(rnd.randint(5, 7), 3) for _ in range(60)]
    for junk in (small, big):
        for _ in range(N):
            z = rnd.choice(small); y = rnd.choice(small)
            x = enc(z, rnd.choice(small), rnd.choice(junk))          # B: P decoded, R2 fires
            pool.append(('B', x, y, z))
            x2 = rnd.choice(small); P = Cf.op(z, x2)
            pool.append(('C', x2, enc(P, rnd.choice(small), rnd.choice(junk)), z))   # R3 fires
            x3 = rnd.choice(small)
            pool.append(('E', x3, enc(rnd.choice(junk), rnd.choice(small), x3), z))  # H3
            P2 = Cf.op(z, x)
            pool.append(('F', x, enc(P2, rnd.choice(small), rnd.choice(junk)), z))   # B+C
    print('population %d instances' % len(pool), flush=True)
    badf = []; badF = []; disagree = []
    per = collections.Counter()
    for lbl, x, y, z in pool:
        try:
            rf = outcome(VF, x, y, z)
            rF = outcome(FULL, x, y, z)
        except RecursionError:
            continue
        per[lbl] += 1
        if rf != x:
            badf.append((lbl, x, y, z, rf, rF))
        if rF != x:
            badF.append((lbl, x, y, z, rf, rF))
        if rf != rF:
            disagree.append((lbl, x, y, z, rf, rF))
    print('tested per kind:', dict(per), flush=True)
    print('variant-f failures : %d' % len(badf), flush=True)
    print('FULL-83  failures  : %d' % len(badF), flush=True)
    print('top-result disagreements between the two rule sets : %d' % len(disagree), flush=True)
    for lbl, x, y, z, rf, rF in (badf + disagree)[:4]:
        print('  [%s] x=%s' % (lbl, show(x)[:150]), flush=True)
        print('       y=%s' % show(y)[:150], flush=True)
        print('       z=%s' % show(z)[:150], flush=True)
        print('       variant-f -> %s ; FULL-83 -> %s ; verdict %s'
              % (show(rf)[:100], show(rF)[:100],
                 'MINIMISATION ARTIFACT' if (rf != x and rF == x) else
                 ('BOTH FALSE' if rf != x else 'disagreement only')), flush=True)


threading.stack_size(96 * 1024 * 1024)
th = threading.Thread(target=work); th.start(); th.join()
