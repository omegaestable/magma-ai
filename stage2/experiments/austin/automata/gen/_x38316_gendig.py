# -*- coding: utf-8 -*-
"""Emit `Adig` for rep38316b: every rule's condition contains `a2 v = p1` (gate on p1) or
`a2 v = p9` (gate on p9).  Parse the if-chain, find the conjunct index of that equality and of
its gate, and emit one `Y` branch per rule.  Never count `.2`s by hand (PLAYBOOK §3.3)."""
import re, io
src = io.open('gen/rep38316b/rec38316.lean', encoding='utf-8').read()
body = src[src.index('  if P1 u v'):src.index('termination_by')]
# the `let` definitions, to know each p_k's call and gate
letm = re.findall(r'let (p\d+) := if hs\d+ : (msr [^\n]*?) < msr u v then op ([^\n]*?) else J u v', src)
LET = {k: (g, c) for k, g, c in letm}
branches = re.findall(r'if (P\d+ u v[^\n]*?) then a1 v', body)
print('%d branches' % len(branches))
out = []
for bi, cond in enumerate(branches):
    parts = [p.strip() for p in cond.split(' ∧ ')]
    ie = next(i for i, p in enumerate(parts) if re.fullmatch(r'a2 v = p\d+', p))
    pk = parts[ie].split('= ')[1]
    gate_txt, call = LET[pk]
    ig = next(i for i, p in enumerate(parts) if p == gate_txt + ' < msr u v')
    def path(i, n):
        return 'h' + '.2' * i + ('.1' if i < n - 1 else '')
    out.append('  (fun h => AD1 (%s) (by rw [dif_pos (%s)] at *; exact %s))'
               % (path(ig, len(parts)), path(ig, len(parts)), path(ie, len(parts))))
    print('  rule %2d: %2d conjuncts, gate at %d, eq at %d, %s = op %s' % (bi + 1, len(parts), ig, ie, pk, call))
io.open('gen/_x38316_dig.txt', 'w', encoding='utf-8').write('\n'.join(out))
# also print the distinct calls
print('distinct p_k used for `a2 v = p_k`:', sorted({re.findall(r'a2 v = (p\d+)', c)[0] for c in branches}))
for k in sorted({re.findall(r'a2 v = (p\d+)', c)[0] for c in branches}, key=lambda s: int(s[1:])):
    print('   %s : gate `%s < msr u v`, call `op %s`' % (k, LET[k][0], LET[k][1]))
