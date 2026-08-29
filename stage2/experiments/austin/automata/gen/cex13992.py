"""cex13992.py : why `theorem law` in gen/rec13992_gen0.lean (the original generator output) is FALSE, and the candidate repair.

1. A concrete instance (Lean-checked in gen/cex13992.lean) on which the shipped rules violate the law:
   x*y reduces through R2 (x = J (J w (J (J P' x') x')) x', y = J (J z' (J P' x)) x), so x != y.1.2.1.2
   and no outer rule recovers x.  Random deep tests reach the same class at ~2 / 10,000.
2. Every rule R2..R12 recovers the left factor of a reduced product by the R1-shape accessor u.1.2.1.2;
   the invariant that actually holds is "op(a,b) reduced  =>  a = b.2".  Variant1 = the shipped rules with
   u.1.2.1.2 -> u.2 and the R1-shape guards J?u.1, J?u.1.2, J?u.1.2.1 dropped.  Bounded evidence only.
Run: python gen/cex13992.py [N]   (default N = 10000 deep tests per seed, seeds 11..14, both rule sets; the accepted rec13992.lean uses the 4-rule variant3 = pruned variant1 with z recovered as Q.2, see rules13992.txt)
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk13992_gen0.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[13992]))
U = ('U',); DEEP = ('A2', ('A1', ('A2', ('A1', U))))
def sub(e):
    if e == DEEP: return ('A2', U)
    if e[0] in ('A1', 'A2'): return (e[0], sub(e[1]))
    if e[0] in ('OP', 'J'): return (e[0], sub(e[1]), sub(e[2]))
    return e
def is_u_shape_tg(c):
    return c[0] == 'TG' and c[1] in (('A1', U), ('A2', ('A1', U)), ('A1', ('A2', ('A1', U))))
V1 = []
for conds, res, tag in rules:
    nc = []
    for c in conds:
        if is_u_shape_tg(c): continue
        cc = (c[0],) + tuple(sub(e) for e in c[1:])
        if cc not in nc: nc.append(cc)
    V1.append((nc, sub(res), tag))
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
x = J(J(g(2), J(J(g(0), g(1)), g(1))), g(1)); y = J(J(g(3), J(g(0), x)), x); z = g(4)
def which_rule(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'
def trace(C, R, s):
    x, y, z = s['x'], s['y'], s['z']
    P = C.op(x, y); Q = C.op(P, y); Rr = C.op(z, Q); Sv = C.op(Rr, y); T = C.op(y, Sv)
    return ' | '.join('%s:%s' % (n, which_rule(C, R, a, b)) for n, a, b in
                      [('P=x*y', x, y), ('Q=P*y', P, y), ('R=z*Q', z, Q), ('S=R*y', Rr, y), ('T=y*S', y, Sv)]), T == x
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
for name, R in (('shipped', rules), ('variant1', V1)):
    C = cf.Closed(law, R)
    print(name, 'hand instance:', trace(C, R, {'x': x, 'y': y, 'z': z}))
    tot = nf = 0; t0 = time.time(); shown = 0
    for seed in (11, 12, 13, 14):
        C = cf.Closed(law, R)
        tested, fails = cf.deep_tests(C, law, N, 300, seed)
        tot += tested; nf += len(fails)
        for s, l in fails:
            if shown < 3: print('   fail sizes x,y,z =', size(s['x']), size(s['y']), size(s['z']), '->', trace(C, R, s)[0]); shown += 1
    print(name, 'deep tests', tot, 'fails', nf, 'secs', round(time.time() - t0, 1))
if '--rules' in sys.argv:
    for r in V1: print(cf.show_rule(r))
