"""_x33020_splice.py : build gen/rep33020.lean = repair33020/rec33020.lean with the proof body
gen/_x33020_body.lean inserted before `theorem law` and the `sorry` replaced."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
skel = open(os.path.join(HERE, 'repair33020', 'rec33020.lean'), encoding='utf-8').read()
body = open(os.path.join(HERE, '_x33020_body.lean'), encoding='utf-8').read()
marker = '/-- THE LAW:'
i = skel.index(marker)
head, tail = skel[:i], skel[i:]
old = 'theorem law (x y z : M) : op (y) (op (op (x) (op (z) (op (y) (x)))) (y)) = x := by\n  sorry\n'
assert old in tail, tail[:400]
new = ('theorem law (x y z : M) : op (y) (op (op (x) (op (z) (op (y) (x)))) (y)) = x :=\n'
       '  main x y z (op y x) (op z (op y x)) (op x (op z (op y x)))\n'
       '    (op (op x (op z (op y x))) y) rfl rfl rfl rfl\n')
tail = tail.replace(old, new)
out = head + body + '\n' + tail
with open(os.path.join(HERE, 'rep33020.lean'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote gen/rep33020.lean', len(out.encode('utf-8')), 'bytes')
