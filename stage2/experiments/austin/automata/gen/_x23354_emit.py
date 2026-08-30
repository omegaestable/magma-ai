"""Emit the completed 6-rule package for 23354 into gen/rep23354/."""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); R = ns['rules']
U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e); A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e); EQc = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b); OP = lambda a, b: ('OP', a, b)
U2c = [TG(U), TG(V), OPEQ(OP(A2(U), A1(V)), A1(U))]
V2c = [TG(A1(V)), TG(A1(A1(V))), EQc(A1(A1(A1(V))), A2(A1(V))), EQc(A2(A1(A1(V))), A2(V))]
V3c = [TG(A1(V)), OPEQ(OP(A2(A1(V)), A2(V)), A1(A1(V)))]
rules = R + [(U2c + V2c, A1(V), 'U2xV2'), (U2c + V3c, A1(V), 'U2xV3')]

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests real fails', len(real))
assert not real
out = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep23354'
os.makedirs(out, exist_ok=True)
print(leangen.emit(EQ, out, rules_override=rules))
