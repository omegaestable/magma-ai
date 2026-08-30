"""Assemble gen/_x12087_cert.lean = skeleton head + gen/_x12087_proof.lean + law proof + tail.

The law proof body lives in gen/_x12087_law.lean (tactic block, indented 2 spaces).
"""
import sys, os
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
base = open(os.path.join(D, 'gen/rep12087/rec12087.lean'), encoding='utf-8').read()
lines = base.split('\n')
i = next(k for k, l in enumerate(lines) if l.startswith('/-- THE LAW'))
head = '\n'.join(lines[:i])
j = next(k for k, l in enumerate(lines) if l.startswith('theorem lhs'))
tail = '\n'.join(lines[j:])
proof = open(os.path.join(D, 'gen/_x12087_proof.lean'), encoding='utf-8').read()
lawb = open(os.path.join(D, 'gen/_x12087_law.lean'), encoding='utf-8').read()
lawstmt = 'theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by\n'
out = head + '\n' + proof + '\n' + lawstmt + lawb + '\n\n' + tail
# optional: goal override for another row
if len(sys.argv) > 2 and sys.argv[1] == '--rhs':
    newrhs = open(sys.argv[2], encoding='utf-8').read()
    a = out.index('theorem rhs : ')
    b = out.index('\n\n', out.index('simp (config := {decide := true})', a))
    out = out[:a] + newrhs.strip() + out[b:]
dest = os.path.join(D, sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'gen/_x12087_cert.lean')
with open(dest, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote', dest, len(out.encode('utf-8')), 'bytes')
