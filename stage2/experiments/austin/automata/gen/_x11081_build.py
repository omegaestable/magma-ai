"""Splice gen/_x11081_proof.lean (helper lemmas + `theorem law`) into the 5-rule 11081 skeleton."""
import sys, re

BASE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/'
skel = open(BASE + 'gen/rep11081/rec11081.lean', encoding='utf-8').read()
proof = open(BASE + 'gen/_x11081_proof.lean', encoding='utf-8').read()

i = skel.index('/-- THE LAW')
j = skel.index('theorem lhs')
out = skel[:i] + proof.rstrip() + '\n\n\n' + skel[j:]
dst = sys.argv[1] if len(sys.argv) > 1 else BASE + 'gen/rec11081x.lean'
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print(dst, len(out.encode('utf-8')), 'bytes')
