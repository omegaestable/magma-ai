"""Reproduce and explain the 3-rule 12087 failures."""
import sys, os, random, json
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, fuzz as fz, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import trace as tr

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('gen/_x12087out/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

bad = []
for sd in (202, 303):
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 300, sd)
    for s, r in f:
        if r != 'recursion': bad.append(('deep%d' % sd, s, r))
C = cf.Closed(law, rules)
t, f = fz.critical_fuzz(C, law, 12000, seed=303)
for s, r in f:
    if r != 'recursion': bad.append(('crit303', s, r))
print('failures', len(bad))
bad.sort(key=lambda b: sum(size(v) for v in b[1].values()))
for tag, s, r in bad[:6]:
    print('---', tag, {k: size(v) for k, v in s.items()}, 'got size', size(r))
for tag, s, r in bad[:1]:
    print('SMALLEST FAILURE', tag)
    for k in ('x', 'y', 'z'):
        print('  ', k, '=', show(s[k]))
    T = tr.Tracing(law, rules)
    T.trace_on = True
    got = T.evp(law[1], s)
    print('  got', show(got))
    print('  want', show(s['x']))
    for (u, v, which, res) in T.log:
        print('     op(%s , %s) -> [%s] %s' % (show(u), show(v), 'free' if which is None else rules[which][2], show(res)))
    print('  cuts', len(T.cuts))
    for e, a, b, u, v in T.cuts[:10]:
        print('     GATE CUT', cf.show_expr(e), 'pair sizes', (size(a), size(b)), 'vs', (size(u), size(v)))
    json.dump({k: s[k] for k in s}, open('gen/_x12087_failcase.json', 'w'))
