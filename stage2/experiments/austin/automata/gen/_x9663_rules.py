"""Candidate rule sets for law 9663  (x = y * ((z*y) * (x*(x*y)))).

Generated 49-rule set lives in gen/chk9663.py.  Only 7 ever fire under deep+fuzz+closure+critical:
  R1 free, R2 B11l, R3 B1l,B11v, R7 B0l, R10 B0l|B0:flff, R11 B0l,B11l, R15 B0l,B1l,B11v
"""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)

U = ('U',)
V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(o, w): return ('OPEQ', o, w)


def gen_rules():
    src = open(os.path.join(HERE, 'gen/chk9663.py'), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


G = gen_rules()
# 1-based indices of the rules that ever fired
LIVE = [1, 2, 3, 7, 10, 11, 15]


def pick(idx):
    return [G[i - 1] for i in idx]


# ---- hand rules -------------------------------------------------------------
# z recovered through u.2.2.2 instead of u.1.2 (the 9667-style relocation):
# op(z,u) decoded  =>  u = J (J z' z) (J x' (J x' z)) , so z is at u.1.2 AND at u.2.2.2.
R7b = ([TG(V), TG(A2(V)), TG(A2(A2(V))), EQ(A1(A2(V)), A1(A2(A2(V)))), EQ(U, A2(A2(A2(V)))),
        TG(U), TG(A2(U)), TG(A2(A2(U))), OPEQ(OP(A2(A2(A2(U))), U), A1(V))],
       A1(A2(V)), 'B0l@222')
R11b = ([TG(V), TG(A2(V)), TG(U), TG(A2(U)), TG(A2(A2(U))),
         OPEQ(OP(A2(A2(A2(U))), U), A1(V)), OPEQ(OP(A1(A2(V)), U), A2(A2(V)))],
        A1(A2(V)), 'B0l,B11l@222')

SETS = {
    'live7': pick(LIVE),
    'live6': pick([1, 2, 3, 7, 11, 15]),
    'live5': pick([1, 2, 7, 11, 15]),
    'live4': pick([1, 2, 7, 11]),
    'live3': pick([1, 2, 11]),
    'live6b': pick([1, 2, 3, 7, 11, 15]) + [R7b],
    'live7b': pick([1, 2, 3, 7, 11, 15]) + [R7b, R11b],
    'live8b': pick([1, 2, 3, 7, 10, 11, 15]) + [R7b],
}

# ---- soft rules: drop the v.1 (= op(z,u)) verification, which is not locatable when
#      op(z'',z) and op(P,z) both decode (the exh9/1 hole: y = (g0*(g0*g0)), z = ((g0*g0)*(g0*(g0*g0)))).
S1 = ([TG(V), TG(A2(V)), OPEQ(OP(A1(A2(V)), U), A2(A2(V)))], A1(A2(V)), 'soft:B11l')
S0 = ([TG(V), TG(A2(V)), TG(A2(A2(V))), EQ(A1(A2(V)), A1(A2(A2(V)))), EQ(U, A2(A2(A2(V))))],
      A1(A2(V)), 'soft:free')
# Q (= x*(x*u)) decoded, x recovered as u.1.2 (R3/R15 shape) with the v.1 guard dropped
S2 = ([TG(V), TG(U), TG(A1(U)), TG(OP(A2(A1(U)), U)), TG(A1(OP(A2(A1(U)), U))),
       OPEQ(OP(A2(A1(OP(A2(A1(U)), U))), OP(A2(A1(U)), U)), A2(V)),
       EQ(A2(A1(U)), A2(A1(OP(A2(A1(U)), U))))], A2(A1(U)), 'soft:B1l,B11v')

SETS['soft1'] = [S1]
SETS['soft0_1'] = [S0, S1]
SETS['soft1_2'] = [S1, S2]
SETS['soft0_1_2'] = [S0, S1, S2]
SETS['soft_r3r15'] = [S1, G[2], G[14]]

# ---- T-rules: op(z,u) decoded to P, P located at u.2.1 (the reading of (z,u) has its
#      B-root and B.2 nodes free, so u = J (op(z'',z)) (J P (op(P,z)))) -- works even when
#      u.1 = op(z'',z) and u.2.2 = op(P,z) are themselves decoded, which R7/R11 need free.
T1 = ([TG(V), TG(U), TG(A2(U)), EQ(A1(V), A1(A2(U))), TG(A2(V)), TG(A2(A2(V))),
       EQ(A1(A2(V)), A1(A2(A2(V)))), EQ(U, A2(A2(A2(V))))], A1(A2(V)), 'B0@u21')
T2 = ([TG(V), TG(U), TG(A2(U)), EQ(A1(V), A1(A2(U))), TG(A2(V)),
       OPEQ(OP(A1(A2(V)), U), A2(A2(V)))], A1(A2(V)), 'B0@u21,B11l')
SETS['t_a'] = pick([1, 2, 7, 11]) + [T2]
SETS['t_b'] = pick([1, 2, 7, 11, 3, 15]) + [T2]
SETS['t_c'] = pick([1, 2]) + [T2]
SETS['t_d'] = pick([1, 2, 11]) + [T2]
SETS['t_e'] = pick([1, 2, 3, 15]) + [T2]
