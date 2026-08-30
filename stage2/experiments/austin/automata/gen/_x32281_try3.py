"""32281: is R2 redundant given R3?  (R3's guard subsumes R2's when s3 is free.)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2
from _x32281_try2 import R3
import closedform as cf

for name, RULES in (('R1+R3   ', [R1, R3]), ('R1+R2+R3', [R1, R2, R3])):
    print('===', name)
    for r in RULES:
        print('   ', cf.show_rule(r))
    report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag=name + ' [3,4,5]')
    report(LAW, RULES, seeds=(77, 78), N=3000, NF=12000, tag=name + ' [77,78]')
    for sd in (101, 202, 303):
        C = cf.Closed(LAW, RULES)
        t, f = cf.deep_tests(C, LAW, 20000, 300, sd)
        print('   deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)
