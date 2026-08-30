"""Replay the constructed guard-2 witness against EVERY 23357 rule set on record."""
import sys
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr
import importlib.util
G = D + '/gen/'
show = tr.show
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)

sv = list(sys.argv); sys.argv = [sys.argv[0]]
r12 = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
M12 = importlib.util.module_from_spec(r12); r12.loader.exec_module(M12)
s2 = importlib.util.spec_from_file_location('_w3_23357_sets2', G + '_w3_23357_sets2.py')
S = importlib.util.module_from_spec(s2); s2.loader.exec_module(S)
law = M12.law
TAG12 = {r[2]: r for r in M12.rules}
MIN6 = ['free', 'Bs|rd:A0', 'Bs|ex:Qa', 'Bs|ex:Qb', 'A0s,B1s|rd:A0', 'As']

SETS = {
    'full12': list(M12.rules),
    'min6(false)': [TAG12[t] for t in MIN6],
    'a5': S.SETS['a5'],
    'f4': S.SETS['f4'],
    'a6': S.SETS['a6'],
    'a7': S.SETS['a7'],
    'b6': S.SETS['b6'],
    'c8': S.SETS['c8'],
    'd7': S.SETS['d7'],
    'e7': S.SETS['e7'],
}

y1 = J(J(g(3), g(2)), g(3))
x1 = J(g(2), J(g(3), g(0)))
y = J(J(y1, x1), y1)
z = J(x1, J(y1, g(0)))
print('y1 =', show(y1), '  x1 =', show(x1), flush=True)
for name, rules in SETS.items():
    C = cf.Closed(law, rules)
    inner = C.op(y1, x1)
    line = '%-12s inner op(y1,x1) %s' % (name, 'FREE' if inner == J(y1, x1) else 'DECODED->' + show(inner)[:40])
    oks = 0; tot = 0
    for x in (g(7), g(8), g(9)):
        C = cf.Closed(law, rules)
        try:
            A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B); top = C.op(U, V)
        except RecursionError:
            line += '  RECURSION'; continue
        tot += 1
        if top == x: oks += 1
        cell = (('AD' if A != J(y, x) else 'AF'), ('UD' if U != J(A, y) else 'UF'),
                ('BD' if B != J(y, z) else 'BF'), ('VD' if V != J(x, B) else 'VF'))
    print('%s   law holds %d/%d   cell=%s' % (line, oks, tot, str(cell)), flush=True)
