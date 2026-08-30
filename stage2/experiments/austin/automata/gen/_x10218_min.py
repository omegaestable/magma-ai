"""law 10218 : x = y * ((x*y) * ((z*x)*y))   -- L-form, not dualized.

closedform (legacy) emits 111 rules (80 KB skeleton, unshippable).
closedform2 (EXTRACTOR_NOTES.md) emits ~63.  Both need heavy minimisation.

Pipeline:
  1. extract with closedform2 (+ soundness filter)
  2. firing census over a large battery -> drop every rule that never fired (batch removal,
     the linear-ish minimiser EXTRACTOR_NOTES.md asks for)
  3. FULL validation of the survivors (rv.run_tests seeds [3,4,5], deep 3000, fuzz 12000)
  4. validated-removal greedy pass on what is left
  5. fresh-seed validation + 20k deep on two more seeds
Writes gen/_x10218_rules.py with the final rule literal.
"""
import sys, os, time, threading, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, fuzz as fz, smallcheck as sc, leangen
import closedform2 as cf2
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 10218


def census(law, rules, seeds, N, NF):
    tot = {}
    def add(C):
        for k, v in C.fired.items():
            tot[k] = tot.get(k, 0) + v
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules); sc.exhaustive(C, law, ms, g, limit=25); add(C)
        print('  census exh%d/%d distinct %d' % (ms, g, len(tot)), flush=True)
    for sd in seeds:
        C = cf.Closed(law, rules); cf.deep_tests(C, law, N, 600, sd); add(C)
        C = cf.Closed(law, rules); fz.fuzz(C, law, rules, NF, seed=sd + 100); add(C)
        C = cf.Closed(law, rules); fz.closure_fuzz(C, law, NF, seed=sd + 200); add(C)
        C = cf.Closed(law, rules); fz.critical_fuzz(C, law, NF, seed=sd + 300); add(C)
        print('  census seed %d distinct %d' % (sd, len(tot)), flush=True)
    return tot


def full(law, rules, seeds=(3, 4, 5)):
    f = rv.run_tests(law, rules, list(seeds), 3000, 12000)
    return [x for x in f if x[1] != 'recursion']


def main():
    cat = catalog(); law = normalise(parse_eq(cat[EQ]))
    print('law', law, flush=True)
    t0 = time.time()
    rules, info = cf2.extract(law)
    print('closedform2 extract', json.dumps(info), '%.1fs' % (time.time() - t0), flush=True)
    for i, r in enumerate(rules):
        print('  R%-3d %s' % (i + 1, cf2.show_rule(r)), flush=True)

    t = time.time()
    real = full(law, rules)
    print('FULL SET run_tests real fails %d  %.1fs' % (len(real), time.time() - t), flush=True)
    for x in real[:5]:
        print('   FAIL', {k: size(v) for k, v in x[0].items()}, x[2], x[3], flush=True)
    if real:
        print('FULL SET IS NOT A MODEL - stop', flush=True)
        return

    t = time.time()
    tot = census(law, rules, [3, 4, 5, 7, 991], 2500, 6000)
    print('census %.1fs, distinct fired %d' % (time.time() - t, len(tot)), flush=True)
    for i in sorted(tot):
        print('  fired R%-3d %-45s %d' % (i + 1, rules[i][2], tot[i]), flush=True)

    keep = [rules[i] for i in sorted(tot)]
    print('batch drop -> %d rules' % len(keep), flush=True)
    t = time.time()
    real = full(law, keep)
    print('BATCH run_tests real fails %d  %.1fs' % (len(real), time.time() - t), flush=True)
    if real:
        for x in real[:5]:
            print('   FAIL', {k: size(v) for k, v in x[0].items()}, x[2], x[3], flush=True)
        print('batch drop unsafe; keeping full set', flush=True)
        keep = rules

    # greedy validated removal, least-fired first
    order = sorted(range(len(keep)), key=lambda i: tot.get(rules.index(keep[i]), 0) if keep[i] in rules else 0)
    cur = list(keep)
    for i in order:
        r = keep[i]
        if r[2] == 'free':
            continue
        if r not in cur:
            continue
        trial = [q for q in cur if q is not r]
        if not trial:
            continue
        f = rv.run_tests(law, trial, [601], 1500, 6000)
        if [x for x in f if x[1] != 'recursion']:
            print('  KEEP %s' % r[2], flush=True)
            continue
        cur = trial
        print('  DROP %s -> %d rules' % (r[2], len(cur)), flush=True)

    print('minimised -> %d rules' % len(cur), flush=True)
    real = full(law, cur, seeds=(77, 78, 79))
    print('FRESH-SEED run_tests real fails %d' % len(real), flush=True)
    if real:
        print('fell back to batch set', flush=True)
        cur = keep
        real = full(law, cur, seeds=(77, 78, 79))
        print('  batch set fresh seeds real fails %d' % len(real), flush=True)

    for sd in (20260829, 12345):
        C = cf.Closed(law, cur)
        n, f = cf.deep_tests(C, law, 20000, 900, sd)
        f = [x for x in f if x[1] != 'recursion']
        print('deep 20000 seed %d : tested %d value fails %d' % (sd, n, len(f)), flush=True)

    for i, r in enumerate(cur):
        print('FINAL R%-3d %s' % (i + 1, cf2.show_rule(r)), flush=True)
    with open('gen/_x10218_rules.py', 'w', encoding='utf-8') as fh:
        fh.write('# minimised validated rule set for law 10218 (closedform2 + batch/greedy removal)\n')
        fh.write('rules = %r\n' % (cur,))
    print('wrote gen/_x10218_rules.py with %d rules' % len(cur), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=main)
th.start()
th.join()
