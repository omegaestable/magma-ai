"""Emit the `theorem rhs` block for another row of law 24200 (same op, different goal)."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import leangen
from closedform import Closed
from freemodel import normalise, catalog, rand_term
from laws import parse_eq, load_rows

EQ = 24200
GID = int(sys.argv[1])
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C2 = Closed(law, rules)
pvars = leangen.pvars


def evg(p, s):
    if isinstance(p, str): return s[p]
    a, b = evg(p[0], s), evg(p[1], s)
    return C2.op(b, a) if dualized else C2.op(a, b)


g = normalise(parse_eq(cat[GID])); gv = pvars(g[1])
print('goal', GID, cat[GID], 'vars', gv, 'dualized', dualized)
s = None
for perm in [(0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 0, 1), (1, 0, 0), (0, 1, 1)]:
    t = {v: ('g', perm[i % 3]) for i, v in enumerate(gv)}
    if t[g[0]] != evg(g[1], t):
        s = t; break
if s is None:
    random.seed(EQ)
    for _ in range(3000):
        t = {v: rand_term(2) for v in gv}
        if t[g[0]] != evg(g[1], t):
            s = t; break
assert s is not None, 'no refuting assignment found'
print('assignment', s, '->', evg(g[1], s))

pnames = ', '.join('P%d' % (k + 1) for k in range(len(rules)))


def lt(t):
    if t[0] == 'g': return 'g %d' % t[1]
    return 'J (%s) (%s)' % (lt(t[1]), lt(t[2]))


def lp(p):
    if isinstance(p, str): return lt(s[p])
    return ('op (%s) (%s)' % (lp(p[1]), lp(p[0]))) if dualized else ('op (%s) (%s)' % (lp(p[0]), lp(p[1])))


block = ('theorem rhs : ¬ @EquationRHS M inst := by\n  intro h\n  have := h %s\n  revert this\n'
         '  change ¬ %s = %s\n  simp (config := {decide := true}) [op.eq_1, sz, ' + pnames + ']\n') % (
    ' '.join('(%s)' % lt(s[v]) for v in ['x'] + [w for w in gv if w != 'x'] if v in s),
    lt(s[g[0]]), lp(g[1]))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_x24200_rhs_%d.txt' % GID), 'w',
     encoding='utf-8', newline='\n').write(block)
print(block)
