import re

t = open('gen/f39163.lean', encoding='utf-8').read()

# 1. delete unused decls: msr_lt_of_max_eq, tg_g, op_free, Pre
def del_decl(t, name):
    # match from '^(theorem|def) name ' to the next top-level decl start
    pat = re.compile(r'\n(?:theorem|def) %s\b.*?(?=\n(?:theorem|def|instance|@\[simp\]|attribute|end) )' % re.escape(name), re.S)
    t2, n = pat.subn('', t)
    assert n == 1, (name, n)
    return t2

for name in ['msr_lt_of_max_eq', 'tg_g', 'op_free', 'Pre']:
    t = del_decl(t, name)

# 2. P1..P5 -> abbrev, drop Decidable instances
t = re.sub(r'\ndef (P[1-5]) \(u v : M\) : Prop :=', r'\nabbrev \1 (u v : M) : Prop :=', t)
t = re.sub(r'\ninstance \(u v : M\) : Decidable \(P[1-5] u v\) := by unfold P[1-5]; infer_instance', '', t)

# 3. nf lemma after NF; rewrite Dg, CNF, law's hpp
t = t.replace('''theorem L1 (x y : M) :''',
'''theorem nf {u v : M} (h : ¬(tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2)) : op u v = J u v :=
  Classical.byContradiction fun t => h (NF t)

theorem L1 (x y : M) :''')

t = t.replace('''theorem Dg {c y : M} (hc : a1 c ≠ y) : op y c = J y c := by
  apply Classical.byContradiction; intro h
  obtain ⟨-, hu, -⟩ := NF h
  exact hc hu.symm''',
'''theorem Dg {c y : M} (hc : a1 c ≠ y) : op y c = J y c := nf fun t => hc t.2.1.symm''')

t = t.replace('''  apply Classical.byContradiction; intro h
  obtain ⟨-, hu, -⟩ := NF h
  have s1 := sz_tg y hty''',
'''  apply nf; intro ⟨-, hu, -⟩
  have s1 := sz_tg y hty''')

t = t.replace('''        apply Classical.byContradiction; intro h
        obtain ⟨htp, hu, -⟩ := NF h
        have := cs hu; have := sz_tg _ htp; omega''',
'''        apply nf; intro ⟨htp, hu, -⟩
        have := cs hu; have := sz_tg _ htp; omega''')

# 4. lhs term-mode
t = t.replace('''theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm''',
'''theorem lhs : @EquationLHS M inst := fun x y z => (law x y z).symm''')

open('gen/g39163.lean', 'w', encoding='utf-8', newline='\n').write(t)
print('bytes:', len(t.encode('utf-8')))
