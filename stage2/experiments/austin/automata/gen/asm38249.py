"""asm38249.py : splice gen/law38249_proof.lean (the proof section, ending with `theorem law`) into the
repaired skeleton gen/repair38249/rec38249.lean (everything before `/-- THE LAW` is kept verbatim, then
`theorem lhs` onward), writing gen/rec38249.lean."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'repair38249', 'rec38249.lean'), encoding='utf-8').read()
i = src.index('/-- THE LAW')
j = src.index('theorem lhs')
proof = open(os.path.join(HERE, 'law38249_proof.lean'), encoding='utf-8').read()
out = src[:i] + proof + '\n' + src[j:]
dst = os.path.join(HERE, 'rec38249.lean')
with open(dst, 'w', encoding='utf-8', newline='\n') as f: f.write(out)
print(dst, len(out.encode('utf-8')), 'bytes; sorry' if 'sorry' in out else 'bytes; no sorry')
