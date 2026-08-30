"""Splice gen/_w3_23357_body.lean into the 5-rule 23357 skeleton -> gen/_w3_23357_cert.lean."""
import sys
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
sk = open(D + 'rep23357c/rec23357.lean', encoding='utf-8').read()
body = open(D + '_w3_23357_body.lean', encoding='utf-8').read()
i = sk.index('/-- THE LAW:')
j = sk.index('theorem lhs :')
out = sk[:i] + body.rstrip() + '\n\n' + sk[i:j] + sk[j:]
with open(D + '_w3_23357_cert.lean', 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('bytes', len(out.encode('utf-8')), ' sorries', out.count('sorry'))
