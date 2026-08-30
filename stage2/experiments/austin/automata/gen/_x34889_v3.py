import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import _x34889_wb as wb
import closedform as cf
from _x34889_wb import U, V, A1, A2, OP, JJ, TG, EQ_, OPEQ

R = wb.chk_rules()
R1, R2, R3, R4 = R

X = A1(A2(U))
STRUCT3 = list(R3[0][:-1])
R3s = (STRUCT3 + [OPEQ(OP(U, X), JJ(U, X))], X, 'B0lW')
BLOCK = (STRUCT3 + [EQ_(A1(V), A2(V))], JJ(U, V), 'blk')
R4b = (STRUCT3, X, 'B0lN')

variants = {
    'F': [R1, R2, BLOCK, R4b],
    'G': [R1, R2, BLOCK, R3s, R4b],
    'H': [R1, R2, BLOCK, R3, R3s, R4b],
}
which = sys.argv[1] if len(sys.argv) > 1 else 'F'
rules = variants[which]
print('== variant', which)
for i, r in enumerate(rules):
    print('R%d %s' % (i + 1, cf.show_rule(r)))
wb.report(rules)
