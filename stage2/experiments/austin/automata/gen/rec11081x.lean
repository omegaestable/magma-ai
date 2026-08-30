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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 v = a1 (a1 u) ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a2 (a1 u))) (u) < msr u v then op (a1 (a2 (a1 u))) (u) else J u v
  let p2 := if hs2 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v
  let p3 := if hs3 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v
  let p4 := if hs4 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 v = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 (a1 u) = p2 ∧ a2 v = p3 then a1 (a1 v)
  else if P4 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p4 then a1 (a1 v)
  else if P5 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 (a1 v) = p4 ∧ a2 v = p1 then a1 (a1 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (op (op (op (g 0) (g 0)) (g 1)) (g 2)) (g 2)) (g 1)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a1 (a2 (a1 u))) (u) < msr u v then op (a1 (a2 (a1 u))) (u) else J u v) ∧
    p2 = (if hs2 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v) ∧
    p4 = (if hs4 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 v)
  else if P2 u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 v = p1 then a1 (a1 v)
  else if P3 u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 (a1 u) = p2 ∧ a2 v = p3 then a1 (a1 v)
  else if P4 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p4 then a1 (a1 v)
  else if P5 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 (a1 v) = p4 ∧ a2 v = p1 then a1 (a1 v)
  else J u v
    ) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or the single common shape, with the firing branch's data -/
theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ tg (a1 v) = 2 ∧ op u v = a1 (a1 v) ∧
    ( (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v))
    ∨ (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ a2 v = op (a1 (a2 (a1 u))) u)
    ∨ (tg (a2 (a1 v)) = 2 ∧ u = a1 (a2 (a1 v)) ∧ a1 (a1 v) = a2 (a2 (a1 v)) ∧ a2 v = a1 (a1 u) ∧
        a2 (a1 u) = op (a2 (a2 u)) (a2 v) ∧ a2 v = op (a2 (a2 u)) u)
    ∨ (tg (a2 v) = 2 ∧ u = a2 (a2 v) ∧ a2 (a1 v) = op u (a1 (a1 v)))
    ∨ (a2 (a1 v) = op u (a1 (a1 v)) ∧ a2 v = op (a1 (a2 (a1 u))) u) )) := by
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    exact Or.inr ⟨h.1, h.2.1, rfl, Or.inl ⟨h.2.2.1, h.2.2.2.1, h.2.2.2.2.1, h.2.2.2.2.2.1, h.2.2.2.2.2.2⟩⟩
  · split
    · rename_i h
      obtain ⟨hP, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr ⟨hP.1, hP.2.1, rfl,
        Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2.1, he⟩)⟩
    · split
      · rename_i h
        obtain ⟨hP, hs2, hs3, he2, he3⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        exact Or.inr ⟨hP.1, hP.2.1, rfl,
          Or.inr (Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2.1,
            hP.2.2.2.2.2.2.2.1, he2, he3⟩))⟩
      · split
        · rename_i h
          obtain ⟨hP, hs4, he⟩ := h
          rw [dif_pos hs4] at hp4; subst hp4
          exact Or.inr ⟨hP.1, hP.2.1, rfl,
            Or.inr (Or.inr (Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2, he⟩)))⟩
        · split
          · rename_i h
            obtain ⟨hP, hs4, hs1, he4, he1⟩ := h
            rw [dif_pos hs4] at hp4; subst hp4
            rw [dif_pos hs1] at hp1; subst hp1
            exact Or.inr ⟨hP.1, hP.2.1, rfl,
              Or.inr (Or.inr (Or.inr (Or.inr ⟨he4, he1⟩)))⟩
          · exact Or.inl rfl

/-- free, or the result is at least four smaller than `v` -/
theorem W (u v : M) : op u v = J u v ∨ (op u v = a1 (a1 v) ∧ sz (op u v) + 4 ≤ sz v) := by
  rcases TR u v with h | ⟨h1, h2, h3, -⟩
  · exact Or.inl h
  · refine Or.inr ⟨h3, ?_⟩
    have e1 := sz_tg v h1
    have e2 := sz_tg (a1 v) h2
    have e3 := sz_pos (a2 v)
    have e4 := sz_pos (a2 (a1 v))
    rw [h3]; omega

theorem NF {a b : M} (h : op a b = b) : False := by
  rcases W a b with hf | ⟨-, hs⟩
  · rw [hf] at h; have := congrArg sz h; simp only [sz] at this; have := sz_pos a; omega
  · rw [h] at hs; omega

/-- the second chain product `op x (op y x)` is always free -/
theorem Bfree (x y : M) : op x (op y x) = J x (op y x) := by
  rcases W y x with hA | ⟨hA1, hA2⟩
  · rw [hA]
    rcases TR x (J y x) with h | ⟨-, -, -, hd⟩
    · exact h
    · exfalso
      simp only [a1_J_eq, a2_J_eq] at hd
      rcases hd with ⟨-, -, -, ht, he⟩ | ⟨-, -, -, he⟩ | ⟨-, -, -, -, -, he⟩ | ⟨ht, he, -⟩ | ⟨-, he⟩
      · have := sz_a2_lt ht; rw [← he] at this; omega
      · exact NF he.symm
      · exact NF he.symm
      · have := sz_a2_lt ht; rw [← he] at this; omega
      · exact NF he.symm
  · rcases TR x (op y x) with h | ⟨h1, -, -, hd⟩
    · exact h
    · exfalso
      have b1 := sz_a2 (a2 (op y x))
      have b2 := sz_a2 (op y x)
      have b3 := sz_a1 (a2 (a1 (op y x)))
      have b4 := sz_a2 (a1 (op y x))
      have b5 := sz_a1 (op y x)
      rcases hd with ⟨-, -, -, -, he⟩ | ⟨-, he, -, -⟩ | ⟨-, he, -, -, -, -⟩ | ⟨-, he, -⟩ | ⟨-, he1⟩
      · rw [← he] at b1; omega
      · rw [← he] at b3; omega
      · rw [← he] at b3; omega
      · rw [← he] at b1; omega
      · rcases W (a1 (a2 (a1 x))) x with hf | ⟨hr, -⟩
        · rw [hf] at he1
          have := congrArg sz he1
          simp only [sz] at this
          have := sz_pos (a1 (a2 (a1 x)))
          omega
        · rw [hr, ← hA1] at he1
          have := sz_a2_lt h1
          rw [he1] at this
          omega

theorem law (x y z : M) : op (y) (op (op (x) (op (y) (x))) (op (z) (y))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
