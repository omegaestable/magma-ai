"""23357: deep validation of the 11-rule repaired set + validated-removal minimisation."""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
law = mod.law
rules = mod.rules

t0 = time.time()
for sd in (2026, 8291, 77771):
    C = cf.Closed(law, rules)
    tested, f = cf.deep_tests(C, law, 20000, 300, sd)
    f = [q for q in f if q[1] != 'recursion']
    print('deep20k seed %d: tested %d fails %d  (%.1fs)' % (sd, tested, len(f), time.time() - t0), flush=True)
    if f:
        print('   ', f[0])

print('--- validated removal ---', flush=True)
C = cf.Closed(law, rules)
cf.deep_tests(C, law, 1500, 120, 991)
order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    bad = [q for q in rv.run_tests(law, trial, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
    if bad:
        print('  KEEP  %-16s (fired %d)  %d fails' % (r[2], C.fired.get(i, 0), len(bad)), flush=True)
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-16s (fired %d) -> %d rules' % (r[2], C.fired.get(i, 0), len(keep)), flush=True)
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped), flush=True)
bad = [q for q in rv.run_tests(law, keep, [77, 78], 3000, 12000) if q[1] != 'recursion']
print('fresh-seed validation fails:', len(bad), flush=True)
for sd in (5551, 6662):
    C2 = cf.Closed(law, keep)
    tested, f = cf.deep_tests(C2, law, 20000, 300, sd)
    f = [q for q in f if q[1] != 'recursion']
    print('min deep20k seed %d: fails %d' % (sd, len(f)), flush=True)
    bad += f
print('OVERALL BAD', len(bad))
print('KEPT TAGS', [r[2] for r in keep])
print('total %.1fs' % (time.time() - t0))
