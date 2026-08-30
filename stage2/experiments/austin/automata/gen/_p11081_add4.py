import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
old = '''/-- the fourth chain product is always free.  OPEN (see NOTES_11081.md). -/
theorem Dfree (x y z : M) : op (J x (op y x)) (op z y) = J (J x (op y x)) (op z y) := by
  sorry
'''
new = '''/-- `sz x < sz (J x (op y x))` and, when `op y x` decodes, `sz y < sz x` -/
theorem BS (x y : M) : sz x < sz (J x (op y x)) \u2227 (op y x = J y x \u2228 sz y < sz x) := by
  have := szp (op y x)
  rcases TR y x with hb | \u27e8hbr, hb1, hb2, -, -\u27e9
  \u00b7 exact \u27e8by simp only [szJ]; omega, Or.inl hb\u27e9
  \u00b7 exact \u27e8by simp only [szJ]; omega, Or.inr (KY' (NJ hb1 hb2 hbr))\u27e9

/-- the fourth chain product is always free.  TWO LEAVES OPEN (see NOTES_11081.md). -/
theorem Dfree (x y z : M) : op (J x (op y x)) (op z y) = J (J x (op y x)) (op z y) := by
  apply Classical.byContradiction; intro hne
  rcases TR (J x (op y x)) (op z y) with hf | \u27e8-, h1, h2, hA, hC\u27e9
  \u00b7 exact hne hf
  \u00b7 have m0 := szp x
    have m1 := szp (op y x)
    have m2 := szp (op z y)
    have m3 := s2L h1
    have m4 := sz_a2 (a2 (op z y))
    have m5 : sz (op z y) \u2264 sz y \u2228 sz (op z y) = sz z + sz y + 1 := by
      rcases TR z y with hc | \u27e8hcr, hc1, hc2, -, -\u27e9
      \u00b7 right; rw [hc]; simp only [szJ]
      \u00b7 left; have := (Wsz (NJ hc1 hc2 hcr)).2; rw [hcr]; omega
    obtain \u27e8mA, mB\u27e9 := BS x y
    have m6 : sz (op y x) = sz y + sz x + 1 \u2228 sz y < sz x := by
      rcases mB with h | h
      \u00b7 left; rw [h]; simp only [szJ]
      \u00b7 right; exact h
    rcases hC with \u27e8q1, q2\u27e9 | \u27e8-, -, q3, q\u27e9 | \u27e8-, -, q3, q\u27e9
    \u00b7 have := congrArg sz q2
      rcases TR z y with hc | \u27e8hcr, hc1, hc2, -, -\u27e9
      \u00b7 rw [hc] at this q1; simp only [a2_J_eq, szJ] at this q1
        have := s2L q1
        rcases m6 with h | h <;> omega
      \u00b7 have hw := (Wsz (NJ hc1 hc2 hcr)).2
        rw [hcr] at this m3 m4
        rcases m6 with h | h <;> omega
    \u00b7 sorry
    \u00b7 sorry
'''
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
