import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
s += '''
/-- the top product of the law always fires -/
theorem FIRE {u v : M} (hs : sz u < sz v) (hv : tg v = 2) (hv1 : tg (a1 v) = 2)
    (hA : a2 (a1 v) = op u (a1 (a1 v))) (hC : CK u (a2 v)) : op u v = a1 (a1 v) := by
  obtain \u27e8p1, p2, p3, hp1, hp2, hp3, hop\u27e9 := op_cases u v
  have b0 := s1L hv
  have b1 := sz_a1 (a1 v)
  have g1 : msr u (a1 (a1 v)) < msr u v := gle (Nat.le_refl _) (by omega) (by omega)
  have c1 := sz_a1 (a2 (a1 u))
  have c2 := sz_a2 (a1 u)
  have c3 := sz_a1 u
  have g2 : msr (a1 (a2 (a1 u))) u < msr u v := gle (by omega) (by omega) (by omega)
  have d1 := sz_a2 (a2 u)
  have d2 := sz_a2 u
  have g3 : msr (a2 (a2 u)) u < msr u v := gle (by omega) (by omega) (by omega)
  rw [dif_pos g1] at hp1; subst hp1
  rw [dif_pos g2] at hp2; subst hp2
  rw [dif_pos g3] at hp3; subst hp3
  rw [hop]
  split
  \u00b7 rfl
  \u00b7 split
    \u00b7 rfl
    \u00b7 split
      \u00b7 rfl
      \u00b7 rename_i n1 n2 n3
        exfalso
        rcases hC with \u27e8k1, k2\u27e9 | \u27e8k1, k2, k3, k4\u27e9 | \u27e8k1, k2, k3, k4\u27e9
        \u00b7 exact n1 \u27e8\u27e8hv, hv1, k1, k2\u27e9, g1, hA\u27e9
        \u00b7 exact n2 \u27e8\u27e8hv, hv1, k1, k2, k3\u27e9, g1, g2, hA, k4\u27e9
        \u00b7 exact n3 \u27e8\u27e8hv, hv1, k1, k2, k3\u27e9, g1, g3, hA, k4\u27e9

/-- CLOSURE: `a2 v = op z u` is recognised for every z.  TWO CASES REMAIN OPEN (see NOTES_11081.md). -/
theorem CKlem (z y : M) : CK y (op z y) := by
  rcases TR z y with hf | \u27e8hr, h1, h2, hA, hC\u27e9
  \u00b7 rw [hf]; exact Or.inl \u27e8rfl, rfl\u27e9
  \u00b7 rw [hr]
    rcases TR z (a1 (a1 y)) with hg | \u27e8hgr, -, -, -, -\u27e9
    \u00b7 rw [hg] at hA
      refine Or.inr (Or.inl \u27e8h1, h2, by rw [hA]; rfl, ?_\u27e9)
      rw [hA]; simp only [a1_J_eq]; exact hr.symm
    \u00b7 rcases hC with \u27e8q1, q2\u27e9 | \u27e8-, -, -, q\u27e9 | \u27e8-, -, -, q\u27e9
      \u00b7 refine Or.inr (Or.inr \u27e8h1, h2, q1, ?_\u27e9)
        rw [\u2190 q2]; exact hr.symm
      \u00b7 sorry
      \u00b7 sorry
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
