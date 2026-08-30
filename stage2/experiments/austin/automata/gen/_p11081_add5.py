import io
p = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_p11081_body.lean'
s = io.open(p, encoding='utf-8').read()
old = '''      \u00b7 have hw := (Wsz (NJ hc1 hc2 hcr)).2
        rw [hcr] at this m3 m4
        rcases m6 with h | h <;> omega'''
new = '''      \u00b7 have hw := (Wsz (NJ hc1 hc2 hcr)).2
        rw [hcr] at this m3 m4
        simp only [szJ] at this
        rcases m6 with h | h <;> omega'''
assert s.count(old) == 1
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
