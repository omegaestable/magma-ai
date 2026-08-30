"""Second repair for 6912: the self-squaring tower rule.

After R15 (B1v-struct) is added, 20,000-deep tests expose a SECOND hole, the tower
    y  arbitrary with tg y = 2 and a1 y = a2 y,   z = J y y,   x = J z z.
The law instance (X:=y, Y:=x, Z:=g) forces  op(x, J x y) = y  (that is R15, so R15 is not optional),
and then the instance (X:=x, Y:=y, Z:=z) forces

    op(y, J y y) = J (J y y) (J y y)

because  op(z,z) = J z z = x free,  op(x,y) = J x y free,  op(x, J x y) = y  by R15,
op(y,y) = J y y = z free, and the law's last product must return x = J z z = J v v.

So the model needs a rule whose RESULT IS BIGGER than its arguments:

    R16 [tower] :  tg v = 2 & a1 v = u & a2 v = u & tg u = 2 & a1 u = a2 u   ->   J v v

Side conditions of that reading are automatic: with z'' = v = J u u and x'' = J v v,
op(v,v), op(J v v, u) and op(u,u) are all free (every rule needs `u = a1 v`, which fails
on those pairs by size), and op(x'', J x'' u) = u is exactly R15.
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, revalidate as rv
from freemodel import size
import _x6912_rep as R

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)

R16 = ([TG(V), EQ_(U, A1(V)), EQ_(U, A2(V)), TG(U), EQ_(A1(U), A2(U))], ('J', V, V), 'tower')

law = R.law
base = R.VARIANTS['bare']                       # 14 generated + R15
FULL16 = base + [R16]
FOUR16 = [r for r in base if r[2] in {'free', 'B11l', 'B1l,B11v', 'B1v-struct'}] + [R16]
VAR = {'full16': FULL16, 'four16': FOUR16}

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'four16'
    rules = VAR[which]
    print('%s rules(%d):' % (which, len(rules)), [r[2] for r in rules], flush=True)
    tot = 0
    for sd in (1234, 4321, 20260829, 55555):
        C = cf.Closed(law, rules)
        t, fl = cf.deep_tests(C, law, 20000, 900, sd)
        fl = [x for x in fl if x[1] != 'recursion']
        tot += len(fl)
        print('deep 20000 seed %d: tested %d fails %d' % (sd, t, len(fl)), flush=True)
        for s, r in fl[:3]:
            print('   FAIL', {k: size(v) for k, v in s.items()}, flush=True)
    print('TOTAL deep fails:', tot, flush=True)
