"""Swap the `theorem rhs` block of gen/_x5837_a.lean for another goal's block."""
import sys, io
base = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
goal = sys.argv[1]
src = io.open(base + '_x5837_a.lean', encoding='utf-8').read()
new = io.open(base + '_x5837_rhs_%s.txt' % goal, encoding='utf-8').read().rstrip('\n')
lines = src.split('\n')
i = next(k for k, l in enumerate(lines) if l.startswith('theorem rhs :'))
j = i
while j < len(lines) and lines[j].strip() != '':
    j += 1
out = '\n'.join(lines[:i]) + '\n' + new + '\n' + '\n'.join(lines[j:])
io.open(base + '_x5837_b.lean', 'w', encoding='utf-8', newline='\n').write(out)
print('wrote _x5837_b.lean', len(out.encode('utf-8')), 'replaced lines', i, j)
