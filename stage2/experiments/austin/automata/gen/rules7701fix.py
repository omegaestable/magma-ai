"""Repaired rule set for law 7701 (x = y * (y * ((x * (z * x)) * y))).

The generated set R1..R3 is FALSE: R2 covers "z*x decoded" (z = x.1) and R3 covers "(x*(z*x))*y decoded"
(y = J q2 B with B encoding by q2), but no rule covers BOTH at once, so at the top level
op(y, J y p) falls through to J y (J y p).  R4 is R3 with the J-shape guard on q2.2 replaced by the
R2-style op-guard q2.2 == op(x.1, x).
"""
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)

R1 = ([('TG', V), ('EQ', U, A1(V)), ('TG', A2(V)), ('TG', A1(A2(V))), ('TG', A2(A1(A2(V)))),
       ('EQ', A1(A1(A2(V))), A2(A2(A1(A2(V))))), ('EQ', U, A2(A2(V)))],
      A1(A1(A2(V))), 'free')
R2 = ([('TG', V), ('EQ', U, A1(V)), ('TG', A2(V)), ('TG', A1(A2(V))), ('EQ', U, A2(A2(V))),
       ('TG', A1(A1(A2(V)))), ('OPEQ', OP(A1(A1(A1(A2(V)))), A1(A1(A2(V)))), A2(A1(A2(V))))],
      A1(A1(A2(V))), 'B101l')
R3 = ([('TG', V), ('EQ', U, A1(V)), ('TG', U), ('OPEQ', OP(A1(U), U), A2(V)), ('TG', A1(U)),
       ('TG', A2(A1(U))), ('EQ', A1(A1(U)), A2(A2(A1(U))))],
      A1(A1(U)), 'B1l')
R4 = ([('TG', V), ('EQ', U, A1(V)), ('TG', U), ('OPEQ', OP(A1(U), U), A2(V)), ('TG', A1(U)),
       ('TG', A1(A1(U))), ('OPEQ', OP(A1(A1(A1(U))), A1(A1(U))), A2(A1(U)))],
      A1(A1(U)), 'B1l+B101l')
rules4 = [R1, R2, R3, R4]
