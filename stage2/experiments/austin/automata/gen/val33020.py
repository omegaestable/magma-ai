"""val33020.py : validate the EMITTED package gen/repair33020 (its chk33020.py rule list, exec'd) against the
L-form law 12883 that `theorem law` states: hand instances I1..I5, fresh deep seeds 31/32, fuzz seed 10."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(HERE, 'repair33020', 'chk33020.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[12883]))
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
y1 = J(J(g(0), J(g(2), J(g(1), g(0)))), g(1)); cy = J(y1, J(g(2), g(0)))
x3 = J(g(1), J(g(1), J(g(0), g(1)))); xb = J(g(1), g(1)); s2b = J(J(g(0), J(g(2), J(xb, g(0)))), xb)
INST = {'I1': {'x': g(1), 'y': J(y1, J(g(2), J(g(1), y1))), 'z': g(1)}, 'I2': {'x': g(1), 'y': cy, 'z': g(1)},
        'I3': {'x': x3, 'y': J(g(0), g(1)), 'z': x3}, 'I4': {'x': xb, 'y': J(s2b, J(g(2), g(0))), 'z': xb},
        'I5': {'x': cy, 'y': J(J(g(0), cy), J(g(2), g(1))), 'z': cy}}
C = cf.Closed(law, rules)
A, B = law[1]
for k, s in INST.items():
    print(k, 'law holds:', C.op(C.evp(A, s), C.evp(B, s)) == s['x'])
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
for seed in (31, 32):
    C = cf.Closed(law, rules); t0 = time.time()
    tested, fails = cf.deep_tests(C, law, N, 120, seed)
    print('deep seed', seed, ':', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
C = cf.Closed(law, rules); t0 = time.time()
tested, fails = fz.fuzz(C, law, rules, N, seed=10)
print('fuzz seed 10 :', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
print('emitted rules:')
for r in rules: print('  ', cf.show_rule(r))
