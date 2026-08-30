"""23357: strong validation of a candidate set from gen/_w3_23357_sets2.py, then further drops.

Oracle (gen/_x23357_drop.py's, the one that killed the 11-rule and 6-rule sets that `run_tests` passed):
    rv.run_tests + gen/_x23357_hunt.py's per-rule/per-chain-slot hunter + two deep runs.
usage: python gen/_w3_23357_strong.py <setname> [--drop]
"""
import sys, time
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, D + '/gen')
import closedform as cf, revalidate as rv
import importlib.util
G = D + '/gen/'
sspec = importlib.util.spec_from_file_location('_w3_23357_sets2', G + '_w3_23357_sets2.py')
S = importlib.util.module_from_spec(sspec)
argv = list(sys.argv); sys.argv = [sys.argv[0]]
sspec.loader.exec_module(S)
law = S.law
hspec = importlib.util.spec_from_file_location('_x23357_hunt', G + '_x23357_hunt.py')


def hunt_with(rules, nper=14, seeds=(41, 42, 43)):
    hm = importlib.util.module_from_spec(hspec)
    hspec.loader.exec_module(hm)
    hm.rules = rules; hm.law = law
    bad = 0; tot = 0
    for sd in seeds:
        n, b = hm.hunt(nper, sd)
        tot += n; bad += len(b)
    return tot, bad


def ok(rules, deep=(515, 616), N=12000):
    t0 = time.time()
    f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
    if f:
        return False, 'run_tests %d %s' % (len(f), {a: b for a, b in f[0][0].items()})
    t, b = hunt_with(rules)
    if b:
        return False, 'hunt %d of %d' % (b, t)
    for sd in deep:
        C = cf.Closed(law, rules)
        _, ff = cf.deep_tests(C, law, N, 240, sd)
        ff = [q for q in ff if q[1] != 'recursion']
        if ff:
            return False, 'deep seed %d: %d' % (sd, len(ff))
    return True, 'hunt %d clean, %.0fs' % (t, time.time() - t0)


if __name__ == '__main__':
    name = argv[1] if len(argv) > 1 else 'a5'
    rules = S.SETS[name]
    for r in rules:
        print('   ', cf.show_rule(r), flush=True)
    g, why = ok(rules)
    print('%s  %d rules  STRONG ok=%s  %s' % (name, len(rules), g, why), flush=True)
    if g and '--drop' in argv:
        keep = list(rules)
        for r in list(rules):
            if r[2] == 'free':
                continue
            trial = [q for q in keep if q is not r]
            gg, w = ok(trial)
            if gg:
                keep = trial
                print('  DROP %-8s -> %d rules' % (r[2], len(keep)), flush=True)
            else:
                print('  KEEP %-8s (%s)' % (r[2], w), flush=True)
        print('FINAL', [r[2] for r in keep], flush=True)
    if g:
        # the heaviest deep runs, 3 seeds x 20,000, on the surviving set
        for sd in (2026, 8291, 77771):
            C = cf.Closed(law, rules)
            t0 = time.time()
            _, ff = cf.deep_tests(C, law, 20000, 300, sd)
            ff = [q for q in ff if q[1] != 'recursion']
            print('  deep20k seed %d: fails %d (%.0fs)' % (sd, len(ff), time.time() - t0), flush=True)
