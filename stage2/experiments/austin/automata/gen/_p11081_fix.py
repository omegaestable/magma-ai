import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
nj = '''
/-- a decoded result is never the free product -/
theorem NJ {u v : M} (h1 : tg v = 2) (h2 : tg (a1 v) = 2) (h : op u v = a1 (a1 v)) :
    op u v \u2260 J u v := by
  intro c
  rw [c] at h
  have := congrArg sz h
  have e1 := sz_tg v h1
  have e2 := sz_tg (a1 v) h2
  have e3 := szp (a2 v)
  have e4 := szp (a2 (a1 v))
  have e5 := szp u
  simp only [szJ] at this
  omega

'''
mk = '/-- if `op y x` decodes then `sz y < sz x` -/'
assert mk in s
s = s.replace(mk, nj + mk, 1)
old = '''          rcases TR y (a1 (a1 x)) with hf3 | \u27e8-, -, -, -, -\u27e9
          \u00b7 rw [hf3] at hA; have := congrArg sz hA; simp only [szJ] at this; omega
          \u00b7 have hne3 : op y (a1 (a1 x)) \u2260 J y (a1 (a1 x)) := by
              intro c; rw [c] at hA; have := congrArg sz hA; simp only [szJ] at this; omega
            have := ih (a1 (a1 x)) y (by omega) hne3
            omega'''
new = '''          rcases TR y (a1 (a1 x)) with hf3 | \u27e8hr3, t1, t2, -, -\u27e9
          \u00b7 rw [hf3] at hA; have := congrArg sz hA; simp only [szJ] at this; omega
          \u00b7 have := ih (a1 (a1 x)) y (by omega) (NJ t1 t2 hr3)
            omega'''
assert s.count(old) == 2, s.count(old)
s = s.replace(old, new)
i = s.index('/-- the second chain product is always free -/')
s = s[:i] + '''/-- the second chain product is always free -/
theorem Bfree (x y : M) : op x (op y x) = J x (op y x) := by
  apply Classical.byContradiction; intro hne
  rcases TR x (op y x) with hf | \u27e8-, h1, h2, hA, hC\u27e9
  \u00b7 exact hne hf
  \u00b7 rcases TR y x with hb | \u27e8hbr, hb1, hb2, -, -\u27e9
    \u00b7 rw [hb] at h1 h2 hA hC
      rcases hC with \u27e8q1, q2\u27e9 | \u27e8-, -, -, q\u27e9 | \u27e8-, -, -, q\u27e9
      \u00b7 simp only [a2_J_eq] at q1 q2
        have := s2L q1; rw [\u2190 q2] at this; omega
      \u00b7 simp only [a2_J_eq] at q; exact NF q
      \u00b7 simp only [a2_J_eq] at q; exact NF q
    \u00b7 rw [hbr] at h1 h2 hA hC
      have f1 := sz_tg x hb1
      have f2 := sz_tg (a1 x) hb2
      have f3 := szp (a2 x)
      have f4 := szp (a2 (a1 x))
      have f5 := s2L h1
      rcases hC with \u27e8q1, q2\u27e9 | \u27e8-, -, -, q\u27e9 | \u27e8-, -, -, q\u27e9
      \u00b7 have := congrArg sz q2
        have := sz_a2 (a2 (a1 (a1 x)))
        omega
      \u00b7 rcases TR (a1 (a2 (a1 x))) x with hg | \u27e8hgr, -, -, -, -\u27e9
        \u00b7 rw [hg] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a1 (a2 (a1 x))); omega
        \u00b7 rw [hgr] at q; have := congrArg sz q; omega
      \u00b7 rcases TR (a2 (a2 x)) x with hg | \u27e8hgr, -, -, -, -\u27e9
        \u00b7 rw [hg] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a2 (a2 x)); omega
        \u00b7 rw [hgr] at q; have := congrArg sz q; omega
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('ok', len(s))
