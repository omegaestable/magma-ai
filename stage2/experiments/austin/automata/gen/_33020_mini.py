"""gen/_33020_mini.py <in.lean> <out.lean>
Local, law-33020-specific squeeze pass: tightens mid-line spacing that the shared squeeze.py's
pattern list does not cover ( ' : ' , ') (' , ' => ' , ' <;> ' , trailing space before ':=' ).
Deliberately never touches leading indentation (that halving bug is what broke _sq33020_r.lean).
"""
import sys, re
def mini(s):
    out = []
    for line in s.split('\n'):
        m = re.match(r'^( *)(.*)$', line)
        ind, rest = m.group(1), m.group(2)
        rest = rest.replace(' :=', ':=')
        rest = rest.replace(' : ', ':')
        rest = rest.replace(' => ', '=>')
        rest = rest.replace(' <;> ', '<;>')
        rest = rest.replace('; ', ';')
        if rest.startswith('@[simp] theorem '):
            rest = '@[simp] def ' + rest[len('@[simp] theorem '):]
        out.append(ind + rest)
    return '\n'.join(out)
if __name__ == '__main__':
    s = open(sys.argv[1], encoding='utf-8').read()
    t = mini(s)
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(t)
    print(len(s.encode()), '->', len(t.encode()))
