"""Test the 4-rule candidate for 6912 (the only rules that ever fire) hard."""
import sys, os, time, pickle
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, revalidate as rv, leangen
from freemodel import size
import _x6912_rep as R

law = R.law
full = R.VARIANTS['bare']
keepTags = {'free', 'B11l', 'B1l,B11v', 'B1v-struct'}
four = [r for r in full if r[2] in keepTags]
print('four rules:', [r[2] for r in four])
for r in four:
    print('  ', cf.show_rule(r) if hasattr(cf, 'show_rule') else r[2])

t0 = time.time()
f1 = rv.run_tests(law, four, [3, 4, 5], 3000, 12000)
f1 = [f for f in f1 if f[1] != 'recursion']
print('run_tests seeds 3,4,5 fails=%d  %.0fs' % (len(f1), time.time() - t0), flush=True)
for s, r, kind, sd in f1[:5]:
    print('  FAIL', kind, sd, {k: size(v) for k, v in s.items()})
if not f1:
    f2 = rv.run_tests(law, four, [77, 78], 3000, 12000)
    f2 = [f for f in f2 if f[1] != 'recursion']
    print('fresh seeds 77,78 fails=%d' % len(f2), flush=True)
    for sd in (1234, 4321, 20260829):
        C = cf.Closed(law, four)
        t, f = cf.deep_tests(C, law, 20000, 900, sd)
        f = [x for x in f if x[1] != 'recursion']
        print('deep 20000 seed %d: tested %d fails %d' % (sd, t, len(f)), flush=True)
    pickle.dump(four, open('gen/_x6912_four.pkl', 'wb'))
