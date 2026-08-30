import io, sys
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
base = io.open(D + 'rec11081w.lean', encoding='utf-8').read()
proof = io.open(D + '_p11081_body.lean', encoding='utf-8').read()
i = base.index('/-- THE LAW')
out = base[:i] + proof + '\n' + base[i:]
io.open(D + (sys.argv[1] if len(sys.argv) > 1 else 'rec11081p.lean'), 'w', encoding='utf-8').write(out)
print('bytes', len(out.encode('utf-8')))
