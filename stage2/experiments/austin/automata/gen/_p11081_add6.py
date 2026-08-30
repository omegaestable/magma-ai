import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
old = '''    \u00b7 sorry
    \u00b7 sorry
'''
new = '''    \u00b7 simp only [a1_J_eq, a2_J_eq] at q q3
      rcases TR (a1 (a2 x)) (J x (op y x)) with hg | \u27e8hgr, -, -, -, -\u27e9
      \u00b7 rw [hg] at q
        have := congrArg sz q
        simp only [szJ] at this
        have := szp (a1 (a2 x))
        rcases m6 with h | h <;> omega
      \u00b7 sorry
    \u00b7 simp only [a1_J_eq, a2_J_eq] at q q3
      rcases TR (a2 (op y x)) (J x (op y x)) with hg | \u27e8hgr, -, -, -, -\u27e9
      \u00b7 rw [hg] at q
        have := congrArg sz q
        simp only [szJ] at this
        have := szp (a2 (op y x))
        rcases m6 with h | h <;> omega
      \u00b7 sorry
'''
assert s.count(old) == 1
s = s.replace(old, new)
old2 = '''    have m5 : sz (op z y) \u2264 sz y \u2228 sz (op z y) = sz z + sz y + 1 := by
      rcases TR z y with hc | \u27e8hcr, hc1, hc2, -, -\u27e9
      \u00b7 right; rw [hc]; simp only [szJ]
      \u00b7 left; have := (Wsz (NJ hc1 hc2 hcr)).2; rw [hcr]; omega'''
new2 = '''    have m7 : sz (a2 (op z y)) \u2264 sz y := by
      rcases TR z y with hc | \u27e8hcr, hc1, hc2, -, -\u27e9
      \u00b7 rw [hc]; simp only [a2_J_eq]
      \u00b7 have := (Wsz (NJ hc1 hc2 hcr)).2
        have := sz_a2 (op z y)
        rw [hcr] at this \u22a2
        omega'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
