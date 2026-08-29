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
theorem tg_g (t : M) (h : tg t ≠ 2) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl
/-- the recursion measure: lexicographic (max size, total size), packed into one Nat -/
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v)) ∧ tg (a2 v) = 2 ∧ a2 (a1 (a1 v)) = a1 (a2 v) ∧ a2 (a1 v) = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ tg (a1 (a1 (a2 (a1 v)))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v
  let p2 := if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v
  let p3 := if hs3 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v
  let p5 := if hs5 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p3 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p4 ∧ a1 (a1 v) = p5 then a1 (a1 (a1 (a2 (a1 v))))
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (op (op (g 0) (g 0)) (g 0)) (g 1)) (op (g 0) (g 2))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]

theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- the unfolding of `op` with the four nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
    p1 = (if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v) ∧
    p3 = (if hs3 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v) ∧
    p5 = (if hs5 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p3 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p4 ∧ a1 (a1 v) = p5 then a1 (a1 (a1 (a2 (a1 v))))
  else J u v) :=
  ⟨_, _, _, _, _, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guards) -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 (a1 v))) ∨
    (P2 u v ∧ a2 v = op (a2 (a1 (a1 v))) (a2 (a1 v)) ∧ op u v = a2 (a1 (a1 v))) ∨
    (P3 u v ∧ a1 v = op (op u (a1 (a2 v))) (a2 (a2 v)) ∧ op u v = a1 (a2 v)) ∨
    (P4 u v ∧ a2 v = op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) ∧ a1 (a1 v) = op u (a1 (a1 (a1 (a2 (a1 v))))) ∧ op u v = a1 (a1 (a1 (a2 (a1 v))))) := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨h2, he, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs2, hs3, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs4, hs5, he4, he5⟩ := h
          rw [dif_pos hs4] at hp4; subst hp4
          rw [dif_pos hs5] at hp5; subst hp5
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he4, he5, rfl⟩)))
        · left; rfl

/-- every rule needs `tg v = 2` and returns a proper subterm of `v` -/
theorem TRv (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  rcases TR4 u v with h | ⟨h1, h⟩ | ⟨h2, -, h⟩ | ⟨h3, -, h⟩ | ⟨h4, -, -, h⟩
  · exact Or.inl h
  · right; rw [h]
    obtain ⟨hv2, hav2, haav2, -, -, -, -⟩ := h1
    have := sz_a2_lt haav2; have := sz_a1 (a1 v); have := sz_a1 v
    omega
  · right; rw [h]
    obtain ⟨hv2, hav2, haav2, -⟩ := h2
    have := sz_a2_lt haav2; have := sz_a1 (a1 v); have := sz_a1 v
    omega
  · right; rw [h]
    obtain ⟨hv2, hav2⟩ := h3
    have := sz_a1_lt hav2; have := sz_a2 v
    omega
  · right; rw [h]
    obtain ⟨hv2, hav2, haav2, ha3, ha4⟩ := h4
    have := sz_a1_lt ha4; have := sz_a1 (a1 (a2 (a1 v))); have := sz_a1 (a2 (a1 v)); have := sz_a2 (a1 v); have := sz_a1 v
    omega

/-- `N2 := op (op y x) z` and `N3 := op x z` never fire R1/R2 together in the "both structurally
    free" sub-case that also has `op y x` free -- clean size contradiction.  The two residual
    sub-cases (`op y x` itself decoded; or either N2/N3 decoded) are NOT yet closed -- see REMAINING
    in the wave report. -/
theorem V_free_partial (x y z : M) : op (op (op y x) z) (op x z) = J (op (op y x) z) (op x z) := by
  rcases TR4 (op (op y x) z) (op x z) with h | ⟨h1, he⟩ | ⟨h2, hg, he⟩ | ⟨h3, hg, he⟩ | ⟨h4, hg1, hg2, he⟩
  · exact h
  · exfalso
    obtain ⟨hv2, hav2, haav2, hueq, -, -, -⟩ := h1
    have hlt : sz (op (op y x) z) < sz (op x z) := by
      rw [hueq]; have := sz_a1_lt haav2; have := sz_a1 (a1 (op x z)); have := sz_a1 (op x z); omega
    rcases TRv (op y x) z with hN2free | hN2dec
    · rcases TRv x z with hN3free | hN3dec
      · rcases TRv y x with hN1free | hN1dec
        · rw [hN1free] at hlt hN2free; rw [hN2free, hN3free] at hlt
          simp only [sz_J] at hlt; have := sz_pos y; have := sz_pos z; omega
        · sorry -- N1 = op y x decoded: the deep residual case (see REMAINING)
      · rw [hN2free] at hlt; simp only [sz_J] at hlt
        have := sz_pos (op y x)
        omega  -- hN3dec : sz (op x z) < sz z, but hlt needs sz(op y x) + sz z + 1 < sz(op x z) < sz z: impossible
    · sorry -- N2 decoded: never observed empirically but not yet ruled out
  · exfalso
    obtain ⟨hv2, hav2, haav2, hueq⟩ := h2
    have hlt : sz (op (op y x) z) < sz (op x z) := by
      rw [hueq]; have := sz_a1_lt haav2; have := sz_a1 (a1 (op x z)); have := sz_a1 (op x z); omega
    rcases TRv (op y x) z with hN2free | hN2dec
    · rcases TRv x z with hN3free | hN3dec
      · rcases TRv y x with hN1free | hN1dec
        · rw [hN1free] at hlt hN2free; rw [hN2free, hN3free] at hlt
          simp only [sz_J] at hlt; have := sz_pos y; have := sz_pos z; omega
        · sorry -- N1 decoded: deep residual (same shape as the R1 branch above)
      · rw [hN2free] at hlt; simp only [sz_J] at hlt
        have := sz_pos (op y x)
        omega
    · sorry -- N2 decoded: never observed empirically but not yet ruled out
  · exfalso
    sorry -- R3 (B0l): P3 places no direct EQ on u; needs the reflexivity/double-op argument (empirically never fires)
  · exfalso
    sorry -- R4 (B00l,B1l): the rare 1/4000 empirical case; needs the deep reflexivity argument

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
