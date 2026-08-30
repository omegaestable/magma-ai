# -*- coding: utf-8 -*-
"""Greedy repair of the 6-rule 10218 model against the corrected forced-firing suite."""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import _x10218_repair as RP
R6, FULL, suite = RP.R6, RP.FULL, RP.suite
cur = list(R6); n, f = suite(cur)
print('start fails', f, flush=True)
for rd in range(5):
    best = None
    have = {q[2] for q in cur}
    for i, r in enumerate(FULL):
        if r[2] in have: continue
        for pos in (1, len(cur)):
            trial = cur[:pos] + [r] + cur[pos:]
            try: n2, f2 = suite(trial)
            except RecursionError: continue
            if best is None or f2 < best[0]: best = (f2, i + 1, r[2], pos, trial)
    if best is None or best[0] >= f:
        print('no further improvement', flush=True); break
    f = best[0]; cur = best[4]
    print('round %d: add R%d [%s] at pos %d -> %d fails, %d rules'
          % (rd + 1, best[1], best[2], best[3], f, len(cur)), flush=True)
    if f == 0: break
print('FINAL fails', f, 'rules', len(cur), [r[2] for r in cur], flush=True)
