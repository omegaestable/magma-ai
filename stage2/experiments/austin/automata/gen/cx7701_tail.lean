
/-! Counterexample to `law` for the generated 7701 skeleton (a level-2 decoder hole).
    x encodes g1 by z = g0, so z◇x decodes to g1 and q2 = x◇(z◇x) = J x g1 carries a DECODED right child;
    y then encodes g3 by q2 (R1 shape), so (q2◇y) = g3, y◇g3 is free, and at the top neither R1 nor R3
    can fire (both need the right child of a1 y to be a J-product `J z x`), so the result is J y (J y g3) ≠ x. -/
def cxZ : M := g 0
def cxX : M := J (g 0) (J (J (g 1) (J (g 2) (g 1))) (g 0))
def cxQ2 : M := J cxX (g 1)
def cxY : M := J cxQ2 (J (J (g 3) (J (g 4) (g 3))) cxQ2)

theorem cx_steps :
    op cxZ cxX = g 1 ∧
    op cxX (g 1) = J cxX (g 1) ∧
    op cxQ2 cxY = g 3 ∧
    op cxY (g 3) = J cxY (g 3) ∧
    op cxY (J cxY (g 3)) = J cxY (J cxY (g 3)) := by
  simp (config := {decide := true}) [cxZ, cxX, cxQ2, cxY, op.eq_1, sz, msr, P1, P2, P3]

theorem cx_law_fails : op cxY (op cxY (op (op cxX (op cxZ cxX)) cxY)) ≠ cxX := by
  simp (config := {decide := true}) [cxZ, cxX, cxQ2, cxY, op.eq_1, sz, msr, P1, P2, P3]

/-- the same hole with a single generator -/
def c0X : M := J (g 0) (J (J (g 0) (J (g 0) (g 0))) (g 0))
def c0Q2 : M := J c0X (g 0)
def c0Y : M := J c0Q2 (J (J (g 0) (J (g 0) (g 0))) c0Q2)

theorem cx_law_fails_g0 : op c0Y (op c0Y (op (op c0X (op (g 0) c0X)) c0Y)) ≠ c0X := by
  simp (config := {decide := true}) [c0X, c0Q2, c0Y, op.eq_1, sz, msr, P1, P2, P3]

end submission
