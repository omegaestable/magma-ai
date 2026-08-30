import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import _x34889_wb as wb
import closedform as cf
from _x34889_wb import U, V, A1, A2, OP, JJ, TG, EQ_, OPEQ

R = wb.chk_rules()
R1, R2, R3, R4 = R

X = A1(A2(U))                      # the payload candidate  u.2.1
STRUCT3 = R3[0][:-1]               # R3's conditions minus the deep OPEQ
R3s = (list(STRUCT3) + [OPEQ(OP(U, X), JJ(U, X))], X, 'B0lW')

variants = {
    'A: R1,R2,R3s': [R1, R2, R3s],
    'B: R1,R2,R3,R3s': [R1, R2, R3, R3s],
}
which = sys.argv[1] if len(sys.argv) > 1 else 'A: R1,R2,R3s'
rules = variants[which]
print('==', which)
for i, r in enumerate(rules):
    print('R%d %s' % (i + 1, cf.show_rule(r)))
wb.report(rules)
