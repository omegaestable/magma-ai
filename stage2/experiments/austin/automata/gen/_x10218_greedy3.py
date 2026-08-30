# -*- coding: utf-8 -*-
"""Minimise/repair 10218 AGAINST THE FORCING SUITE (force3), not the fuzz battery.

Step 1: evaluate the 6-rule model and the greedy-8 candidate from _x10218_greedy.log on force3.
Step 2: greedy-add rules from the full 140-rule extraction, scored on force3, until 0 fails.
Step 3: greedy-drop, re-scored on force3, to get a minimal set.
"""
import sys, os, itertools, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
import _x10218_force3 as F3
law = F3.law
FULL = cf.Extractor(law).rules(exist=False)
BYTAG = {}
for r in FULL: BYTAG.setdefault(r[2], r)
R6 = F3.RULES
print('full extraction', len(FULL), 'rules; 6-rule model tags', [r[2] for r in R6], flush=True)

def score(rules):
    try:
        n, bad = F3.evaluate(rules)
    except RecursionError:
        return 10 ** 9, 0
    return len(bad), n

f6, n6 = score(R6)
print('6-rule model on force3: %d assignments, %d fails' % (n6, f6), flush=True)
CAND8 = ['free', 'B0l,B10s|B0:flff', 'B10l|B10:flff', 'B10l', 'B1l', 'B1l,B10l', 'B0l', 'B0l,B10l']
c8 = [BYTAG[t] for t in CAND8 if t in BYTAG]
if len(c8) == len(CAND8):
    f8, n8 = score(c8)
    print('greedy-8 candidate on force3: %d assignments, %d fails' % (n8, f8), flush=True)
else:
    print('greedy-8: missing tags', [t for t in CAND8 if t not in BYTAG], flush=True)
    c8 = list(R6); f8 = f6

cur = c8 if f8 <= f6 else list(R6)
f = min(f8, f6)
for rd in range(6):
    if f == 0: break
    best = None; have = {q[2] for q in cur}
    for r in FULL:
        if r[2] in have: continue
        for pos in (1, len(cur)):
            trial = cur[:pos] + [r] + cur[pos:]
            f2, _ = score(trial)
            if best is None or f2 < best[0]: best = (f2, r[2], pos, trial)
    if best is None or best[0] >= f:
        print('ADD: no further improvement at %d fails' % f, flush=True); break
    f, cur = best[0], best[3]
    print('add [%s] at %d -> %d fails, %d rules' % (best[1], best[2], f, len(cur)), flush=True)
print('after adding: %d fails, %d rules %s' % (f, len(cur), [r[2] for r in cur]), flush=True)
if f == 0:
    i = 0
    while i < len(cur):
        trial = cur[:i] + cur[i + 1:]
        f2, _ = score(trial)
        if f2 == 0:
            cur = trial; print('  drop -> %d rules' % len(cur), flush=True)
        else:
            i += 1
    print('MINIMAL on force3: %d rules %s' % (len(cur), [r[2] for r in cur]), flush=True)
    import json
    json.dump({'eq': 10218, 'scored_on': 'force3', 'tags': [r[2] for r in cur]},
              open(os.path.join(HERE, 'gen', '_x10218_force3_set.json'), 'w'))
