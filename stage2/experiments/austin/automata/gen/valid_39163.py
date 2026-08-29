import sys, os, json
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 39163
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized', dualized, 'law', law)

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQg(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), EQg(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQg(U, A2(A1(A2(V)))), TG(A2(A2(V))), EQg(U, A2(A2(A2(V))))], A1(A2(A2(V))), 'free')
R2 = ([TG(V), EQg(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQg(U, A2(A1(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B11l')
R3 = ([TG(V), EQg(U, A1(V)), TG(A2(V)), TG(A2(A2(V))), EQg(U, A2(A2(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A1(A2(V)))], A1(A2(A2(V))), 'B10l')
R4 = ([TG(V), EQg(U, A1(V)), TG(A2(V)), TG(U), OPEQ(OP(A1(U), U), A1(A2(V))), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B10l,B11l')
R5 = ([TG(V), EQg(U, A1(V)), TG(A2(V)), TG(U), EQg(A1(U), A2(U)), EQg(A1(U), A1(A2(V))), OPEQ(OP(A1(A2(V)), A2(V)), A1(U))], JJ(A2(V), U), 'rep5')
rules = [R1, R2, R3, R4, R5]

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('FAILS', len(fails))
for f in fails[:10]:
    print(f)
