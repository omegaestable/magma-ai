"""Assemble gen/_x40037_p.lean = skeleton(rep40037b) + gen/_x40037_body.lean + gen/_x40037_law.lean."""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
SK = os.path.join(HERE, 'gen', 'rep40037b', 'rec40037.lean')
BODY = os.path.join(HERE, 'gen', '_x40037_body.lean')
LAW = os.path.join(HERE, 'gen', '_x40037_law.lean')
OUT = os.path.join(HERE, 'gen', '_x40037_p.lean')

sk = open(SK, encoding='utf-8').read()
body = open(BODY, encoding='utf-8').read()
law = open(LAW, encoding='utf-8').read() if os.path.exists(LAW) else '  sorry\n'
i = sk.index('/-- THE LAW:')
j = sk.index('theorem lhs :')
head = sk[:i]
tail = sk[j:]
lawhdr = 'theorem law (x y z : M) : op (z) (op (x) (op (z) (op (op (y) (x)) (y)))) = x := by\n'
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write(head)
    f.write(body)
    f.write('\n')
    f.write(lawhdr)
    f.write(law)
    f.write('\n\n')
    f.write(tail)
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
