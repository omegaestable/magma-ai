# -*- coding: utf-8 -*-
"""Emit the full per-rule digest TR for rep38316c: one Y branch per rule, each exporting P_k plus
every op-equality of that rule's condition with the p_k dites resolved by dif_pos."""
import re, io
NL = chr(10)
src = io.open('gen/rep38316c/rec38316.lean', encoding='utf-8').read()
LET = {k: (g, c) for k, g, c in re.findall(
    r'let (p\d+) := if hs\d+ : (msr [^' + NL + r']*?) < msr u v then op ([^' + NL + r']*?) else J u v', src)}
body = src[src.index('  if P1 u v'):src.index('termination_by')]
branches = re.findall(r'if (P\d+ u v[^' + NL + r']*?) then a1 v', body)
def path(i, n): return 'h' + '.2'*i + ('.1' if i < n-1 else '')
stmts, proofs = [], []
for bi, cond in enumerate(branches):
    parts = [p.strip() for p in cond.split(' ∧ ')]
    n = len(parts)
    eqs = [(i, p) for i, p in enumerate(parts) if re.search(r'= p\d+$', p)]
    conj, pf = ['P%d u v' % (bi+1)], ['h.1']
    for ie, p in eqs:
        lhs, pk = p.rsplit(' = ', 1)
        ig = parts.index(LET[pk][0] + ' < msr u v')
        conj.append('%s = op %s' % (lhs, LET[pk][1]))
        pf.append('(by have e := %s; rw [dif_pos (%s)] at e; exact e)' % (path(ie, n), path(ig, n)))
    stmts.append('(' + ' ∧ '.join(conj) + ')')
    proofs.append('⟨' + ', '.join(pf) + '⟩')
def wrap(k, n, inner):
    t = inner if k == n - 1 else 'Or.inl (%s)' % inner
    for _ in range(k): t = 'Or.inr (%s)' % t
    return t
term = '(fun hh => absurd rfl hh)'
for k in reversed(range(len(branches))):
    term = 'Y' + NL + '    (fun h => ' + wrap(k, len(branches), proofs[k]) + ')' + NL + '    (' + term + ')'
out = ('theorem TR {u v : M} (h : op u v ≠ J u v) :' + NL + '    '
       + (' ∨' + NL + '    ').join(stmts) + ' := by' + NL
       + '  rw [op.eq_1] at h' + NL + '  revert h' + NL + '  exact ' + term + NL)
io.open('gen/_x38316_tr.txt', 'w', encoding='utf-8', newline=NL).write(out)
print('TR bytes', len(out.encode('utf-8')))
