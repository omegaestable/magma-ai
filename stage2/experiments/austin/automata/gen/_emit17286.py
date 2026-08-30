"""_emit17286.py -- emit the REPAIRED skeleton for law 17286 (7 extracted rules + R8b, the DD cell)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
BASE = cf.Extractor(law).rules(exist=False)
U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e); A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b); JE = lambda a, b: ('J', a, b)
P_ = A2(A2(V)); X_ = JE(A1(P_), P_)
R8b = ([('TG', V), ('TG', A2(V)), ('EQ', A1(V), A1(A2(V))), ('TG', P_),
        ('OPEQ', OP(U, A1(P_)), A2(P_)), ('OPEQ', OP(X_, A1(V)), P_)], X_, 'DDb')
RULES = [r for r in BASE if r[2] != 'Bs'] + [R8b]   # R4 [Bs] is unsatisfiable (v = a2 v)
print('rules:', len(RULES))
for i, r in enumerate(RULES, 1):
    print(' R%d %s' % (i, cf.show_rule(r)))
out = os.path.join(HERE, 'x17286')
print(json.dumps(leangen.emit(EQ, out, rules_override=RULES)))
