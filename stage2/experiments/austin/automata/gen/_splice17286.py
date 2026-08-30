"""splice gen/_proof17286.lean into gen/r17286.lean's `theorem law` slot -> gen/p17286.lean"""
import sys, os, io
HERE = os.path.dirname(os.path.abspath(__file__))
sk = io.open(os.path.join(HERE, 'r17286.lean'), encoding='utf-8').read()
pf = io.open(os.path.join(HERE, '_proof17286.lean'), encoding='utf-8').read()
MARK = '\n/-- THE LAW:'
i = sk.index(MARK)
j = sk.index('\ntheorem lhs :')
out = sk[:i] + '\n' + pf.rstrip('\n') + '\n' + sk[j:]
p = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'p17286.lean')
io.open(p, 'w', encoding='utf-8', newline='\n').write(out)
print(p, len(out.encode('utf-8')), 'bytes')
