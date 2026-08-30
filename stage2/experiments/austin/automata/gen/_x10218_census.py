"""Firing census for law 10218's 111-rule generated set, then a batch drop of the
never-fired rules, then FULL validation of the survivor set.

Rationale: validated-removal one rule at a time is ~111 x run_tests = hours at this rule
count.  A batch drop of rules that never fire in a large battery, followed by the full
validation standard on the survivors, is the same soundness argument applied once.
"""
import sys, os, time, threading, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, fuzz as fz, smallcheck as sc, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 10218
OUT = 'gen/_x10218_census.json'


def load_rules():
    src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def census(law, rules, seeds, N, NF):
    tot = {}
    def add(C):
        for k, v in C.fired.items():
            tot[k] = tot.get(k, 0) + v
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        sc.exhaustive(C, law, ms, g, limit=25)
        add(C)
        print('  census exh%d/%d done, distinct fired %d' % (ms, g, len(tot)), flush=True)
    for sd in seeds:
        C = cf.Closed(law, rules); cf.deep_tests(C, law, N, 600, sd); add(C)
        C = cf.Closed(law, rules); fz.fuzz(C, law, rules, NF, seed=sd + 100); add(C)
        C = cf.Closed(law, rules); fz.closure_fuzz(C, law, NF, seed=sd + 200); add(C)
        C = cf.Closed(law, rules); fz.critical_fuzz(C, law, NF, seed=sd + 300); add(C)
        print('  census seed %d done, distinct fired %d' % (sd, len(tot)), flush=True)
    return tot


def main():
    cat = catalog(); law = normalise(parse_eq(cat[EQ]))
    rules = load_rules()
    print('nrules', len(rules), flush=True)
    t0 = time.time()
    tot = census(law, rules, [3, 4, 5, 7, 991], 2500, 5000)
    print('census %.1fs' % (time.time() - t0), flush=True)
    fired = sorted(tot.items(), key=lambda kv: -kv[1])
    for i, c in fired:
        print('  R%-4d %-40s fired %d' % (i + 1, rules[i][2], c), flush=True)
    keep_idx = sorted(tot.keys())
    keep = [rules[i] for i in keep_idx]
    print('batch keep %d rules: %s' % (len(keep), [rules[i][2] for i in keep_idx]), flush=True)
    json.dump({'fired': {str(k): v for k, v in tot.items()},
               'keep_idx': keep_idx,
               'keep_tags': [rules[i][2] for i in keep_idx]},
              open(OUT, 'w'), indent=1)
    t = time.time()
    fails = rv.run_tests(law, keep, [3, 4, 5], 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    print('BATCH-DROP run_tests: fails %d real %d  %.1fs' % (len(fails), len(real), time.time() - t), flush=True)
    for f in real[:5]:
        print('  FAIL', {k: size(v) for k, v in f[0].items()}, f[2], f[3], flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=main)
th.start()
th.join()
