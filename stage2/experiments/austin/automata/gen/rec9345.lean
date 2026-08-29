import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2
def a1 : M → M
  | .J x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1
theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl

/-- G u v : v = J p (J q (J u u)) — v has the shape of the law's encoding with y = u -/
def G (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ a1 (a2 (a2 v)) = u ∧ a2 (a2 (a2 v)) = u
instance (u v : M) : Decidable (G u v) := by unfold G; infer_instance

theorem G_ex {u v : M} (h : G u v) : ∃ p q, v = J p (J q (J u u)) := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a2_J_eq] at h2 h3 h4 h5
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
  simp only [a2_J_eq] at h3 h4 h5
  obtain ⟨d0, d1, rfl⟩ := tg_J _ h3
  simp only [a1_J_eq, a2_J_eq] at h4 h5
  subst h4; subst h5
  exact ⟨b0, c0, rfl⟩

theorem G_sz {u v : M} (h : G u v) : sz v = sz (a1 v) + sz (a1 (a2 v)) + sz u + sz u + 3 := by
  obtain ⟨p, q, rfl⟩ := G_ex h; simp [sz]; omega

/-- E u : u = J _ (J _ (J x x)) — u is itself an encoding; its decoded x is a1 (a2 (a2 u)) -/
def E (u : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a1 (a2 (a2 u)) = a2 (a2 (a2 u))
instance (u : M) : Decidable (E u) := by unfold E; infer_instance

/-- op u v = x when v = (x ◇ u) ◇ (z ◇ (u ◇ u)): rule 1 reads x off a free product x ◇ u = J x u;
    rule 2 handles a non-free x ◇ u, where x is forced to be a1 (a2 (a2 u)) and is checked by recomputing. -/
def op (u v : M) : M :=
  if hg : G u v then
    if tg (a1 v) = 2 ∧ a2 (a1 v) = u then a1 (a1 v)
    else if E u ∧ op (a1 (a2 (a2 u))) u = a1 v then a1 (a2 (a2 u))
    else J u v
  else J u v
termination_by sz u + sz v
decreasing_by
  all_goals (have := G_sz hg; have := sz_a1 (a2 (a2 u)); have := sz_a2 (a2 u); have := sz_a2 u; omega)

def inst : Magma M := { op := op }

theorem op_nG {u v : M} (h : ¬ G u v) : op u v = J u v := by rw [op.eq_1, dif_neg h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
  simp (disch := decide) [op_nG]

/-- one-unfold characterisation -/
theorem TR (u v : M) : op u v = J u v ∨ (G u v ∧
    ((tg (a1 v) = 2 ∧ a2 (a1 v) = u ∧ op u v = a1 (a1 v)) ∨
     (E u ∧ op (a1 (a2 (a2 u))) u = a1 v ∧ op u v = a1 (a2 (a2 u))))) := by
  by_cases hg : G u v
  · have e : op u v = _ := op.eq_1 u v
    simp only [dif_pos hg] at e
    split at e
    · rename_i h; exact Or.inr ⟨hg, Or.inl ⟨h.1, h.2, e⟩⟩
    · split at e
      · rename_i h; exact Or.inr ⟨hg, Or.inr ⟨h.1, h.2, e⟩⟩
      · exact Or.inl e
  · exact Or.inl (op_nG hg)

/-- a non-free product is strictly smaller than its right argument -/
theorem TRs (u v : M) : op u v = J u v ∨ (G u v ∧ sz (op u v) < sz v) := by
  rcases TR u v with h | ⟨hg, ⟨h1, h2, h⟩ | ⟨h1, h2, h⟩⟩
  · exact Or.inl h
  · right; refine ⟨hg, ?_⟩; rw [h]; have := G_sz hg; have := sz_a1 (a1 v); omega
  · right; refine ⟨hg, ?_⟩; rw [h]; have := G_sz hg; have := sz_a1 (a2 (a2 u)); have := sz_a2 (a2 u); have := sz_a2 u; omega

theorem op_self (u : M) : op u u = J u u := by
  apply op_nG; intro h; have := G_sz h; omega

/-- z ◇ (y ◇ y) is always free -/
theorem op_R (z y : M) : op z (J y y) = J z (J y y) := by
  rcases TR z (J y y) with h | ⟨hg, ⟨h1, h2, h⟩ | ⟨h1, h2, h⟩⟩
  · exact h
  · exfalso
    have h3 := hg.2.2.1; have h5 := hg.2.2.2.2
    simp only [a1_J_eq, a2_J_eq] at h1 h2 h3 h5
    rw [h2] at h3 h5
    have := sz_tg _ h3
    rw [h5] at this; omega
  · exfalso
    simp only [a1_J_eq] at h2
    have h3 := hg.2.2.1; have h4 := hg.2.2.2.1; have h5 := hg.2.2.2.2
    simp only [a2_J_eq] at h3 h4 h5
    have e1 := sz_tg _ h3
    rw [h4, h5] at e1
    have e2 := sz_a2 y
    rcases TRs (a1 (a2 (a2 z))) z with h' | ⟨-, h'⟩
    · rw [h'] at h2
      have := congrArg a2 h2; simp only [a2_J_eq] at this
      have := congrArg sz this; omega
    · rw [h2] at h'; omega

/-- (x ◇ y) ◇ (z ◇ (y ◇ y)) is always free -/
theorem op_S (x y z : M) : op (op x y) (J z (J y y)) = J (op x y) (J z (J y y)) := by
  apply op_nG; intro hg
  have h3 := hg.2.2.1; have h4 := hg.2.2.2.1; have h5 := hg.2.2.2.2
  simp only [a2_J_eq] at h3 h4 h5
  have ey := sz_tg _ h3
  rcases TR x y with h | ⟨hgx, ⟨h1, h2, h⟩ | ⟨h1, h2, h⟩⟩
  · rw [h] at h4; have := congrArg sz h4; simp only [sz] at this; omega
  · rw [h] at h4; have := sz_tg _ h1; have := congrArg sz h4; omega
  · rw [h] at h5
    have g3 := hgx.2.2.1; have g4 := hgx.2.2.2.1
    have := sz_tg _ g3
    rw [g4] at this
    have := sz_a2 (a2 y)
    have := congrArg sz h5
    have := sz_a1 (a2 (a2 x)); have := sz_a2 (a2 x); have := sz_a2 x
    omega

theorem op_R1 (x y z : M) : op y (J (J x y) (J z (J y y))) = x := by
  rw [op.eq_1]; simp [G]

theorem op_R2 {u v : M} (hg : G u v) (h1 : ¬ (tg (a1 v) = 2 ∧ a2 (a1 v) = u)) (h2 : E u)
    (h3 : op (a1 (a2 (a2 u))) u = a1 v) : op u v = a1 (a2 (a2 u)) := by
  rw [op.eq_1, dif_pos hg]; simp only [if_neg h1, if_pos (And.intro h2 h3)]

/-- THE LAW: x = y * ((x * y) * (z * (y * y))) -/
theorem law (x y z : M) : op (y) (op (op (x) (y)) (op (z) (op (y) (y)))) = x := by
  rw [op_self, op_R, op_S]
  have hg : G y (J (op x y) (J z (J y y))) := by simp [G]
  rcases TR x y with hP | ⟨hgx, ⟨h1, h2, hP⟩ | ⟨h1, h2, hP⟩⟩
  · rw [hP]; exact op_R1 x y z
  · have e1 : ¬ (tg (a1 (J (op x y) (J z (J y y)))) = 2 ∧ a2 (a1 (J (op x y) (J z (J y y)))) = y) := by
      simp only [a1_J_eq]; rw [hP]
      intro ⟨t1, t2⟩
      have := congrArg sz t2; have := sz_a2 (a1 (a1 y)); have := sz_a1 (a1 y)
      have := sz_tg _ h1; have := sz_tg _ hgx.1; omega
    have e2 : E y := by
      obtain ⟨p, q, hy⟩ := G_ex hgx
      rw [hy]; simp [E]
    have e3 : op (a1 (a2 (a2 y))) y = a1 (J (op x y) (J z (J y y))) := by
      rw [hgx.2.2.2.1]; simp only [a1_J_eq]
    rw [op_R2 hg e1 e2 e3]; exact hgx.2.2.2.1
  · have e1 : ¬ (tg (a1 (J (op x y) (J z (J y y)))) = 2 ∧ a2 (a1 (J (op x y) (J z (J y y)))) = y) := by
      simp only [a1_J_eq]; rw [hP]
      intro ⟨t1, t2⟩
      have := congrArg sz t2; have := sz_a2 (a1 (a2 (a2 x))); have := sz_a1 (a2 (a2 x))
      have := sz_a2 (a2 x); have := sz_a2 x; have := G_sz hgx; omega
    have e2 : E y := by
      obtain ⟨p, q, hy⟩ := G_ex hgx
      rw [hy]; simp [E]
    have e3 : op (a1 (a2 (a2 y))) y = a1 (J (op x y) (J z (J y y))) := by
      rw [hgx.2.2.2.1]; simp only [a1_J_eq]
    rw [op_R2 hg e1 e2 e3]; exact hgx.2.2.2.1

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
