"""The repaired rule set for 40057 (rules for the DUAL L-form law x = y*(y*(x*((z*x)*y)))): R1-R4 from the
generator plus R5/R6, which read the payload x through u when the third product E = op x P1 is itself decoded.

Reading (u, v): v = J u E, u = J P0 (J P1 u3), P1 = J x _, with  E = op x P1,  P1 = op P0 u,  P0 = op z x
(R5: P0 = J z x free;  R6: P0 = op (a1 x) x decoded).  Result x = u.2.1.1.
"""
import sys
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
from chk40057 import rules as rules4

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
P0 = A1(U); P1 = A1(A2(U)); X = A1(A1(A2(U)))
common = [('TG', V), ('EQ', U, A1(V)), ('TG', U), ('TG', A2(U)), ('TG', P1),
          ('OPEQ', OP(X, P1), A2(V)),        # E = op x P1
          ('OPEQ', OP(P0, U), P1)]           # P1 = op P0 u
R5 = (common + [('TG', P0), ('EQ', A2(P0), X)], X, 'L2free')                 # P0 = J z x
R6 = (common + [('TG', X), ('OPEQ', OP(A1(X), X), P0)], X, 'L2dec')          # P0 = op (a1 x) x
rules6 = list(rules4) + [R5, R6]
