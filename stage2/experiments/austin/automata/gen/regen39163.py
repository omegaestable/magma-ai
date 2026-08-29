"""regenerate gen/rec39163.lean from the repaired 5-rule set (R1-R4 as extracted + R5, the payload-through-R4 repair)"""
import sys, os, json
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import leangen
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V))))], A1(A2(A2(V))), 'free')
R2 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B11l')
R3 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), TG(U), OPEQ(OP(A1(U), U), A1(A2(V)))], A1(A2(A2(V))), 'B10l')
R4 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(U), OPEQ(OP(A1(U), U), A1(A2(V))), OPEQ(OP(A1(U), U), A2(A2(V)))], A1(U), 'B10l,B11l')
R5 = ([TG(V), EQ(U, A1(V)), TG(A2(V)), TG(U), EQ(A1(U), A2(U)), EQ(A1(U), A1(A2(V))), OPEQ(OP(A1(A2(V)), A2(V)), A1(U))], JJ(A2(V), U), 'rep5')
res = leangen.emit(39163, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen', rules_override=[R1, R2, R3, R4, R5])
print(json.dumps(res))
