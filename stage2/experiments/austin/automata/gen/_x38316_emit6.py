import sys
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import leangen
G = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
ns = {}; exec(open(G + '_x38316_rules_cand6.py', encoding='utf-8').read(), ns)
print(leangen.emit(38316, G + 'rep38316c', rules_override=ns['rules']))
