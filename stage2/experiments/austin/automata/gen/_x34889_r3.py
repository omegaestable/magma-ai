import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import _x34889_wb as wb
import closedform as cf

R = wb.chk_rules()
sub = [r for r in R if r[2] != 'B0l~']
for i, r in enumerate(sub):
    print('R%d %s' % (i + 1, cf.show_rule(r)))
wb.report(sub)
