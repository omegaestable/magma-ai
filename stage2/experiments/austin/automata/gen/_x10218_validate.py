# -*- coding: utf-8 -*-
"""Validate a 10218 candidate rule set against BOTH oracles: the fuzz battery AND force3.
Minimising against either alone produced a false model this session (battery -> the 6-rule set;
force2 -> the greedy-8).  The criterion is the union."""
import sys, os, json, time, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x10218_force3 as F3
law = F3.law
FULL = cf.Extractor(law).rules(exist=False)
BYTAG = {}
for r in FULL: BYTAG.setdefault(r[2], r)
TAGS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else \
    ["B10l|B10:flfl", "B0l,B10s|B0:flff", "B10l|B10:flff", "B10l", "B0l"]
rules = [BYTAG[t] for t in TAGS]
print('candidate: %d rules %s' % (len(rules), TAGS), flush=True)
t0 = time.time()
n, bad = F3.evaluate(rules)
print('force3      : %6d assignments, %d fails  (%.0fs)' % (n, len(bad), time.time() - t0), flush=True)
t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests   : %d fails  (%.0fs)' % (len(fails), time.time() - t0), flush=True)
kinds = {}
for f in fails[:2000]:
    k = f[1] if len(f) > 1 and isinstance(f[1], str) else 'value'
    kinds[k] = kinds.get(k, 0) + 1
if fails: print('   kinds', kinds)
C = cf.Closed(law, rules)
for sd in (10218, 987654, 555):
    t0 = time.time(); nn, ff = cf.deep_tests(C, law, 20000, 300, sd)
    print('deep %-7d: %d tested, %d fails (%.0fs)' % (sd, nn, len(ff), time.time() - t0), flush=True)
pool = sc.terms_upto(9, 1) + sc.terms_upto(7, 2)
pool = list(dict.fromkeys(pool))
C2 = cf.Closed(law, rules)
t0 = time.time(); nx = 0; bx = 0
def J(a, b): return ('J', a, b)
for x, y, z in itertools.product(pool, repeat=3):
    try:
        r = C2.op(y, C2.op(C2.op(x, y), C2.op(C2.op(z, x), y)))
    except RecursionError:
        continue
    nx += 1
    if r != x: bx += 1
print('exhaustive  : %d assignments, %d fails (%.0fs)' % (nx, bx, time.time() - t0), flush=True)
ok = (len(bad) == 0 and len(fails) == 0 and bx == 0)
print('VERDICT:', 'PASSES BOTH ORACLES' if ok else 'FAILS')
if ok:
    leangen.emit(10218, os.path.join(HERE, 'gen', 'rep10218b'), rules_override=rules)
    print('emitted gen/rep10218b/')
