"""_x38565_build.py -- splice the helper lemmas and the `law` proof into the emitted skeleton."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))

skel = open(os.path.join(HERE, 'rep38565.lean'), encoding='utf-8').read()
helpers = open(os.path.join(HERE, '_x38565_helpers.lean'), encoding='utf-8').read()
lawproof = open(os.path.join(HERE, '_x38565_lawproof.lean'), encoding='utf-8').read()

MARK = '/-- THE LAW:'
i = skel.index(MARK)
head, tail = skel[:i], skel[i:]
assert tail.count('  sorry\n') == 1, tail[:400]
tail = tail.replace('  sorry\n', lawproof)
out = head + helpers + '\n' + tail
dst = os.path.join(HERE, 'x38565.lean')
with open(dst, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote', dst, len(out.encode('utf-8')), 'bytes')
