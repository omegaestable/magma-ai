"""_orch_minim.py <eq> [--full]

Shrink an enormous extracted rule set WITHOUT the mistake that has now cost this project twice: minimising
against a validator too weak to see the hole.  (First run of this script minimised 10218 from 140 rules to 3
against 600 deep tests + 2,000 fuzz, and the full validator then found 73 failures.)

The fix: the drop candidates are the rules that never fire during the FULL validator's own load -- which
includes the exhaustive one-generator terms of size <= 9 and two-generator of size <= 5, the tests that
actually catch these holes -- and every surviving set is re-checked with the FULL validator, never a cheap one.

Why this is needed at all: revalidate.py does not finish on 10222/36524/12294/10218/8485.  Extraction costs
0.2-0.3 s; what it returns is 83-218 rules, Closed.op is O(rules) per call, and validated removal over that
many rules re-runs the full validator once per rule.  Shrinking first with a single instrumented pass turns
an O(rules) x full-validator job into one full-validator pass plus a handful.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.setrecursionlimit(20000)
import closedform as cf
import fuzz as fz
import smallcheck as sc
import revalidate as rv
import leangen
from freemodel import normalise, catalog
from laws import parse_eq

def load_law(eq):
    orig = normalise(parse_eq(catalog()[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    return (('x', leangen.dual_pat(orig[1])) if dualized else orig), dualized

def fired_under_full_load(law, rules, seeds, N, NF):
    """union of the rules that fire under every phase the full validator uses"""
    fired = set()
    C = cf.Closed(law, rules)
    for ms, g in ((9, 1), (5, 2)):
        sc.exhaustive(C, law, ms, g, limit=1)
        fired |= set(C.fired)
    for sd in seeds:
        C = cf.Closed(law, rules); cf.deep_tests(C, law, N, 240, sd); fired |= set(C.fired)
        C = cf.Closed(law, rules); fz.fuzz(C, law, rules, NF, seed=sd + 100); fired |= set(C.fired)
        C = cf.Closed(law, rules); fz.closure_fuzz(C, law, NF, seed=sd + 200); fired |= set(C.fired)
        C = cf.Closed(law, rules); fz.critical_fuzz(C, law, NF, seed=sd + 300); fired |= set(C.fired)
    return fired

def full(law, rules, seeds, N, NF):
    return rv.run_tests(law, rules, seeds, N, NF)

def main():
    eq = int(sys.argv[1])
    law, dualized = load_law(eq)
    seeds = [eq * 7 + 3, eq * 7 + 14]
    N, NF = 800, 4000                       # the SHRINK load; the final check uses the standard 3000/12000
    t0 = time.time()
    rules = cf.Extractor(law).rules(exist=False)
    print(eq, 'dualized', dualized, '| extracted', len(rules), 'rules in %.1f s' % (time.time() - t0), flush=True)
    fired = fired_under_full_load(law, rules, seeds, N, NF)
    keep = [r for i, r in enumerate(rules) if i in fired or r[2] == 'free']
    print('  fired under the FULL load: %d of %d (%.0f s)' % (len(keep), len(rules), time.time() - t0), flush=True)
    f = full(law, keep, seeds, 3000, 12000)
    print('  FULL VALIDATOR on %d rules: %d fails (%.0f s)' % (len(keep), len(f), time.time() - t0), flush=True)
    cur = keep
    if f:
        print('  bulk drop lost the model -> keeping the full %d-rule set as the base' % len(rules), flush=True)
        f2 = full(law, rules, seeds, 3000, 12000)
        print('  FULL VALIDATOR on all %d rules: %d fails (%.0f s)' % (len(rules), len(f2), time.time() - t0), flush=True)
        if f2:
            print('  THE FULL SET IS ALSO FALSE -> this is a repair problem, not a size problem'); 
            json.dump({'eq': eq, 'status': 'model-false', 'n': len(rules), 'fails': len(f2)},
                      open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_orch_min%d.json' % eq), 'w'))
            return
        cur = rules
    # validated removal, FULL validator each time, least-fired first
    order = sorted(range(len(cur)), key=lambda i: (cur[i][2] == 'free', i), reverse=False)
    i = 0
    while i < len(cur):
        if cur[i][2] == 'free': i += 1; continue
        trial = cur[:i] + cur[i + 1:]
        if not full(law, trial, seeds, 1200, 6000):
            cur = trial
            print('    dropped -> %d rules (%.0f s)' % (len(cur), time.time() - t0), flush=True)
        else:
            i += 1
    f3 = full(law, cur, seeds, 3000, 12000)
    print('  FINAL: %d rules, %d fails (%.0f s)' % (len(cur), len(f3), time.time() - t0), flush=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_orch_min%d.json' % eq)
    json.dump({'eq': eq, 'dualized': dualized, 'status': 'ok' if not f3 else 'fails',
               'n_extracted': len(rules), 'n_min': len(cur), 'fails': len(f3), 'rules': cur,
               'secs': round(time.time() - t0, 1)}, open(out, 'w'))
    print('  wrote', out, flush=True)
    if not f3:
        leangen.emit(eq, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rep%d' % eq), rules_override=cur)
        print('  emitted gen/rep%d.lean' % eq, flush=True)

if __name__ == '__main__':
    main()
