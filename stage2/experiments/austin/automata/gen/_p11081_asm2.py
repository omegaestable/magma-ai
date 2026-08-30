import io, sys
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
base = io.open(D + 'rec11081w.lean', encoding='utf-8').read()
proof = io.open(D + '_p11081_body.lean', encoding='utf-8').read()
lawtxt = io.open(D + '_p11081_law.txt', encoding='utf-8').read()
i = base.index('/-- THE LAW')
head = base[:i] + proof + '\n' + base[i:]
old = '''theorem law (x y z : M) : op (y) (op (op (x) (op (y) (x))) (op (z) (y))) = x := by
  sorry
'''
assert old in head
head = head.replace(old, lawtxt)
io.open(D + (sys.argv[1] if len(sys.argv) > 1 else 'rec11081p.lean'), 'w', encoding='utf-8').write(head)
print('bytes', len(head.encode('utf-8')))
