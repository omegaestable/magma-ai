# -*- coding: utf-8 -*-
"""Repair 10218 against the UNION of both oracles.

Measured this session, symmetrically:
  minimise against the fuzz battery alone -> 6 rules, battery-clean, 288 force3 fails
  minimise against force3 alone           -> 5 rules, force3-clean, 78 run_tests + 50 deep + 1 exh
So score every candidate on BOTH.  Cheap proxy during the search:
  force3 (1,476 constructed assignments) + exhaustive terms_upto(7,1)+terms_upto(5,2) (19,683).
The winner is then put through the full battery by gen/_x10218_validate.py.
"""
import sys, os, itertools, json, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq
import _x10218_force3 as F3
law = F3.law
FULL = cf.Extractor(law).rules(exist=False)
BYTAG = {}
for r in FULL: BYTAG.setdefault(r[2], r)
R6 = F3.RULES
POOL = sc.terms_upto(7, 1) + sc.terms_upto(5, 2)
POOL = list(dict.fromkeys(POOL))
TRIPLES = list(itertools.product(POOL, repeat=3))
print('battery proxy: %d assignments; force3: 1476' % len(TRIPLES), flush=True)

def exh(rules):
    C = cf.Closed(law, rules); bad = 0
    for x, y, z in TRIPLES:
        try:
            r = C.op(y, C.op(C.op(x, y), C.op(C.op(z, x), y)))
        except RecursionError:
            continue
        if r != x: bad += 1
    return bad

def score(rules):
    try:
        _, bad = F3.evaluate(rules); f = len(bad)
    except RecursionError:
        return 10 ** 9, 10 ** 9
    try:
        e = exh(rules)
    except RecursionError:
        return f, 10 ** 9
    return f, e

f, e = score(R6)
print('6-rule model: force3 %d, exh %d' % (f, e), flush=True)
cur = list(R6)
for rd in range(6):
    if f == 0 and e == 0: break
    best = None; have = {q[2] for q in cur}
    for r in FULL:
        if r[2] in have: continue
        for pos in (1, len(cur)):
            trial = cur[:pos] + [r] + cur[pos:]
            f2, e2 = score(trial)
            key = (f2 + e2, f2, e2)
            if best is None or key < best[0]: best = (key, r[2], pos, trial, f2, e2)
    if best is None or best[0][0] >= f + e:
        print('no improvement at force3 %d exh %d' % (f, e), flush=True); break
    f, e, cur = best[4], best[5], best[3]
    print('add [%s] at %d -> force3 %d, exh %d, %d rules' % (best[1], best[2], f, e, len(cur)), flush=True)
print('after adding: force3 %d exh %d, %d rules %s' % (f, e, len(cur), [r[2] for r in cur]), flush=True)
if f == 0 and e == 0:
    i = 0
    while i < len(cur):
        trial = cur[:i] + cur[i + 1:]
        f2, e2 = score(trial)
        if f2 == 0 and e2 == 0:
            cur = trial; print('  drop -> %d rules' % len(cur), flush=True)
        else:
            i += 1
    print('MINIMAL on the union: %d rules %s' % (len(cur), [r[2] for r in cur]), flush=True)
    json.dump({'eq': 10218, 'scored_on': 'force3+exh', 'tags': [r[2] for r in cur]},
              open(os.path.join(HERE, 'gen', '_x10218_union_set.json'), 'w'))
