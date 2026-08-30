"""Hand rule sets for law 21864:  x = (y * (z * x)) * (x * (x * y))   (both-compound).

u = A = op(y, P),  P = op(z, x)      v = B = op(x, Q),  Q = op(x, y)
generic shapes:  u = J y (J z x)     v = J x (J x y)

Import RULES from here; gen/_x21864_run.py validates/classifies whichever set is named.
"""
U = ('U',)
V = ('V',)


def A1(e):
    return ('A1', e)


def A2(e):
    return ('A2', e)


def OP(a, b):
    return ('OP', a, b)


def TG(e):
    return ('TG', e)


def EQ(a, b):
    return ('EQ', a, b)


def OPEQ(a, b):
    return ('OPEQ', a, b)


# ---- the generated 9 (verbatim from gen/chk21864.py, re-expressed) -----------------------------
R1 = ([TG(U), TG(A2(U)), TG(V), EQ(A2(A2(U)), A1(V)), TG(A2(V)),
       EQ(A2(A2(U)), A1(A2(V))), EQ(A1(U), A2(A2(V)))], A2(A2(U)), 'free')

R2 = ([TG(U), TG(A2(U)), TG(V), EQ(A2(A2(U)), A1(V)),
       OPEQ(OP(A2(A2(U)), A1(U)), A2(V))], A2(A2(U)), 'B1s')

R3 = ([TG(U), TG(A2(U)),
       OPEQ(OP(A2(A2(U)), OP(A2(A2(U)), A1(U))), V)], A2(A2(U)), 'Bs')

R4 = ([TG(U), TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), EQ(A1(U), A2(A2(V))),
       TG(A1(V)), EQ(A2(U), A1(A1(V))), TG(A2(A1(V))), EQ(A2(U), A1(A2(A1(V))))], A1(V), 'A1s')

R5 = ([TG(U), TG(V), TG(A1(V)), EQ(A2(U), A1(A1(V))), TG(A2(A1(V))), EQ(A2(U), A1(A2(A1(V)))),
       OPEQ(OP(A1(V), A1(U)), A2(V))], A1(V), 'A1s,B1s')

R6 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))), TG(A2(A2(A2(V)))),
       EQ(U, A2(A2(A2(A2(V))))), TG(A1(V)), EQ(U, A1(A1(V))), EQ(A1(A2(A2(V))), A2(A1(V))),
       OPEQ(OP(A2(A2(V)), OP(U, A1(V))), U)], A1(V), 'As')

R7 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))), TG(A2(A2(A2(V)))),
       EQ(U, A2(A2(A2(A2(V))))), OPEQ(OP(U, A1(A2(A2(V)))), A1(V)),
       OPEQ(OP(A2(A2(V)), OP(U, A1(V))), U)], A1(V), 'As|rd:B1')

R8 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))), TG(A2(A2(A2(V)))),
       EQ(U, A2(A2(A2(A2(V))))), TG(A1(V)), EQ(U, A1(A1(V))),
       EQ(A1(A2(A2(V))), A2(A1(V)))], A1(V), 'As~')

R9 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))), TG(A2(A2(A2(V)))),
       EQ(U, A2(A2(A2(A2(V))))), OPEQ(OP(U, A1(A2(A2(V)))), A1(V))], A1(V), 'As|rd:B1~')

GEN = [R1, R2, R3, R4, R5, R6, R7, R8, R9]

# ---- repairs ----------------------------------------------------------------------------------
# (a) A1s with the level-2 B-side inner product decoded: x = J(P, W) with W = op(P, y') for SOME y'
#     (y' occurs only inside the forgotten z, so it is existentially quantified: drop the guard).
R4b = ([TG(U), TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), EQ(A1(U), A2(A2(V))),
        TG(A1(V)), EQ(A2(U), A1(A1(V)))], A1(V), 'A1s~')

# (b) same, with B's inner node decoded at the top (v.2 = op(x,y))
R5b = ([TG(U), TG(V), TG(A1(V)), EQ(A2(U), A1(A1(V))),
        OPEQ(OP(A1(V), A1(U)), A2(V))], A1(V), 'A1s,B1s~')

# (c) A1s where the level-2 encoding's INNER product decoded:
#     P decoded => exists y'. x = op(P, op(P,y')).  x = J(P,W) free-outer, and op(P,y') = W by a DECODE
#     needs P = op(Y, op(Z,W)) for some Y,Z, structurally P = J(Y, J(Z, W)) with W = a2 x.
R4c = ([TG(U), TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), EQ(A1(U), A2(A2(V))),
        TG(A1(V)), EQ(A2(U), A1(A1(V))),
        TG(A2(U)), TG(A2(A2(U))), EQ(A2(A2(A2(U))), A2(A1(V)))], A1(V), 'A1s|l2')

# (c') same with B's inner node decoded at the top (v.2 = op(x,y) rather than J x y)
R5c = ([TG(U), TG(V), TG(A1(V)), EQ(A2(U), A1(A1(V))),
        TG(A2(U)), TG(A2(A2(U))), EQ(A2(A2(A2(U))), A2(A1(V))),
        OPEQ(OP(A1(V), A1(U)), A2(V))], A1(V), 'A1s,B1s|l2')

# (z) maximally permissive last-resort: v is an encoding J(x, J(x, _)) -> x, no u condition at all.
RZ = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V)))], A1(V), 'Z')
# (z2) same but requiring the y-slot to match u's head when u is a J is impossible in the DSL;
#      instead require v's y-slot to be a J (weak discriminator)
RZ2 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A1(V))], A1(V), 'Z2')

# ---- As-level analogues of R4/R4c ---------------------------------------------------------------
# A decoded with y free-shaped: y = J(Y2, J(Z2, u)),  P := J(u, J(u, Y2))  is then determined.
# Enc(x, P) has three branches: E1 (x = J(u,Y2))  = R6/R8 ; E2a ; E2b.
Y2 = A1(A2(A2(V)))
PEXP = ('J', U, ('J', U, Y2))
ASPRE = [TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))), TG(A2(A2(A2(V)))),
         EQ(U, A2(A2(A2(A2(V)))))]

R6d = (ASPRE + [TG(A1(V)), EQ(A1(A1(V)), PEXP), TG(A2(A1(V))), EQ(A1(A2(A1(V))), PEXP)], A1(V), 'As|E2a')
R6e = (ASPRE + [TG(A1(V)), EQ(A1(A1(V)), PEXP), EQ(A2(A1(V)), Y2)], A1(V), 'As|E2b')

# ---- the RECURSIVE As rule -----------------------------------------------------------------------
# Acc(p,q,w) := "exists t, op(p, op(t,q)) = w".  The final pair needs v = J(x,J(x,y)) and Acc(y,x,u).
# Acc(p,q,w) has a recursive branch:  tg q = 2 & a1 q = w & Acc(a2 q, w, p),
# and Acc(p',q',w') holds iff op(w', J(q', J(q', p'))) = q'  (the model's own final-pair decode).
# With (p,q,w) = (y,x,u) that guard is   op(y, J(u, J(u, a2 x))) == u ,
# whose recursion measure sz p + sz q + sz w strictly decreases.  This replaces R6..R9.
RA = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A1(V)), EQ(U, A1(A1(V))),
       OPEQ(OP(A2(A2(V)), ('J', U, ('J', U, A2(A1(V))))), U)], A1(V), 'Arec')

# ---- As with the y-side inner product decoded ----------------------------------------------------
# A decoded to u:  y = op(Y2, op(Z2,u)) with op(Z2,u) DECODED to Wp = a2 y   [Enc(u,Wp) branch (a2)]
# and P := op(u, op(u, Y2)) must satisfy Enc(x, P) branch (a1): tg P = 2 & a2 P = x.
WP = A2(A2(A2(V)))
PE = OP(U, OP(U, Y2))
RB = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))),
       TG(U), EQ(A1(U), WP), TG(A2(U)), EQ(A1(A2(U)), WP),
       TG(PE), EQ(A2(PE), A1(V))], A1(V), 'As|yEnc')

# ---- B1s with y reconstructed from the R1-shape of the (x,y) decode ------------------------------
# v = J(x, Q) with Q = op(x,y) DECODED by the free rule R1: then y = J(Q, J(Q, a1 x)) is DETERMINED.
# Validate it with op(x, y) == Q; the A-side is then only constrained by a1 x = u.
YREC = ('J', A2(V), ('J', A2(V), A1(A1(V))))
RC = ([TG(V), TG(A1(V)), EQ(U, A1(A1(V))), OPEQ(OP(A1(V), YREC), A2(V))], A1(V), 'B1s|yrec')

# ---- B1s (Q = op(x,y) decoded by R1, y reconstructed) + As with a1 x = u --------------------------
# v = J(x, Q); y := J(Q, J(Q, a1 x)) validated by op(x,y) == Q.  Then Acc(a2 x, u, y) is needed
# (RA's branch) but its canonical guard op(y, J(u,J(u,a2 x))) == u is GATE-CUT; the equivalent
# branch-(b) instantiation  op(a2 x, op(a1 (a2 x), u)) == y  is below the gate.
RD = ([TG(V), TG(A1(V)), EQ(U, A1(A1(V))), TG(A2(A1(V))), TG(A1(A2(A1(V)))),
       OPEQ(OP(A1(V), YREC), A2(V)),
       OPEQ(OP(A2(A1(V)), OP(A1(A2(A1(V))), U)), YREC)], A1(V), 'B1s|yrec|Arec2')

# ---- RB with Enc(u, a2 y) taken through its (a2)(ii) branch --------------------------------------
# Enc(q,W) = "exists t, op(t,q) = W";  branch (a2): q = J(W, W2) with W2 = op(W,Y) for some Y, and
#   (i)  W2 = J(W,Y) free            -> tg W2 = 2 & a1 W2 = W        (RB)
#   (ii) op(W,Y) decoded             -> tg W = 2 & tg (a2 W) = 2 & a2 (a2 W) = W2   (RB2)
RB2 = ([TG(V), TG(A2(V)), EQ(A1(V), A1(A2(V))), TG(A2(A2(V))),
        TG(U), EQ(A1(U), WP), TG(WP), TG(A2(WP)), EQ(A2(A2(WP)), A2(U)),
        TG(PE), EQ(A2(PE), A1(V))], A1(V), 'As|yEnc2')
