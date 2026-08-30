"""Heavy validation of the 12294 hand model (RULES_D2)."""
import sys, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, smallcheck as sc, fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x12294_model as MM
from _x12294_drive import show, chain

EQ = 12294
law = normalise(parse_eq(catalog()[EQ]))
A, B = law[1]
RULES = MM.RULES_E2

bad = 0


def rep(tag, fails):
    global bad
    val = [f for f in fails if f[1] != 'recursion']
    print('  %-22s fails=%d val=%d' % (tag, len(fails), len(val)), flush=True)
    bad += len(val)
    for s, r in val[:2]:
        print('     ', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r, flush=True)


t0 = time.time()
for ms, g in ((11, 1), (7, 2), (5, 3)):
    C = MM.Model(RULES)
    n, f = sc.exhaustive(C, law, ms, g, limit=25)
    print('  exhaustive %d/%d: %d assignments' % (ms, g, n), flush=True)
    rep('exh%d/%d' % (ms, g), f)

for sd in (11, 23, 37, 101, 911, 2027):
    C = MM.Model(RULES)
    t, f = cf.deep_tests(C, law, 20000, 300, sd)
    rep('deep20k/%d (%d)' % (sd, t), f)

for sd in (3, 4, 5, 77, 78):
    C = MM.Model(RULES)
    t, f = fz.closure_fuzz(C, law, 20000, seed=sd)
    rep('closure/%d' % sd, f)
    C = MM.Model(RULES)
    t, f = fz.critical_fuzz(C, law, 20000, seed=sd)
    rep('critical/%d' % sd, f)

C = MM.Model(RULES)
n, f = sc.exhaustive(C, law, 9, 1, limit=25)
print('firing counts', C.fired, 'cycles', C.cycles, flush=True)
print('TOTAL value fails: %d   (%.1fs)' % (bad, time.time() - t0), flush=True)
