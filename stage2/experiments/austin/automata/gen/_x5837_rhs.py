"""Emit the `theorem rhs` block for another goal of law 5837, using leangen's own logic."""
import sys, os, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, pvars, rand_term
from laws import parse_eq

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ_(U, A2(A1(A2(A2(V))))), EQ_(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R2p = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R3 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
q = A1(U); xx = A1(q)
common = [EQ_(V, U), TG(U), TG(A2(U)), EQ_(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ_(xx, A2(A1(A2(q)))), EQ_(xx, A2(A2(q)))], xx, 'R4a')
R4b = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(q)))], xx, 'R4b')
R4bp = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), OPEQ(OP(xx, xx), A1(A2(q)))], xx, 'R4bp')
R4c = (common + [TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A2(q)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(xx)))], xx, 'R4c')
RULES = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]

EQ = 5837
GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 25964
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
C2 = cf.Closed(law, RULES)
print('dualized', dualized)

def evg(p, s):
    if isinstance(p, str): return s[p]
    a, b = evg(p[0], s), evg(p[1], s)
    return C2.op(b, a) if dualized else C2.op(a, b)

g = normalise(parse_eq(cat[GOAL])); gv = pvars(g[1])
print('goal', cat[GOAL], 'normalised', g, 'vars', gv)
cand = []
for perm in [(0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 0, 1), (1, 0, 0), (0, 1, 1)]:
    s = {v: ('g', perm[i % 3]) for i, v in enumerate(gv)}
    if s[g[0]] != evg(g[1], s):
        cand.append(s); break
if not cand:
    random.seed(EQ)
    for _ in range(3000):
        s = {v: rand_term(2) for v in gv}
        if s[g[0]] != evg(g[1], s):
            cand.append(s); break
assert cand, 'NO REFUTING TRIPLE'
s = cand[0]
pnames = ', '.join('P%d' % (k + 1) for k in range(len(RULES)))
def lt(t):
    if t[0] == 'g': return 'g %d' % t[1]
    return 'J (%s) (%s)' % (lt(t[1]), lt(t[2]))
def lp(p):
    if isinstance(p, str): return lt(s[p])
    return ('op (%s) (%s)' % (lp(p[1]), lp(p[0]))) if dualized else ('op (%s) (%s)' % (lp(p[0]), lp(p[1])))
block = ('theorem rhs : \u00ac @EquationRHS M inst := by\n  intro h\n  have := h %s\n  revert this\n  change \u00ac %s = %s\n  simp (config := {decide := true}) [op.eq_1, sz, ' + pnames + ']\n') % (
    ' '.join('(%s)' % lt(s[v]) for v in ['x'] + [w for w in gv if w != 'x'] if v in s), lt(s[g[0]]), lp(g[1]))
print('----- RHS BLOCK -----')
print(block)
open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x5837_rhs_%d.txt' % GOAL, 'w', encoding='utf-8', newline='\n').write(block)
