import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
old = '''      \u00b7 sorry
      \u00b7 sorry
'''
new = '''      \u00b7 rcases TR (a1 (a2 (a1 z))) z with hh | \u27e8hhr, -, -, -, -\u27e9
        \u00b7 rw [hh] at q
          refine Or.inr (Or.inr \u27e8h1, h2, by rw [q]; rfl, ?_\u27e9)
          rw [q]; simp only [a2_J_eq]; exact hr.symm
        \u00b7 sorry
      \u00b7 rcases TR (a2 (a2 z)) z with hh | \u27e8hhr, -, -, -, -\u27e9
        \u00b7 rw [hh] at q
          refine Or.inr (Or.inr \u27e8h1, h2, by rw [q]; rfl, ?_\u27e9)
          rw [q]; simp only [a2_J_eq]; exact hr.symm
        \u00b7 sorry
'''
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
