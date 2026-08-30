"""Rule set for law 40037 (dual L-form: x = z * (x * (z * ((y * x) * y)))).

Chain of the law, with u = z, v = t4:
    t1 = op(y, x)      t2 = op(t1, y)      t3 = op(z, t2)      t4 = op(x, t3)      op(z, t4) = x

The generated 6 rules cover the modes where t4 is free and (t3 free, t2 free, t1 free/decoded)
and the root-decoded families.  The hole (2 failing instances, one deep one critical):

    t1 DECODED  =>  x = v.1 is itself an encoding whose *z_role* is y, i.e.  y = v.1.2.1.
    Once y is recovered there, the whole chain can be replayed as one nested guard.

  * instance A (deep):  t1 decoded, t2 free, t3 DECODED, t4 free  -- v.2 is the decoded t3, so t2
    (and with it y) is gone from v; but t1 decoded puts y at v.1.2.1.
  * instance B (critical): t1 decoded, t2 DECODED, t3 free, t4 free -- v.2.2 is the decoded t2, so
    again y is gone from v, and again t1 decoded puts y at v.1.2.1.

R7 replays the chain from Y := v.1.2.1 with a single nested guard, so it covers both:
    J?v & J?v.1 & J?v.1.2 & op(u, op(op(v.1.2.1, v.1), v.1.2.1)) == v.2  ->  v.1

which is R5 with its decoder re-aimed: R5 reads Y at v.1.2.2.1.1 (the y_role of x's own encoding),
R7 reads it at v.1.2.1 (the z_role of x's own encoding), which is the occurrence a decoded t1
provably guarantees.  (PLAYBOOK_REPAIR.md §4a.)
"""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)

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


def load_generated():
    src = open(os.path.join(HERE, 'gen', 'chk40037.py'), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


Y = A1(A2(A1(V)))                      # v.1.2.1 -- y, when s1 = op(y,x) DECODED (then x = J s1 (J y R))
Y2 = A1(A2(V))                         # v.2.1 -- y, when s3 decoded onto a FREE s1 (v.2 = s1 = J y x)

# R7: replay the whole chain from Y.
R7 = ([TG(V), TG(A1(V)), TG(A2(A1(V))),
       OPEQ(OP(U, OP(OP(Y, A1(V)), Y)), A2(V))],
      A1(V), 'B1l,rdY')

# R7s: R7 plus the fact that makes Y readable at all -- s1 = op(y,x) really is a1 x.
R7s = ([TG(V), TG(A1(V)), TG(A2(A1(V))),
        OPEQ(OP(Y, A1(V)), A1(A1(V))),
        OPEQ(OP(U, OP(OP(Y, A1(V)), Y)), A2(V))],
       A1(V), 'B1l,rdY+')

# R8: replay from Y2.
R8 = ([TG(V), TG(A2(V)),
       OPEQ(OP(U, OP(OP(Y2, A1(V)), Y2)), A2(V))],
      A1(V), 'B1l,rdY2')

# R8s: R8 with the structural shape v = J x (J y x) of its case.
R8s = ([TG(V), TG(A2(V)), EQ(A2(A2(V)), A1(V)),
        OPEQ(OP(U, OP(OP(Y2, A1(V)), Y2)), A2(V))],
       A1(V), 'B1l,rdY2+')

# R8p: the same case with no op-guard at all (the outer op(u, s2) is gate-cut when sz s2 >= sz v).
R8p = ([TG(V), TG(A2(V)), EQ(A2(A2(V)), A1(V))],
       A1(V), 'B1l,rdY2~')

# R8q: v = J x (J y x) with the *inner* half of the replay only (always gate-admissible).
R8q = ([TG(V), TG(A2(V)), EQ(A2(A2(V)), A1(V)),
        OPEQ(OP(Y2, A1(V)), A2(V))],
       A1(V), 'B1l,rdY2i')

# R10: R7 with R5's structural guards -- x = v.1 must have the *shape* of an encoding
# (J?v.1.2.2, J?v.1.2.2.1), which is what a decoded s1 = op(y,x) forces.  Without them R7 fires
# on one-generator coincidences (the exh9/1 instance) and derails s3.
R10 = ([TG(V), TG(A1(V)), TG(A2(A1(V))), TG(A2(A2(A1(V)))), TG(A1(A2(A2(A1(V))))),
        OPEQ(OP(U, OP(OP(Y, A1(V)), Y)), A2(V))],
       A1(V), 'B1l,rdY2g')

# R11: R10 plus the fully-free shape of x's own encoding.
R11 = ([TG(V), TG(A1(V)), TG(A2(A1(V))), TG(A2(A2(A1(V)))), TG(A1(A2(A2(A1(V))))),
        EQ(A2(A1(A2(A2(A1(V))))), A1(A1(V))),
        EQ(A1(A1(A2(A2(A1(V))))), A2(A2(A2(A1(V))))),
        OPEQ(OP(U, OP(OP(Y, A1(V)), Y)), A2(V))],
       A1(V), 'B1l,rdYfull')

# ---- the UNIFORM design: every rule verifies the whole chain
#      a2 v = op u (op (op Y (a1 v)) Y)   with Y read at one of three provable positions.
#      Then `op u v != J u v` implies  EX Y, a2 v = op u (op (op Y (a1 v)) Y)  by construction.
YA = A2(A2(A2(V)))                     # y when s3 and s2 are free (v.2 = J u (J s1 y))


def replay(Y):
    return OPEQ(OP(U, OP(OP(Y, A1(V)), Y)), A2(V))


QA = ([TG(V), TG(A2(V)), TG(A2(A2(V))), replay(YA)], A1(V), 'QA')
QAu = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), replay(YA)], A1(V), 'QAu')
QB = ([TG(V), TG(A1(V)), TG(A2(A1(V))), TG(A2(A2(A1(V)))), TG(A1(A2(A2(A1(V))))),
       EQ(A2(A1(A2(A2(A1(V))))), A1(A1(V))),
       EQ(A1(A1(A2(A2(A1(V))))), A2(A2(A2(A1(V))))),
       replay(Y)], A1(V), 'QB')
QC = ([TG(V), TG(A2(V)), EQ(A2(A2(V)), A1(V)), replay(Y2)], A1(V), 'QC')

GEN = load_generated()
# 1..6 generated, 7 R7, 8 R8, 9 R7s, 10 R8s, 11 R8p, 12 R8q, 13 R10, 14 R11
ALL = GEN + [R7, R8, R7s, R8s, R8p, R8q, R10, R11, QA, QAu, QB, QC]  # 15 QA, 16 QAu, 17 QB, 18 QC
RULES = GEN + [R7, R8]
