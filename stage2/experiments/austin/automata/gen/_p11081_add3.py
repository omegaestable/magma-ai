import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
s += '''
/-- the fourth chain product is always free.  OPEN (see NOTES_11081.md). -/
theorem Dfree (x y z : M) : op (J x (op y x)) (op z y) = J (J x (op y x)) (op z y) := by
  sorry

/-- the key is strictly smaller than the encoding: what every msr gate at the top needs -/
theorem SZV (x y z : M) : sz y < sz (J (J x (op y x)) (op z y)) := by
  have s1 := szp (op z y)
  have s2 := szp x
  rcases TR y x with hb | \u27e8hbr, hb1, hb2, -, -\u27e9
  \u00b7 rw [hb]; simp only [szJ]; omega
  \u00b7 have := KY' (NJ hb1 hb2 hbr)
    have := szp (op y x)
    simp only [szJ]
    omega
'''
io.open(p, 'w', encoding='utf-8').write(s)
# and the law
q = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_law.txt'
io.open(q, 'w', encoding='utf-8').write('''theorem law (x y z : M) : op (y) (op (op (x) (op (y) (x))) (op (z) (y))) = x := by
  rw [Bfree x y, Dfree x y z]
  exact FIRE (SZV x y z) rfl rfl rfl (CKlem z y)
''')
print('ok')
