"""Full validation standard for the 2-rule 32281 model."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2
import closedform as cf, smallcheck as sc
from freemodel import size

RULES = [R1, R2]
for r in RULES:
    print(cf.show_rule(r))

t0 = time.time()
f1, r1 = report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag='run_tests[3,4,5]')
f2, r2 = report(LAW, RULES, seeds=(77, 78), N=3000, NF=12000, tag='run_tests[77,78]')

for sd in (101, 202, 303, 404):
    C = cf.Closed(LAW, RULES)
    t, f = cf.deep_tests(C, LAW, 20000, 300, sd)
    print('deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)

for ms, g in ((9, 1), (5, 2), (11, 1), (6, 2)):
    n, f = sc.exhaustive(cf.Closed(LAW, RULES), LAW, ms, g, limit=25)
    print('exhaustive size<=%d gens=%d : %d tested, %d fails' % (ms, g, n, len(f)), flush=True)

print('total %.1fs' % (time.time() - t0))
