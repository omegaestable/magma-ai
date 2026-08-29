"""Emit the repaired 5837 skeleton (8 rules: R1 R2 R2' R3 R4a R4b R4b' R4c) into gen/repair5837/ via leangen.emit.
Does not touch gen/rec5837.lean."""
import sys, os
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import leangen
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ(U, A2(A1(A2(A2(V))))), EQ(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R2p = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R3 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
q = A1(U); x = A1(q)
common = [EQ(V, U), TG(U), TG(A2(U)), EQ(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ(x, A2(A1(A2(q)))), EQ(x, A2(A2(q)))], x, 'R4a')
R4b = (common + [TG(A2(q)), EQ(x, A2(A2(q))), TG(x), TG(A2(x)), OPEQ(OP(A1(A2(x)), x), A1(A2(q)))], x, 'R4b')
R4bp = (common + [TG(A2(q)), EQ(x, A2(A2(q))), OPEQ(OP(x, x), A1(A2(q)))], x, 'R4bp')
R4c = (common + [TG(x), TG(A2(x)), OPEQ(OP(A1(A2(x)), x), A2(q)), OPEQ(OP(A1(A2(x)), x), A1(A2(x)))], x, 'R4c')
rules = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]
out = 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen\\repair5837'
leangen.emit(5837, out, rules_override=rules)
print('emitted into', out, os.listdir(out))
