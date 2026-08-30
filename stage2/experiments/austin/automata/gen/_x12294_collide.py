"""Decisive test for 12294: does the encoding map  (x,z) |-> s4  collide for a fixed y?

The law demands  op(y, s4(x,y,z)) = x.  If s4(x1,y,z1) = s4(x2,y,z2) with x1 != x2 then NO magma whose
chain evaluates that way can satisfy the law -- the obstruction is the model, not the rule set.
"""
import sys, itertools, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import smallcheck as sc
import _x12294_model as MM
from _x12294_drive import show, law

RULES = getattr(MM, sys.argv[1] if len(sys.argv) > 1 else 'RULES_E2')
MS = int(sys.argv[2]) if len(sys.argv) > 2 else 11
GN = int(sys.argv[3]) if len(sys.argv) > 3 else 1

pool = sc.terms_upto(MS, GN)
print('pool', len(pool))
A, B = law[1]           # A = 'y',  B = ((z*y)*x)*(x*y)
C = MM.Model(RULES)
hits = 0
for y in pool:
    seen = {}
    for x in pool:
        for z in pool:
            s = {'x': x, 'y': y, 'z': z}
            s4 = C.evp(B, s)
            prev = seen.get(s4)
            if prev is None:
                seen[s4] = (x, z)
            elif prev[0] != x:
                hits += 1
                if hits <= 6:
                    print('COLLISION y=%s' % show(y))
                    print('   x1=%s z1=%s' % (show(prev[0]), show(prev[1])))
                    print('   x2=%s z2=%s' % (show(x), show(z)))
                    print('   s4=%s' % show(s4))
print('collisions:', hits)
