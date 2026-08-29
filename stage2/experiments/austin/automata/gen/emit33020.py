"""emit33020.py : emit the REFINED repaired skeleton for law 33020 (op = free model of the dual L-form law 12883)
into gen/repair33020/ via leangen.emit (rules_override).  Rules: R2full, R3full, R4a, R4b of gen/fix33020b.py.
Does not touch gen/rec33020.lean."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import leangen
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
X = A1(A1(V)); Z = A1(A2(A1(V))); S1 = OP(U, X)
R2f = ([('TG', V), ('TG', A1(V)), ('TG', A2(A1(V))), ('EQ', U, A2(V)),
        ('OPEQ', S1, A2(A2(A1(V)))), ('OPEQ', OP(Z, A2(A2(A1(V)))), A2(A1(V))),
        ('OPEQ', OP(X, A2(A1(V))), A1(V)), ('OPEQ', OP(A1(V), U), V)], X, 'R2full')
R3f = ([('TG', V), ('TG', A1(V)), ('EQ', U, A2(V)), ('TG', S1),
        ('OPEQ', OP(A2(S1), S1), A2(A1(V))), ('OPEQ', OP(X, A2(A1(V))), A1(V)), ('OPEQ', OP(A1(V), U), V)], X, 'R3full')
XU = A2(A1(U)); S3 = OP(XU, A1(U))
R4a = ([('TG', V), ('EQ', U, A2(V)), ('TG', U), ('TG', A1(U)), ('TG', A2(U)),
        ('OPEQ', OP(U, XU), JJ(U, XU)), ('OPEQ', S3, A2(A2(U))), ('OPEQ', OP(A1(A2(U)), A2(A2(U))), A2(U)),
        ('OPEQ', OP(A1(U), A2(U)), U), ('OPEQ', S3, A1(V)), ('OPEQ', OP(A1(V), U), V)], XU, 'R4a')
R4b = ([('TG', V), ('EQ', U, A2(V)), ('TG', U), ('TG', A1(U)),
        ('OPEQ', OP(U, XU), JJ(U, XU)), ('TG', S3), ('OPEQ', OP(A2(S3), S3), A2(U)),
        ('OPEQ', OP(A1(U), A2(U)), U), ('OPEQ', S3, A1(V)), ('OPEQ', OP(A1(V), U), V)], XU, 'R4b')
REFINED = [R2f, R3f, R4a, R4b]
out = os.path.join(HERE, 'repair33020')
print(json.dumps(leangen.emit(33020, out, rules_override=REFINED)))
print('emitted into', out, os.listdir(out))
