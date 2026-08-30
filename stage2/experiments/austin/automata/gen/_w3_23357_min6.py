"""23357: STRONG validation of the never-validated 6-rule minimised set, then further drops.

gen/_x23357_val12.out ends at `minimised 12 -> 6 rules` -- the script (gen/_x23357_min.py) was cut off
before its own follow-up validation printed, and its drop oracle was only `rv.run_tests`, the oracle that
passed a set gen/_x23357_drop.py later proved FALSE.  So re-validate with the strong oracle
(run_tests + the rule/slot hunter + two deep runs), then try to drop further.
"""
import sys, os, time
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, revalidate as rv
import importlib.util
G = D + '/gen/'
spec = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law = mod.law
ALL = list(mod.rules)
TAG = {r[2]: r for r in ALL}
hspec = importlib.util.spec_from_file_location('_x23357_hunt', G + '_x23357_hunt.py')

KEEP6 = ['free', 'Bs|rd:A0', 'Bs|ex:Qa', 'Bs|ex:Qb', 'A0s,B1s|rd:A0', 'As']


def hunt_with(rules, nper=12, seeds=(41, 42)):
    hm = importlib.util.module_from_spec(hspec)
    hspec.loader.exec_module(hm)
    hm.rules = rules; hm.law = law
    bad = 0
    for sd in seeds:
        n, b = hm.hunt(nper, sd)
        bad += len(b)
    return bad


def ok(rules, label=''):
    t0 = time.time()
    f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 2500, 9000) if q[1] != 'recursion']
    if f:
        return False, 'run_tests %d %s' % (len(f), {a: b for a, b in f[0][0].items()})
    b = hunt_with(rules)
    if b:
        return False, 'hunt %d' % b
    for sd in (515, 616):
        C = cf.Closed(law, rules)
        t, ff = cf.deep_tests(C, law, 12000, 200, sd)
        ff = [q for q in ff if q[1] != 'recursion']
        if ff:
            return False, 'deep %d' % len(ff)
    return True, '%.0fs' % (time.time() - t0)


if __name__ == '__main__':
    keep = [TAG[t] for t in KEEP6]
    g, why = ok(keep)
    print('BASELINE 6 rules  ok=%s  %s' % (g, why), flush=True)
    print('  tags', [r[2] for r in keep], flush=True)
    if not g:
        sys.exit(0)
    for r in list(keep):
        if r[2] == 'free':
            continue
        trial = [q for q in keep if q is not r]
        gg, w = ok(trial)
        if gg:
            keep = trial
            print('  DROP %-18s -> %d rules' % (r[2], len(keep)), flush=True)
        else:
            print('  KEEP %-18s (%s)' % (r[2], w), flush=True)
    print('FINAL %d rules:' % len(keep), [r[2] for r in keep], flush=True)
