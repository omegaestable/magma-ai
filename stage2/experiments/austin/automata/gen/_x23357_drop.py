"""23357: validated removal with a STRONG acceptance test (rv.run_tests + the targeted gap hunter).

The plain validator is demonstrably incomplete on this law: the 11-rule set passed run_tests on three
seeds, three 20,000-deep runs and the exhaustive small-term check, and was still FALSE (gen/_x23357_gaps.py).
So a rule is dropped only if the full validator AND the rule-driven chain hunter stay clean.
"""
import sys, os, time, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv
import importlib.util
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
spec = importlib.util.spec_from_file_location('_x23357_rep', D + '_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law = mod.law
hspec = importlib.util.spec_from_file_location('_x23357_hunt', D + '_x23357_hunt.py')


def hunt_with(rules, nper=12, seeds=(41, 42)):
    hm = importlib.util.module_from_spec(hspec)
    hm.__dict__['__name__'] = '_hunt_lib'
    hspec.loader.exec_module(hm)
    hm.rules = rules
    hm.law = law
    bad = 0
    for sd in seeds:
        n, b = hm.hunt(nper, sd)
        bad += len(b)
    return bad


def ok(rules):
    f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 2500, 9000) if q[1] != 'recursion']
    if f:
        return False, 'run_tests %d' % len(f)
    b = hunt_with(rules)
    if b:
        return False, 'hunt %d' % b
    for sd in (515, 616):
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, 12000, 200, sd)
        f = [q for q in f if q[1] != 'recursion']
        if f:
            return False, 'deep %d' % len(f)
    return True, ''


if __name__ == '__main__':
    rules = list(mod.rules)
    keep = list(rules)
    t0 = time.time()
    good, why = ok(keep)
    print('baseline %d rules ok=%s %s (%.0fs)' % (len(keep), good, why, time.time() - t0), flush=True)
    dropped = []
    for r in list(rules):
        if r[2] == 'free':
            continue
        trial = [q for q in keep if q is not r]
        g, why = ok(trial)
        if g:
            keep = trial
            dropped.append(r[2])
            print('  DROP %-16s -> %d rules  (%.0fs)' % (r[2], len(keep), time.time() - t0), flush=True)
        else:
            print('  KEEP %-16s (%s)  (%.0fs)' % (r[2], why, time.time() - t0), flush=True)
    print('FINAL %d rules:' % len(keep), [q[2] for q in keep], flush=True)
