"""Candidate rule sets for the 11081 free model.  Shared by _v11081_ct.py and _v11081_hand.py."""
U = ('U',)
V = ('V',)
a1 = lambda e: ('A1', e)
a2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b)
TG = lambda e: ('TG', e)
EQ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)

P = a1(a1(V))      # payload   v.1.1
AA = a2(a1(V))     # A slot    v.1.2
CC = a2(V)         # C slot    v.2

# tg v = 2, tg (a1 v) = 2, op u (a1 (a1 v)) = a2 (a1 v)
CORE = [TG(V), TG(a1(V)), OPEQ(OP(U, P), AA)]

# ---- readings of "a2 v = op z u for some z" ----
# (1) op z u free:  a2 v = J z u
X1 = (CORE + [TG(CC), EQ(U, a2(CC))], P, 'Cfree')
# (2) op z u decoded, no witness at all (over-approximation; FALSE, see NOTES_11081.md)
X2 = (CORE + [TG(U), TG(a1(U)), EQ(CC, a1(a1(U)))], P, 'Cdec')
# (2b) witness z = a1 (a2 (a1 u))  (the extractor's R9 reading: A-slot of u is free)
X2b = (CORE + [TG(U), TG(a1(U)), TG(a2(a1(U))), OPEQ(OP(a1(a2(a1(U))), U), CC)], P, 'Cdec-A')
# (2c) over-approximation + tg (a1 (a1 u)) = 2
X2c = (CORE + [TG(U), TG(a1(U)), TG(a1(a1(U))), EQ(CC, a1(a1(U)))], P, 'Cdec-J')
# (2e) witness z = a2 (a2 u)  (the X1 reading of u's own encoding: C-slot of u is free)
X2e = (CORE + [TG(U), TG(a1(U)), TG(a2(U)), EQ(CC, a1(a1(U))),
               OPEQ(OP(a2(a2(U)), a1(a1(U))), a2(a1(U)))], P, 'Cdec-C')
# (2f) same but stated as "op (a2 (a2 u)) u = a2 v" -- one op call, one level deeper
X2f = (CORE + [TG(U), TG(a1(U)), TG(a2(U)), OPEQ(OP(a2(a2(U)), U), CC)], P, 'Cdec-C2')

SETS = {
    'x1': [X1],
    'x12': [X1, X2],
    'x12b': [X1, X2b],
    'x12c': [X1, X2c],
    'x12e': [X1, X2e],
    'x12f': [X1, X2f],
    'x12be': [X1, X2b, X2e],
    'x12bf': [X1, X2b, X2f],
    'x12ef': [X1, X2e, X2f],
    'x12bef': [X1, X2b, X2e, X2f],
}

# ---- exact free reading: z = a1 (a2 v), verified by op(a1 (a2 v), u) = a2 v ----
Y1 = (CORE + [TG(CC), EQ(U, a2(CC)), OPEQ(OP(a1(CC), U), CC)], P, 'Cfree-x')
# ---- "u is decodable" readings, all with a2 v = a1 (a1 u) ----
DEC = [TG(U), TG(a1(U)), EQ(CC, a1(a1(U)))]
# (D1) u's A-slot is the free pair J z (a1 (a1 u)); witness z = a1 (a2 (a1 u))
D1 = (CORE + DEC + [TG(a2(a1(U))), EQ(a2(a2(a1(U))), a1(a1(U))),
                    OPEQ(OP(a1(a2(a1(U))), a1(a1(U))), a2(a1(U)))], P, 'Dec-Afree')
# (D1s) same without the op re-check
D1s = (CORE + DEC + [TG(a2(a1(U))), EQ(a2(a2(a1(U))), a1(a1(U)))], P, 'Dec-Afree-s')
# (D2) u's A-slot is itself a decoded value of u's payload
D2 = (CORE + DEC + [TG(a1(a1(U))), TG(a1(a1(a1(U)))),
                    EQ(a2(a1(U)), a1(a1(a1(a1(U)))))], P, 'Dec-Adec')
# (D3) u's C-slot is free with key a2 (a2 u) and that key decodes u  (the old X2e)
D3 = (CORE + DEC + [TG(a2(U)), OPEQ(OP(a2(a2(U)), a1(a1(U))), a2(a1(U)))], P, 'Dec-Cfree')

SETS['y1'] = [Y1, D1]
SETS['y1s'] = [Y1, D1s]
SETS['y12'] = [Y1, D1, D2]
SETS['y13'] = [Y1, D1, D3]
SETS['y123'] = [Y1, D1, D2, D3]
SETS['y1s2'] = [Y1, D1s, D2]
SETS['z1'] = [X1, D1]
SETS['z12'] = [X1, D1, D2]
SETS['z123'] = [X1, D1, D2, D3]

# ---- the closure-motivated design: Dec u = "a canonical key decodes u", two canonical keys ----
# W1 = extractor R8 ; W2 = extractor R9 ; W3 = the a2(a2 u) twin of R9
W1 = (CORE + [TG(CC), EQ(U, a2(CC))], P, 'K1')
W2 = (CORE + [TG(U), TG(a1(U)), TG(a2(a1(U))), OPEQ(OP(a1(a2(a1(U))), U), CC)], P, 'K2a')
W3 = (CORE + [TG(U), TG(a1(U)), TG(a2(U)), OPEQ(OP(a2(a2(U)), U), CC)], P, 'K2b')
SETS['w12'] = [W1, W2]
SETS['w13'] = [W1, W3]
SETS['w123'] = [W1, W2, W3]
SETS['w123y'] = [Y1, W2, W3]
