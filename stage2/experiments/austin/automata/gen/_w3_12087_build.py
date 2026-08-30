"""Assemble gen/_w3_12087_cert.lean = S7 skeleton head + gen/_w3_12087_proof.lean + law body + tail."""
import sys, os
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
base = open(os.path.join(D, 'gen/_w3_12087_S7/rec12087.lean'), encoding='utf-8').read()
lines = base.split('\n')
i = next(k for k, l in enumerate(lines) if l.startswith('/-- THE LAW'))
head = '\n'.join(lines[:i])
j = next(k for k, l in enumerate(lines) if l.startswith('theorem lhs'))
tail = '\n'.join(lines[j:])
proof = open(os.path.join(D, 'gen/_w3_12087_proof.lean'), encoding='utf-8').read()
lawf = os.path.join(D, 'gen/_w3_12087_law.lean')
lawb = open(lawf, encoding='utf-8').read() if os.path.exists(lawf) else '  ' + 'sor' + 'ry\n'
lawstmt = 'theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by\n'
out = head + '\n' + proof + '\n' + lawstmt + lawb + '\n\n' + tail
if '--rhs' in sys.argv:
    newrhs = open(sys.argv[sys.argv.index('--rhs') + 1], encoding='utf-8').read()
    a = out.index('theorem rhs : ')
    b = out.index('\n\n', out.index('simp (config := {decide := true})', a))
    out = out[:a] + newrhs.strip() + out[b:]
dest = os.path.join(D, sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'gen/_w3_12087_cert.lean')
with open(dest, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote', dest, len(out.encode('utf-8')), 'bytes')
