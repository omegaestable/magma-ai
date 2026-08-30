"""Emit the minimised 10-rule 21864 package into gen/rep21864/ (13-rule set is rep21864_13/).

t8 (13 rules) = GEN[:5] + [R4c,R5c,RA,R6d,R6e,RB,RB2,RD]      validated: run_tests 0, 3x20k deep 0
min (10 rules) = t8 minus Bs (idx2), As|E2a (idx8), As|yEnc2 (idx11)   -- never fire under the
                 full validator's load; validated removal re-checked with the FULL validator.
usage: python gen/_p2_emit21864.py [13]
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import leangen
import _x21864_rules as RR

T8 = RR.GEN[:5] + [RR.R4c, RR.R5c, RR.RA, RR.R6d, RR.R6e, RR.RB, RR.RB2, RR.RD]
DROP = {2, 8}          # 11 rules; {2,8,11} FAILS deep20k seed 78 (that is what RB2 is for)
MIN = [r for i, r in enumerate(T8) if i not in DROP]

if __name__ == '__main__':
    full = len(sys.argv) > 1 and sys.argv[1] == '13'
    rules = T8 if full else MIN
    out = os.path.join(HERE, 'rep21864_13' if full else 'rep21864')
    print('rules', len(rules), [r[2] for r in rules])
    print(leangen.emit(21864, out, rules_override=rules))
    p = os.path.join(out, 'rec21864.lean')
    print('bytes', os.path.getsize(p))
