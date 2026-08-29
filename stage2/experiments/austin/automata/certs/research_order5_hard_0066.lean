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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg (a2 (a2 (a2 v))) = 2 ∧ u = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a1 u = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ a2 (a2 (a2 v)) = a1 (a2 (a2 (a2 u))) ∧ a1 u = a2 (a2 (a2 (a2 u)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : sz (a1 u) + sz (u) < sz u + sz v then op (a1 u) (u) else J u v
  let p2 := if hs2 : sz (u) + sz (p1) < sz u + sz v then op (u) (p1) else J u v
  let p3 := if hs3 : sz (a1 (p2)) + sz (p2) < sz u + sz v then op (a1 (p2)) (p2) else J u v
  let p4 := if hs4 : sz (u) + sz (p3) < sz u + sz v then op (u) (p3) else J u v
  if P1 u v then a1 (a2 (a2 (a2 v)))
  else if P2 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 u
  else if P3 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 u
  else if P4 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ a2 (a2 v) = p2 then a1 u
  else if P5 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (a1 (p2)) + sz (p2) < sz u + sz v ∧ tg (p2) = 2 ∧ a2 v = p3 then a1 u
  else if P6 u v ∧ sz (a1 u) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (a1 (p2)) + sz (p2) < sz u + sz v ∧ sz (u) + sz (p3) < sz u + sz v ∧ tg (p2) = 2 ∧ v = p4 then a1 u
  else J u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (g 0) (op (g 1) (op (g 1) (op (g 0) (op (g 2) (g 2)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]

theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp only [sz] <;> omega

theorem P1_ex {u v : M} (h : P1 u v) : ∃ a w, v = J u (J a (J u (J w u))) := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 h3 h4 h5 h6 h7
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h3
  simp only [a1_J_eq, a2_J_eq] at h4 h5 h6 h7
  obtain ⟨d0, d1, rfl⟩ := tg_J _ h4
  simp only [a1_J_eq, a2_J_eq] at h5 h6 h7
  obtain ⟨e0, e1, rfl⟩ := tg_J _ h6
  simp only [a1_J_eq, a2_J_eq] at h7
  subst h2; subst h5; subst h7
  exact ⟨c0, e0, rfl⟩

theorem P1_sz {u v : M} (h : P1 u v) : sz v = sz u + sz u + sz u + sz (a1 (a2 v)) + sz (a1 (a2 (a2 (a2 v)))) + 4 := by
  obtain ⟨a, w, rfl⟩ := P1_ex h
  simp only [a1_J_eq, a2_J_eq, sz]; omega

theorem P2_shape {u v : M} (h : P2 u v) : v = J u (J (a1 (a2 v)) (J u (a2 (a2 (a2 v))))) := by
  obtain ⟨h1, h2, h3, h4, h5, -⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 h3 h4 h5 ⊢
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h3
  simp only [a1_J_eq, a2_J_eq] at h4 h5 ⊢
  obtain ⟨d0, d1, rfl⟩ := tg_J _ h4
  simp only [a1_J_eq, a2_J_eq] at h5 ⊢
  subst h2; subst h5; rfl

theorem P3_P2 {u v : M} (h : P3 u v) : P2 u v := by
  obtain ⟨h1, h2, h3, h4, h5, h6, -⟩ := h
  exact ⟨h1, h2, h3, h4, h5, h6⟩

theorem P4_shape {u v : M} (h : P4 u v) : v = J u (J (a1 (a2 v)) (a2 (a2 v))) := by
  obtain ⟨h1, h2, h3, -⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 h3 ⊢
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h3
  simp only [a1_J_eq, a2_J_eq] at h2 ⊢
  subst h2; rfl

theorem P5_shape {u v : M} (h : P5 u v) : v = J u (a2 v) := by
  obtain ⟨h1, h2, -⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 ⊢
  subst h2; rfl

def SHP (u v : M) : Prop :=
    (∃ a, v = J u (J a (J u (op (a1 u) u)))) ∨
    (∃ a, v = J u (J a (op u (op (a1 u) u))) ∧ sz (op (a1 u) u) < sz v) ∨
    (v = J u (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) ∧ sz (op (a1 u) u) < sz v ∧ sz (a1 (op u (op (a1 u) u))) + sz (op u (op (a1 u) u)) < sz u + sz v) ∨
    (v = op u (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) ∧ sz (op (a1 u) u) < sz v ∧ sz (a1 (op u (op (a1 u) u))) + sz (op u (op (a1 u) u)) < sz u + sz v ∧ sz (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) < sz v)

def TRP (u v r : M) : Prop := r = J u v ∨ (P1 u v ∧ r = a1 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ r = a1 u ∧ SHP u v)

def q1 (u v : M) : M := if hs1 : sz (a1 u) + sz u < sz u + sz v then op (a1 u) u else J u v
def q2 (u v : M) : M := if hs2 : sz u + sz (q1 u v) < sz u + sz v then op u (q1 u v) else J u v
def q3 (u v : M) : M := if hs3 : sz (a1 (q2 u v)) + sz (q2 u v) < sz u + sz v then op (a1 (q2 u v)) (q2 u v) else J u v
def q4 (u v : M) : M := if hs4 : sz u + sz (q3 u v) < sz u + sz v then op u (q3 u v) else J u v
def body (u v : M) : M :=
  if P1 u v then a1 (a2 (a2 (a2 v)))
  else if P2 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = q1 u v then a1 u
  else if P3 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = q1 u v then a1 u
  else if P4 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ a2 (a2 v) = q2 u v then a1 u
  else if P5 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ sz (a1 (q2 u v)) + sz (q2 u v) < sz u + sz v ∧ tg (q2 u v) = 2 ∧ a2 v = q3 u v then a1 u
  else if P6 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ sz (a1 (q2 u v)) + sz (q2 u v) < sz u + sz v ∧ sz u + sz (q3 u v) < sz u + sz v ∧ tg (q2 u v) = 2 ∧ v = q4 u v then a1 u
  else J u v

theorem op_body (u v : M) : op u v = body u v := by
  rw [op.eq_1 u v]; rfl

theorem q1_pos {u v : M} (h1 : sz (a1 u) + sz u < sz u + sz v) : q1 u v = op (a1 u) u := by
  unfold q1; rw [dif_pos h1]
theorem q2_pos {u v : M} (h1 : sz (a1 u) + sz u < sz u + sz v) (h2 : sz u + sz (op (a1 u) u) < sz u + sz v) :
    q2 u v = op u (op (a1 u) u) := by
  unfold q2; rw [q1_pos h1, dif_pos h2]
theorem q3_pos {u v : M} (h1 : sz (a1 u) + sz u < sz u + sz v) (h2 : sz u + sz (op (a1 u) u) < sz u + sz v)
    (h3 : sz (a1 (op u (op (a1 u) u))) + sz (op u (op (a1 u) u)) < sz u + sz v) :
    q3 u v = op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u)) := by
  unfold q3; rw [q2_pos h1 h2, dif_pos h3]
theorem q4_pos {u v : M} (h1 : sz (a1 u) + sz u < sz u + sz v) (h2 : sz u + sz (op (a1 u) u) < sz u + sz v)
    (h3 : sz (a1 (op u (op (a1 u) u))) + sz (op u (op (a1 u) u)) < sz u + sz v)
    (h4 : sz u + sz (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) < sz u + sz v) :
    q4 u v = op u (op (a1 (op u (op (a1 u) u))) (op u (op (a1 u) u))) := by
  unfold q4; rw [q3_pos h1 h2 h3, dif_pos h4]

theorem TRP_0 (u v : M) : TRP u v (J u v) := by unfold TRP; exact Or.inl rfl
theorem TRP_1 {u v : M} (h : P1 u v) : TRP u v (a1 (a2 (a2 (a2 v)))) := by unfold TRP; exact Or.inr (Or.inl ⟨h, rfl⟩)
theorem TRP_2 {u v : M} (h : P2 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = q1 u v) : TRP u v (a1 u) := by
  unfold TRP SHP
  obtain ⟨hp, hs1, he⟩ := h
  rw [q1_pos hs1] at he
  have hsh := P2_shape hp
  obtain ⟨-, -, -, -, -, h6⟩ := hp
  refine Or.inr (Or.inr ⟨h6, rfl, Or.inl ⟨a1 (a2 v), ?_⟩⟩)
  rw [← he]; exact hsh
theorem TRP_3 {u v : M} (h : P3 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = q1 u v) : TRP u v (a1 u) :=
  TRP_2 ⟨P3_P2 h.1, h.2.1, h.2.2⟩
theorem TRP_4 {u v : M} (h : P4 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ a2 (a2 v) = q2 u v) : TRP u v (a1 u) := by
  unfold TRP SHP
  obtain ⟨hp, hs1, hs2, he⟩ := h
  rw [q1_pos hs1] at hs2
  rw [q2_pos hs1 hs2] at he
  have hsh := P4_shape hp
  obtain ⟨-, -, -, h4⟩ := hp
  refine Or.inr (Or.inr ⟨h4, rfl, Or.inr (Or.inl ⟨a1 (a2 v), ?_, by omega⟩)⟩)
  rw [← he]; exact hsh
theorem TRP_5 {u v : M} (h : P5 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ sz (a1 (q2 u v)) + sz (q2 u v) < sz u + sz v ∧ tg (q2 u v) = 2 ∧ a2 v = q3 u v) : TRP u v (a1 u) := by
  unfold TRP SHP
  obtain ⟨hp, hs1, hs2, hs3, -, he⟩ := h
  rw [q1_pos hs1] at hs2
  rw [q2_pos hs1 hs2] at hs3
  rw [q3_pos hs1 hs2 hs3] at he
  have hsh := P5_shape hp
  obtain ⟨-, -, h3⟩ := hp
  refine Or.inr (Or.inr ⟨h3, rfl, Or.inr (Or.inr (Or.inl ⟨?_, by omega, hs3⟩))⟩)
  rw [← he]; exact hsh
theorem TRP_6 {u v : M} (h : P6 u v ∧ sz (a1 u) + sz u < sz u + sz v ∧ sz u + sz (q1 u v) < sz u + sz v ∧ sz (a1 (q2 u v)) + sz (q2 u v) < sz u + sz v ∧ sz u + sz (q3 u v) < sz u + sz v ∧ tg (q2 u v) = 2 ∧ v = q4 u v) : TRP u v (a1 u) := by
  unfold TRP SHP
  obtain ⟨hp, hs1, hs2, hs3, hs4, -, he⟩ := h
  rw [q1_pos hs1] at hs2
  rw [q2_pos hs1 hs2] at hs3
  rw [q3_pos hs1 hs2 hs3] at hs4
  rw [q4_pos hs1 hs2 hs3 hs4] at he
  exact Or.inr (Or.inr ⟨hp, rfl, Or.inr (Or.inr (Or.inr ⟨he, by omega, hs3, by omega⟩))⟩)

theorem TR_core (u v : M) : TRP u v (op u v) := by
  rw [op_body u v]
  unfold body
  repeat' split
  all_goals first
    | exact TRP_0 u v
    | (rename_i h; first
        | exact TRP_1 h | exact TRP_2 h | exact TRP_3 h | exact TRP_4 h | exact TRP_5 h | exact TRP_6 h)

theorem TR_full (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ op u v = a1 u ∧ SHP u v) :=
  TR_core u v

theorem C1 (u : M) (hu : tg u = 2) : op (a1 u) u = J (a1 u) u ∨ sz (op (a1 u) u) < sz u := by
  have s1 := sz_a1 u; have s2 := sz_a1 (a1 u); have s3 := sz_tg u hu; have s4 := sz_pos (a2 u)
  rcases TR_full (a1 u) u with h | ⟨h, he⟩ | ⟨-, he, -⟩
  · exact Or.inl h
  · right; have hz := P1_sz h; rw [he]; omega
  · right; rw [he]; omega

theorem C2 (u : M) (hu : tg u = 2) : op u (op (a1 u) u) = J u (op (a1 u) u) := by
  have s1 := sz_a1 u; have s3 := sz_tg u hu; have s4 := sz_pos (a2 u)
  rcases TR_full u (op (a1 u) u) with h | ⟨h, -⟩ | ⟨-, -, h⟩
  · exact h
  · exfalso
    have hz := P1_sz h
    rcases C1 u hu with h1 | h1
    · rw [h1] at hz; simp only [sz, a1_J_eq, a2_J_eq] at hz; omega
    · omega
  · exfalso
    unfold SHP at h
    rcases h with ⟨a, h⟩ | ⟨a, -, h⟩ | ⟨-, h, -⟩ | ⟨-, h, -, -⟩
    · have := congrArg sz h; simp only [sz] at this; omega
    · omega
    · omega
    · omega

theorem C3 (u : M) (hu : tg u = 2) : op u (J u (op (a1 u) u)) = J u (J u (op (a1 u) u)) := by
  have s1 := sz_a1 u; have s3 := sz_tg u hu; have s4 := sz_pos (a2 u)
  rcases TR_full u (J u (op (a1 u) u)) with h | ⟨h, -⟩ | ⟨-, -, h⟩
  · exact h
  · exfalso
    have hz := P1_sz h
    simp only [a1_J_eq, a2_J_eq, sz] at hz
    rcases C1 u hu with h1 | h1
    · rw [h1] at hz; simp only [sz, a1_J_eq, a2_J_eq] at hz; omega
    · omega
  · exfalso
    unfold SHP at h
    rcases h with ⟨a, h⟩ | ⟨a, h, -⟩ | ⟨-, -, h⟩ | ⟨-, -, h, -⟩
    · injection h with _ h; have := congrArg sz h; simp only [sz] at this; omega
    · injection h with _ h; rw [C2 u hu] at h; have := congrArg sz h; simp only [sz] at this; omega
    · rw [C2 u hu] at h; simp only [a1_J_eq, sz] at h; omega
    · rw [C2 u hu] at h; simp only [a1_J_eq, sz] at h; omega

theorem C4 (u : M) (hu : tg u = 2) : op u (J u (J u (op (a1 u) u))) = J u (J u (J u (op (a1 u) u))) := by
  have s1 := sz_a1 u; have s3 := sz_tg u hu; have s4 := sz_pos (a2 u)
  rcases TR_full u (J u (J u (op (a1 u) u))) with h | ⟨h, -⟩ | ⟨-, -, h⟩
  · exact h
  · exfalso
    have hz := P1_sz h
    simp only [a1_J_eq, a2_J_eq, sz] at hz
    rcases C1 u hu with h1 | h1
    · rw [h1] at hz; simp only [sz, a1_J_eq, a2_J_eq] at hz; omega
    · omega
  · exfalso
    unfold SHP at h
    rcases h with ⟨a, h⟩ | ⟨a, h, -⟩ | ⟨h, -, -⟩ | ⟨-, -, -, h⟩
    · injection h with _ h; injection h with _ h; have := congrArg sz h; simp only [sz] at this; omega
    · injection h with _ h; injection h with _ h; rw [C2 u hu] at h; have := congrArg sz h; simp only [sz] at this; omega
    · injection h with _ h; rw [C2 u hu] at h; simp only [a1_J_eq] at h; rw [C3 u hu] at h
      have := congrArg sz h; simp only [sz] at this; omega
    · rw [C2 u hu] at h; simp only [a1_J_eq] at h; rw [C3 u hu] at h; simp only [sz] at h; omega

theorem SH (u v : M) : op u v = J u v ∨ P1 u v ∨ (tg u = 2 ∧ ∃ a, v = J u (J a (J u (op (a1 u) u)))) := by
  rcases TR_full u v with h | ⟨h, -⟩ | ⟨hu, -, h⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · right; right; refine ⟨hu, ?_⟩
    unfold SHP at h
    rcases h with ⟨a, h⟩ | ⟨a, h, -⟩ | ⟨h, -, -⟩ | ⟨h, -, -, -⟩
    · exact ⟨a, h⟩
    · rw [C2 u hu] at h; exact ⟨a, h⟩
    · rw [C2 u hu] at h; simp only [a1_J_eq] at h; rw [C3 u hu] at h; exact ⟨u, h⟩
    · rw [C2 u hu] at h; simp only [a1_J_eq] at h; rw [C3 u hu, C4 u hu] at h; exact ⟨u, h⟩

theorem LemB (x y : M) : op x y = J x y ∨ (tg y = 2 ∧ x = a1 y ∧ sz (op x y) < sz y) := by
  rcases TR_full x y with h | ⟨h, he⟩ | ⟨hx, he, h⟩
  · exact Or.inl h
  · right
    have hz := P1_sz h
    obtain ⟨a, w, rfl⟩ := P1_ex h
    refine ⟨rfl, rfl, ?_⟩
    rw [he]; simp only [a1_J_eq, a2_J_eq, sz] at hz ⊢; omega
  · right
    have s1 := sz_a1 x
    unfold SHP at h
    rcases h with ⟨a, rfl⟩ | ⟨a, rfl, -⟩ | ⟨rfl, -, -⟩ | ⟨rfl, -, -, -⟩
    · refine ⟨rfl, rfl, ?_⟩; rw [he]; simp only [sz]; omega
    · refine ⟨rfl, rfl, ?_⟩; rw [he, C2 x hx]; simp only [sz]; omega
    · refine ⟨rfl, rfl, ?_⟩; rw [he, C2 x hx]; simp only [a1_J_eq]; rw [C3 x hx]; simp only [sz]; omega
    · rw [he, C2 x hx]; simp only [a1_J_eq]; rw [C3 x hx, C4 x hx]
      refine ⟨rfl, rfl, ?_⟩; simp only [sz]; omega

theorem R1 (u a w : M) : op u (J u (J a (J u (J w u)))) = w := by
  have hP1 : P1 u (J u (J a (J u (J w u)))) := by simp [P1]
  rw [op_body, body, if_pos hP1]
  all_goals rfl

theorem R2 (u a : M) (hu : tg u = 2) : op u (J u (J a (J u (op (a1 u) u)))) = a1 u := by
  have s1 := sz_a1 u; have s3 := sz_tg u hu; have s4 := sz_pos (a2 u)
  have hs1 : sz (a1 u) + sz u < sz u + sz (J u (J a (J u (op (a1 u) u)))) := by
    simp only [sz]; omega
  have hP2 : P2 u (J u (J a (J u (op (a1 u) u)))) := by simp [P2, hu]
  rw [op_body, body]
  by_cases h1 : P1 u (J u (J a (J u (op (a1 u) u))))
  · rw [if_pos h1]
    have hz := P1_sz h1
    simp only [a1_J_eq, a2_J_eq, sz] at hz ⊢
    rcases C1 u hu with h2 | h2
    · rw [h2, a1_J_eq]
    · exfalso; omega
  · rw [if_neg h1]
    split
    · rfl
    · rename_i h2; exact (h2 ⟨hP2, hs1, (q1_pos hs1).symm⟩).elim

theorem N2 (x y : M) : op y (op x y) = J y (op x y) := by
  rcases SH y (op x y) with h | h | ⟨hy, a, h⟩
  · exact h
  · obtain ⟨a, w, h⟩ := P1_ex h
    rcases LemB x y with h1 | ⟨-, -, h1⟩
    · rw [h1] at h; injection h with h2 h3; have := congrArg sz h3; simp only [sz] at this; omega
    · rw [h] at h1; simp only [sz] at h1; omega
  · rcases LemB x y with h1 | ⟨-, -, h1⟩
    · rw [h1] at h; injection h with h2 h3; have := congrArg sz h3; simp only [sz] at this; omega
    · rw [h] at h1; simp only [sz] at h1; omega

theorem N3 (x y z : M) : op z (J y (op x y)) = J z (J y (op x y)) := by
  rcases SH z (J y (op x y)) with h | h | ⟨hz, a, h⟩
  · exact h
  · obtain ⟨a, w, h⟩ := P1_ex h
    injection h with h1 h2
    rw [← h1] at h2
    rcases LemB x y with h3 | ⟨-, -, h3⟩
    · rw [h3] at h2; injection h2 with h4 h5; have := congrArg sz h5; simp only [sz] at this; omega
    · rw [h2] at h3; simp only [sz] at h3; omega
  · injection h with h1 h2
    rw [← h1] at h2
    rcases LemB x y with h3 | ⟨-, -, h3⟩
    · rw [h3] at h2; injection h2 with h4 h5; have := congrArg sz h5; simp only [sz] at this; omega
    · rw [h2] at h3; simp only [sz] at h3; omega

theorem N4 (x y z : M) : op y (J z (J y (op x y))) = J y (J z (J y (op x y))) := by
  rcases SH y (J z (J y (op x y))) with h | h | ⟨hy, a, h⟩
  · exact h
  · obtain ⟨a, w, h⟩ := P1_ex h
    injection h with h1 h2; injection h2 with h3 h4
    rcases LemB x y with h5 | ⟨-, -, h5⟩
    · rw [h5] at h4; injection h4 with h6 h7; have := congrArg sz h7; simp only [sz] at this; omega
    · rw [h4] at h5; simp only [sz] at h5; omega
  · injection h with h1 h2; injection h2 with h3 h4
    rcases LemB x y with h5 | ⟨-, -, h5⟩
    · rw [h5] at h4; injection h4 with h6 h7
      rcases C1 y hy with h8 | h8
      · rw [h8] at h7; have := congrArg sz h7; simp only [sz] at this; omega
      · rw [← h7] at h8; omega
    · rw [h4] at h5; simp only [sz] at h5; omega

/-- THE LAW: x = y * (y * (z * (y * (x * y)))) -/
theorem law (x y z : M) : op (y) (op (y) (op (z) (op (y) (op (x) (y))))) = x := by
  rw [N2, N3, N4]
  rcases LemB x y with h | ⟨hy, hx, -⟩
  · rw [h]; exact R1 y z x
  · subst hx; exact R2 y z hy


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
