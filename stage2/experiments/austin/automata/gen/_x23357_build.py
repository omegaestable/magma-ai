"""Splice gen/_x23357_body.lean into the 23357 skeleton, producing gen/_x23357_cert.lean."""
import sys, os
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
sk = open(D + 'rep23357b/rec23357.lean', encoding='utf-8').read()
body = open(D + '_x23357_body.lean', encoding='utf-8').read()
i = sk.index('/-- THE LAW:')
j = sk.index('theorem lhs :')
out = sk[:i] + body.rstrip() + '\n\n\n' + sk[j:]
with open(D + '_x23357_cert.lean', 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('bytes', len(out.encode('utf-8')), ' sorries', out.count('sorry'))
