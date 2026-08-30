import re, sys

src = open('gen/rec39163.lean', encoding='utf-8').read()
lines = src.split('\n')
out = []
for line in lines:
    if line.startswith('macro '):
        continue
    out.append(line)
t = '\n'.join(out)

# kf <term>(, <term>)* : terms have no commas; ends at newline or ')'
def kf_repl(m):
    args = m.group(1)
    parts = [p.strip() for p in args.split(',')]
    return '; '.join('have := %s' % p for p in parts) + '; omega'

# kf occurrences: either "kf args\n" or "kf args)" (inline by-block)
t = re.sub(r'\bkf ([^\n)]+)(?=\)|\n)', kf_repl, t)

# kb2 h1 h2
t = re.sub(r"\bkb2 ([A-Za-z0-9_']+) ([A-Za-z0-9_']+)",
           r'have := cs \1; have := cs \2; simp only [sz] at *; omega', t)
# kb h
t = re.sub(r"\bkb ([A-Za-z0-9_']+)",
           r'have := cs \1; simp only [sz] at this; omega', t)
# sj [at locs] / ss [at locs]
t = re.sub(r"\bsj at ([A-Za-z0-9_' ⊢]+?)(?=\)|\n|;)", r'simp only [j1, j2] at \1', t)
t = re.sub(r"\bsj\b", 'simp only [j1, j2]', t)
t = re.sub(r"\bss at ([A-Za-z0-9_' ⊢*]+?)(?=\)|\n|;)", r'simp only [sz] at \1', t)
t = re.sub(r"\bss\b", 'simp only [sz]', t)

open('gen/e39163.lean', 'w', encoding='utf-8', newline='\n').write(t)
print('bytes:', len(t.encode('utf-8')))
for bad in ['macro', ' sj', ' ss', 'kb ', 'kb2', 'kf ']:
    for i, l in enumerate(t.split('\n')):
        if re.search(r'\b%s' % bad.strip() + r'\b', l):
            print('LEFTOVER', bad, i + 1, l)
