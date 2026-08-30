import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  | E : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2
  | .E _ _ => 3
def a1 : M → M
  | .J x _ => x
  | .E x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | .E _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .J a b => sz a + sz b + 1
  | .E a b => sz a + sz b + 1

@[simp] theorem tJ (a b : M) : tg (J a b) = 2 := rfl
@[simp] theorem tE (a b : M) : tg (E a b) = 3 := rfl
@[simp] theorem q1J (a b : M) : a1 (J a b) = a := rfl
@[simp] theorem q2J (a b : M) : a2 (J a b) = b := rfl
@[simp] theorem q1E (a b : M) : a1 (E a b) = a := rfl
@[simp] theorem q2E (a b : M) : a2 (E a b) = b := rfl
@[simp] theorem sJ (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
@[simp] theorem sE (a b : M) : sz (E a b) = sz a + sz b + 1 := rfl

theorem szp (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem s1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem s2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem st {t : M} (h : tg t ≠ 1) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  cases t <;> simp_all [tg, a1, a2, sz]
theorem s1l {t : M} (h : tg t ≠ 1) : sz (a1 t) < sz t := by
  have := st h; have := szp (a2 t); omega
theorem s2l {t : M} (h : tg t ≠ 1) : sz (a2 t) < sz t := by
  have := st h; have := szp (a1 t); omega

def W (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem wlt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : W a b < W u v := by
  unfold W
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) :=
    Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  have : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  omega
theorem gv {a b u v : M} (ha : sz a < sz v) (hb : sz b < sz v) : W a b < W u v :=
  wlt (Nat.lt_of_lt_of_le (Nat.max_lt.mpr ⟨ha, hb⟩) (Nat.le_max_right (sz u) (sz v)))
theorem gu {a b u v : M} (ha : sz a < sz u) (hb : sz b < sz u) : W a b < W u v :=
  wlt (Nat.lt_of_lt_of_le (Nat.max_lt.mpr ⟨ha, hb⟩) (Nat.le_max_left (sz u) (sz v)))
theorem gm {a b u v : M} (ha : sz a ≤ sz u) (hb : sz b < sz v) : W a b < W u v := by
  rcases Nat.lt_or_ge (max (sz a) (sz b)) (max (sz u) (sz v)) with h | h
  · exact wlt h
  · have he : max (sz a) (sz b) = max (sz u) (sz v) :=
      Nat.le_antisymm (Nat.max_le.mpr ⟨Nat.le_trans ha (Nat.le_max_left _ _),
        Nat.le_trans (Nat.le_of_lt hb) (Nat.le_max_right _ _)⟩) h
    unfold W; rw [he]; omega

/-- the two fixed-depth readings of the payload out of a tagged `v` -/
def K1 (v : M) : M := a1 (a2 v)
def K2 (v : M) : M := a1 (a1 (a1 (a2 (a1 v))))
/-- the two readings of the payload at the (N2,N3) pair -/
def L1 (u : M) : M := a2 (a1 u)
def L2 (u : M) : M := a1 (a1 (a1 (a2 u)))

def op (u v : M) : M :=
  let r1 := if h : W u (K1 v) < W u v then op u (K1 v) else J u v
  let r2 := if h : W (K1 v) (a2 (a1 v)) < W u v then op (K1 v) (a2 (a1 v)) else J u v
  let r3 := if h : W u (K2 v) < W u v then op u (K2 v) else J u v
  let r4 := if h : W (K2 v) (a2 (a1 v)) < W u v then op (K2 v) (a2 (a1 v)) else J u v
  let r5 := if h : W (L1 u) (a2 u) < W u v then op (L1 u) (a2 u) else J u v
  let r6 := if h : W (L2 u) (a2 u) < W u v then op (L2 u) (a2 u) else J u v
  if tg v = 3 ∧ tg (a2 v) ≠ 1 ∧ r1 = a1 (a1 v) ∧ r2 = a2 v then K1 v
  else if tg v = 3 ∧ tg (a2 (a1 v)) = 3 ∧ r3 = a1 (a1 v) ∧ r4 = a2 v then K2 v
  else if tg u ≠ 1 ∧ tg (a1 u) ≠ 1 ∧ r5 = v then E u v
  else if tg u ≠ 1 ∧ tg (a2 u) = 3 ∧ r6 = v then E u v
  else J u v
termination_by W u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption

def inst : Magma M := { op := op }


theorem oc (u v : M) : ∃ r1 r2 r3 r4 r5 r6 : M,
    r1 = (if h : W u (K1 v) < W u v then op u (K1 v) else J u v) ∧
    r2 = (if h : W (K1 v) (a2 (a1 v)) < W u v then op (K1 v) (a2 (a1 v)) else J u v) ∧
    r3 = (if h : W u (K2 v) < W u v then op u (K2 v) else J u v) ∧
    r4 = (if h : W (K2 v) (a2 (a1 v)) < W u v then op (K2 v) (a2 (a1 v)) else J u v) ∧
    r5 = (if h : W (L1 u) (a2 u) < W u v then op (L1 u) (a2 u) else J u v) ∧
    r6 = (if h : W (L2 u) (a2 u) < W u v then op (L2 u) (a2 u) else J u v) ∧
    op u v = (
  if tg v = 3 ∧ tg (a2 v) ≠ 1 ∧ r1 = a1 (a1 v) ∧ r2 = a2 v then K1 v
  else if tg v = 3 ∧ tg (a2 (a1 v)) = 3 ∧ r3 = a1 (a1 v) ∧ r4 = a2 v then K2 v
  else if tg u ≠ 1 ∧ tg (a1 u) ≠ 1 ∧ r5 = v then E u v
  else if tg u ≠ 1 ∧ tg (a2 u) = 3 ∧ r6 = v then E u v
  else J u v) :=
  ⟨_, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the tag fires on the (N2,N3) pair when N1 and N2 are free: every guard is `rfl` -/
theorem tag (x y z : M) (h3 : op x z = J x z) :
    op (J (J y x) z) (J x z) = E (J (J y x) z) (J x z) := by
  obtain ⟨r1, r2, r3, r4, r5, r6, -, -, -, -, hr5, -, hop⟩ := oc (J (J y x) z) (J x z)
  have g5 : W (L1 (J (J y x) z)) (a2 (J (J y x) z)) < W (J (J y x) z) (J x z) := by
    refine gu ?_ ?_ <;> simp only [L1, q1J, q2J, sJ] <;> have := szp x <;> have := szp y <;>
      have := szp z <;> omega
  have h5 : r5 = J x z := by rw [hr5, dif_pos g5]; simpa only [L1, q1J, q2J] using h3
  rw [hop, if_neg (by simp), if_neg (by simp), if_pos ⟨by simp, by simp, h5⟩]

/-- the root decodes the tag: both certificates are `rfl` -/
theorem root (x y z : M) (h1 : op y x = J y x) (h3 : op x z = J x z) :
    op y (E (J (J y x) z) (J x z)) = x := by
  obtain ⟨r1, r2, r3, r4, r5, r6, hr1, hr2, -, -, -, -, hop⟩ := oc y (E (J (J y x) z) (J x z))
  have g1 : W y (K1 (E (J (J y x) z) (J x z))) < W y (E (J (J y x) z) (J x z)) := by
    refine gm (Nat.le_refl _) ?_ <;> simp only [K1, q1E, q2E, q1J, q2J, sE, sJ] <;>
      have := szp y <;> have := szp z <;> omega
  have g2 : W (K1 (E (J (J y x) z) (J x z))) (a2 (a1 (E (J (J y x) z) (J x z))))
      < W y (E (J (J y x) z) (J x z)) := by
    refine gv ?_ ?_ <;> simp only [K1, q1E, q2E, q1J, q2J, sE, sJ] <;>
      have := szp x <;> have := szp y <;> have := szp z <;> omega
  have e1 : r1 = J y x := by rw [hr1, dif_pos g1]; simpa only [K1, q1E, q2E, q1J] using h1
  have e2 : r2 = J x z := by rw [hr2, dif_pos g2]; simpa only [K1, q1E, q2E, q1J, q2J] using h3
  rw [hop, if_pos ⟨by simp, by simp, by simpa only [q1E, q1J] using e1, by simpa only [q2E] using e2⟩]
  simp only [K1, q2E, q1J]


/-- every branch of `op` returns the free product, the tag, or a proper subterm of `v` -/
theorem SZ (u v : M) : op u v = J u v ∨ op u v = E u v ∨ sz (op u v) < sz v := by
  obtain ⟨r1, r2, r3, r4, r5, r6, -, -, -, -, -, -, hop⟩ := oc u v
  rw [hop]
  split
  · rename_i h
    refine Or.inr (Or.inr ?_)
    have hv : tg v ≠ 1 := by rw [h.1]; decide
    have := s1 (a2 v); have := s2l hv
    simp only [K1]; omega
  · split
    · rename_i h1 h
      refine Or.inr (Or.inr ?_)
      have hv : tg v ≠ 1 := by rw [h.1]; decide
      have := s1 (a1 (a1 (a2 (a1 v)))); have := s1 (a1 (a2 (a1 v))); have := s1 (a2 (a1 v))
      have := s2 (a1 v); have := s1l hv
      simp only [K2]; omega
    · split
      · exact Or.inr (Or.inl rfl)
      · split
        · exact Or.inr (Or.inl rfl)
        · exact Or.inl rfl

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (op (g 0) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2, W, K1, K2, L1, L2]

/-- THE LAW: x = y * (((y * x) * z) * (x * z)) -/
theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
