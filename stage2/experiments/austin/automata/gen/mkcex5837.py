"""Splice a Lean refutation of `theorem law` for the concrete counterexample instance into the 5837 skeleton.
Writes gen/cex5837.lean (the skeleton's definitions verbatim, `law`/`lhs`/`submission` removed, plus the
concrete-instance evaluation decided by simp+decide)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'rec5837.lean'), encoding='utf-8').read()
cut = src.index('/-- THE LAW')
head = src[:cut]
tail = '''
/-- the coincidence instance:  z = x*((w*x)*x),  y = z*(z*((w'*z)*z))  with x = g 0, w = g 1, w' = g 2 -/
def x0 : M := g 0
def z0 : M := J (g 0) (J (J (g 1) (g 0)) (g 0))
def y0 : M := J z0 (J z0 (J (J (g 2) z0) z0))

theorem step1 : op z0 y0 = z0 := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, x0, y0, z0]
theorem step3 : op y0 z0 = J y0 z0 := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, x0, y0, z0]
theorem step4 : op x0 (J y0 z0) = y0 := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, x0, y0, z0]
theorem step5 : op y0 y0 = J y0 y0 := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, x0, y0, z0]

theorem law_fails_here : op y0 (op x0 (op y0 (op (op z0 y0) y0))) ≠ x0 := by
  rw [step1, step1, step3, step4, step5]
  simp [x0, y0, z0]

theorem law_is_false : ¬ ∀ x y z : M, op y (op x (op y (op (op z y) y))) = x :=
  fun h => law_fails_here (h x0 y0 z0)

end submission
'''
open(os.path.join(here, 'cex5837.lean'), 'w', encoding='utf-8', newline='\n').write(head + tail)
print('wrote', os.path.join(here, 'cex5837.lean'), len(head + tail), 'bytes')
