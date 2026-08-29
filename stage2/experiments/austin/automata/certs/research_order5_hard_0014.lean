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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg (a2 (a2 (a2 v))) = 2 ∧ u = a2 (a2 (a2 (a2 v)))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a1 (a2 u) = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ a2 (a2 (a2 v)) = a1 (a2 (a2 (a2 u))) ∧ a1 (a2 u) = a2 (a2 (a2 (a2 u)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : sz (a1 (a2 u)) + sz (u) < sz u + sz v then op (a1 (a2 u)) (u) else J u v
  let p2 := if hs2 : sz (u) + sz (p1) < sz u + sz v then op (u) (p1) else J u v
  let p3 := if hs3 : sz (u) + sz (p2) < sz u + sz v then op (u) (p2) else J u v
  let p4 := if hs4 : sz (a1 (a2 (p3))) + sz (p3) < sz u + sz v then op (a1 (a2 (p3))) (p3) else J u v
  if P1 u v then a1 (a2 (a2 (a2 v)))
  else if P2 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 u)
  else if P3 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 u)
  else if P4 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ a2 (a2 v) = p2 then a1 (a2 u)
  else if P5 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p2) < sz u + sz v ∧ a2 v = p3 then a1 (a2 u)
  else if P6 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p2) < sz u + sz v ∧ sz (a1 (a2 (p3))) + sz (p3) < sz u + sz v ∧ tg (p3) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = p4 then a1 (a2 u)
  else J u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (g 0)) (op (g 0) (op (g 0) (op (g 0) (g 0))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]
theorem P1_sz {u v : M} (h : P1 u v) : sz v = sz (a1 v) + sz u + sz u + sz (a1 (a2 (a2 (a2 v)))) + sz u + 4 := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
  obtain ⟨b0, b1, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 h3 h4 h5 h6 h7 ⊢
  obtain ⟨c0, c1, rfl⟩ := tg_J _ h2
  simp only [a1_J_eq, a2_J_eq] at h3 h4 h5 h6 h7 ⊢
  obtain ⟨d0, d1, rfl⟩ := tg_J _ h4
  simp only [a1_J_eq, a2_J_eq] at h5 h6 h7 ⊢
  obtain ⟨e0, e1, rfl⟩ := tg_J _ h6
  simp only [a1_J_eq, a2_J_eq] at h7 ⊢
  subst h3; subst h5; subst h7
  simp only [sz]; omega

/-- the unfolding of `op` with the four nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : sz (a1 (a2 u)) + sz u < sz u + sz v then op (a1 (a2 u)) u else J u v) ∧
    p2 = (if hs2 : sz u + sz p1 < sz u + sz v then op u p1 else J u v) ∧
    p3 = (if hs3 : sz u + sz p2 < sz u + sz v then op u p2 else J u v) ∧
    p4 = (if hs4 : sz (a1 (a2 p3)) + sz p3 < sz u + sz v then op (a1 (a2 p3)) p3 else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 (a2 (a2 v)))
  else if P2 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 u)
  else if P3 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 (a2 u)
  else if P4 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ a2 (a2 v) = p2 then a1 (a2 u)
  else if P5 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz u + sz p2 < sz u + sz v ∧ a2 v = p3 then a1 (a2 u)
  else if P6 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz u + sz p2 < sz u + sz v ∧ sz (a1 (a2 p3)) + sz p3 < sz u + sz v ∧ tg p3 = 2 ∧ tg (a2 p3) = 2 ∧ v = p4 then a1 (a2 u)
  else J u v) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`, with the gates of every reachable branch -/
theorem TR4 (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ tg (a2 u) = 2 ∧ op u v = a1 (a2 u) ∧ (
    (P2 u v ∧ a2 (a2 (a2 v)) = op (a1 (a2 u)) u) ∨
    (P4 u v ∧ sz (op (a1 (a2 u)) u) < sz v ∧ a2 (a2 v) = op u (op (a1 (a2 u)) u)) ∨
    (tg v = 2 ∧ sz (op (a1 (a2 u)) u) < sz v ∧ sz (op u (op (a1 (a2 u)) u)) < sz v ∧ a2 v = op u (op u (op (a1 (a2 u)) u))) ∨
    (sz (op (a1 (a2 u)) u) < sz v ∧ sz (op u (op (a1 (a2 u)) u)) < sz v ∧ sz (a1 (a2 (op u (op u (op (a1 (a2 u)) u))))) + sz (op u (op u (op (a1 (a2 u)) u))) < sz u + sz v ∧ v = op (a1 (a2 (op u (op u (op (a1 (a2 u)) u))))) (op u (op u (op (a1 (a2 u)) u)))))) := by
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr ⟨h2.2.2.2.2.2.1, h2.2.2.2.2.2.2, rfl, Or.inl ⟨h2, he⟩⟩)
    · split
      · rename_i h1 h2 h
        exfalso; apply h2
        obtain ⟨h3, hs1, he⟩ := h
        exact ⟨⟨h3.1, h3.2.1, h3.2.2.1, h3.2.2.2.1, h3.2.2.2.2.1, h3.2.2.2.2.2.1, h3.2.2.2.2.2.2.1⟩, hs1, he⟩
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs1, hs2, he⟩ := h
          rw [dif_pos hs1] at hp1; subst hp1
          rw [dif_pos hs2] at hp2; subst hp2
          exact Or.inr (Or.inr ⟨h4.2.2.2.1, h4.2.2.2.2, rfl, Or.inr (Or.inl ⟨h4, by omega, he⟩)⟩)
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨h5, hs1, hs2, hs3, he⟩ := h
            rw [dif_pos hs1] at hp1; subst hp1
            rw [dif_pos hs2] at hp2; subst hp2
            rw [dif_pos hs3] at hp3; subst hp3
            exact Or.inr (Or.inr ⟨h5.2.1, h5.2.2, rfl, Or.inr (Or.inr (Or.inl ⟨h5.1, by omega, by omega, he⟩))⟩)
          · split
            · rename_i h1 h2 h3 h4 h5 h
              obtain ⟨h6, hs1, hs2, hs3, hs4, ht1, ht2, he⟩ := h
              rw [dif_pos hs1] at hp1; subst hp1
              rw [dif_pos hs2] at hp2; subst hp2
              rw [dif_pos hs3] at hp3; subst hp3
              rw [dif_pos hs4] at hp4; subst hp4
              exact Or.inr (Or.inr ⟨h6.1, h6.2, rfl, Or.inr (Or.inr (Or.inr ⟨by omega, by omega, hs4, he⟩))⟩)
            · left; rfl

theorem TR (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ tg (a2 u) = 2 ∧ op u v = a1 (a2 u)) := by
  rcases TR4 u v with h | h | ⟨h1, h2, h3, -⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr ⟨h1, h2, h3⟩)

theorem sz_op_le (u v : M) : sz (op u v) ≤ sz u + sz v + 1 := by
  rcases TR u v with h | ⟨-, h⟩ | ⟨-, -, h⟩
  · rw [h]; simp [sz]
  · rw [h]; have := sz_a1 (a2 (a2 (a2 v))); have := sz_a2 (a2 (a2 v)); have := sz_a2 (a2 v); have := sz_a2 v; omega
  · rw [h]; have := sz_a1 (a2 u); have := sz_a2 u; omega

theorem TRs (u v : M) : op u v = J u v ∨ sz (op u v) < sz v ∨ sz (op u v) < sz u := by
  rcases TR u v with h | ⟨h1, h⟩ | ⟨h1, -, h⟩
  · exact Or.inl h
  · right; left; rw [h]; have := sz_tg v h1.1; have := sz_a1 (a2 (a2 (a2 v))); have := sz_a2 (a2 (a2 v)); have := sz_a2 (a2 v); omega
  · right; right; rw [h]; have := sz_tg u h1; have := sz_a1 (a2 u); omega

/-- the second product of the decoding chain is free -/
theorem Q2free {u : M} (hd : tg u = 2 ∧ tg (a2 u) = 2) : op u (op (a1 (a2 u)) u) = J u (op (a1 (a2 u)) u) := by
  have hq := sz_op_le (a1 (a2 u)) u
  have s1 := sz_tg u hd.1
  have s2 := sz_tg (a2 u) hd.2
  rcases TR4 u (op (a1 (a2 u)) u) with h | ⟨h1, -⟩ | ⟨-, -, -, h⟩
  · exact h
  · have := P1_sz h1; omega
  · rcases h with ⟨h2, he⟩ | ⟨-, hs, -⟩ | ⟨-, hs, -⟩ | ⟨hs, -⟩
    · have t1 := sz_tg _ h2.1
      have t2 := sz_tg _ h2.2.1
      have t3 := sz_tg _ h2.2.2.2.1
      rw [he] at t3; omega
    · exact absurd hs (Nat.lt_irrefl _)
    · exact absurd hs (Nat.lt_irrefl _)
    · exact absurd hs (Nat.lt_irrefl _)

/-- the third product of the decoding chain is free -/
theorem R3free {u : M} (hd : tg u = 2 ∧ tg (a2 u) = 2) : op u (J u (op (a1 (a2 u)) u)) = J u (J u (op (a1 (a2 u)) u)) := by
  have hq := sz_op_le (a1 (a2 u)) u
  have s1 := sz_tg u hd.1
  have s2 := sz_tg (a2 u) hd.2
  rcases TR4 u (J u (op (a1 (a2 u)) u)) with h | ⟨h1, -⟩ | ⟨-, -, -, h⟩
  · exact h
  · have := P1_sz h1; simp only [a1_J_eq, a2_J_eq, sz] at this; omega
  · rcases h with ⟨h2, he⟩ | ⟨h4, -, he⟩ | ⟨-, -, hs, -⟩ | ⟨-, hs, -⟩
    · simp only [a2_J_eq] at he
      have t1 := sz_tg _ h2.2.1
      have t2 := sz_tg _ h2.2.2.2.1
      simp only [a1_J_eq, a2_J_eq] at t1 t2
      rw [he] at t2; omega
    · rw [Q2free hd] at he; simp only [a2_J_eq] at he
      have := congrArg sz he; simp only [sz] at this; have := sz_a2 (op (a1 (a2 u)) u); omega
    · rw [Q2free hd] at hs; exact absurd hs (Nat.lt_irrefl _)
    · rw [Q2free hd] at hs; exact absurd hs (Nat.lt_irrefl _)

/-- the clean characterisation: free, or P1, or the P2 shape -/
theorem TR5 (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ tg (a2 u) = 2 ∧
    tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ a2 (a2 (a2 v)) = op (a1 (a2 u)) u ∧ op u v = a1 (a2 u)) := by
  rcases TR4 u v with h | h | ⟨hd1, hd2, hr, h⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · have hd : tg u = 2 ∧ tg (a2 u) = 2 := ⟨hd1, hd2⟩
    right; right
    rcases h with ⟨h2, he⟩ | ⟨h4, hs2, he⟩ | ⟨htv, hs2, hs3, he⟩ | ⟨hs2, hs3, hs4, he⟩
    · exact ⟨hd1, hd2, h2.1, h2.2.1, h2.2.2.1, h2.2.2.2.1, h2.2.2.2.2.1, he, hr⟩
    · rw [Q2free hd] at he
      refine ⟨hd1, hd2, h4.1, h4.2.1, h4.2.2.1, ?_, ?_, ?_, hr⟩ <;> rw [he] <;> rfl
    · rw [Q2free hd, R3free hd] at he
      refine ⟨hd1, hd2, htv, ?_, ?_, ?_, ?_, ?_, hr⟩ <;> rw [he] <;> rfl
    · rw [Q2free hd, R3free hd] at hs4 he
      simp only [a1_J_eq, a2_J_eq] at hs4 he
      have hq := sz_op_le (a1 (a2 u)) u
      rcases TR u (J u (J u (op (a1 (a2 u)) u))) with h' | ⟨-, h'⟩ | ⟨-, -, h'⟩
      · rw [h'] at he; subst he
        exact ⟨hd1, hd2, rfl, rfl, rfl, rfl, rfl, rfl, hr⟩
      · rw [h'] at he; simp only [a2_J_eq] at he
        have := sz_a1 (a2 (op (a1 (a2 u)) u)); have := sz_a2 (op (a1 (a2 u)) u)
        rw [he] at hs4; simp only [sz] at hs4; omega
      · rw [h'] at he
        have := sz_a1 (a2 u); have := sz_a2 u
        rw [he] at hs4; simp only [sz] at hs4; omega

theorem L1 (x y : M) : op x y = J x y ∨ (tg y = 2 ∧ tg (a2 y) = 2 ∧ x = a1 (a2 y)) := by
  rcases TR5 x y with h | ⟨h1, -⟩ | ⟨-, -, h1, h2, h3, -⟩
  · exact Or.inl h
  · exact Or.inr ⟨h1.1, h1.2.1, h1.2.2.1⟩
  · exact Or.inr ⟨h1, h2, h3⟩

theorem QA (x y : M) : op y (J x y) = J y (J x y) := by
  rcases TR5 y (J x y) with h | ⟨⟨-, h2, h3, -⟩, -⟩ | ⟨-, -, -, h2, h3, -⟩
  · exact h
  · simp only [a2_J_eq] at h2 h3; have := sz_tg y h2; rw [← h3] at this; omega
  · simp only [a2_J_eq] at h2 h3; have := sz_tg y h2; rw [← h3] at this; omega

theorem RA (x y : M) : op y (J y (J x y)) = J y (J y (J x y)) := by
  rcases TR5 y (J y (J x y)) with h | ⟨⟨-, -, -, h4, h5, -⟩, -⟩ | ⟨-, -, -, -, -, h4, h5, -⟩
  · exact h
  · simp only [a2_J_eq] at h4 h5; have := sz_tg y h4; rw [← h5] at this; omega
  · simp only [a2_J_eq] at h4 h5; have := sz_tg y h4; rw [← h5] at this; omega

theorem SA (x y z : M) : op z (J y (J y (J x y))) = J z (J y (J y (J x y))) := by
  rcases TR5 z (J y (J y (J x y))) with h | ⟨⟨-, -, h3, -, h5, h6, h7⟩, -⟩ | ⟨-, -, -, -, h3, -, h5, h7, -⟩
  · exact h
  · simp only [a1_J_eq, a2_J_eq] at h3 h5 h6 h7
    subst h3; subst h5
    have := sz_tg z h6; rw [← h7] at this; omega
  · simp only [a1_J_eq, a2_J_eq] at h3 h5 h7
    subst h3; subst h5
    rcases TRs (a1 (a2 z)) z with h' | h' | h'
    · rw [h'] at h7; have := congrArg sz h7; simp only [sz] at this; omega
    · rw [← h7] at h'; exact absurd h' (Nat.lt_irrefl _)
    · rw [← h7] at h'; have := sz_a1 (a2 z); have := sz_a2 z; omega

theorem SB {y : M} (hd : tg y = 2 ∧ tg (a2 y) = 2) (z : M) :
    op z (J y (J y (op (a1 (a2 y)) y))) = J z (J y (J y (op (a1 (a2 y)) y))) := by
  have s1 := sz_tg y hd.1
  have s2 := sz_tg (a2 y) hd.2
  rcases TR5 z (J y (J y (op (a1 (a2 y)) y))) with h | ⟨⟨-, -, h3, h4, h5, h6, h7⟩, -⟩ | ⟨-, -, -, -, h3, h4, h5, h7, -⟩
  · exact h
  · simp only [a1_J_eq, a2_J_eq] at h3 h4 h5 h6 h7
    subst h3
    have t1 := sz_tg _ h4
    have t2 := sz_tg _ h6
    rcases TRs (a1 (a2 z)) z with h' | h' | h'
    · rw [h'] at h5; simp only [a1_J_eq] at h5; have := congrArg sz h5; omega
    · have := congrArg sz h7; have := sz_a2 (a2 (op (a1 (a2 z)) z)); have := sz_a2 (op (a1 (a2 z)) z); omega
    · have := congrArg sz h7; have := sz_a2 (a2 (op (a1 (a2 z)) z)); have := sz_a2 (op (a1 (a2 z)) z); have := sz_a1 (a2 z); have := sz_a2 z; omega
  · simp only [a1_J_eq, a2_J_eq] at h3 h4 h5 h7
    subst h3
    have t1 := sz_tg _ h4
    rw [h7] at t1; have := sz_a1 (op (a1 (a2 z)) z); omega

theorem op_R1 (y z x : M) : op y (J z (J y (J y (J x y)))) = x := by
  obtain ⟨p1, p2, p3, p4, -, -, -, -, hop⟩ := op_cases y (J z (J y (J y (J x y))))
  have h1 : P1 y (J z (J y (J y (J x y)))) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

theorem op_R2 {y : M} (hd : tg y = 2 ∧ tg (a2 y) = 2) (z : M) :
    op y (J z (J y (J y (op (a1 (a2 y)) y)))) = a1 (a2 y) := by
  have t := TRs (a1 (a2 y)) y
  have s1 := sz_a1 (a2 y)
  have s2 := sz_a2 y
  have s3 := sz_a2 (op (a1 (a2 y)) y)
  obtain ⟨p1, p2, p3, p4, hp1, hp2, hp3, hp4, hop⟩ := op_cases y (J z (J y (J y (op (a1 (a2 y)) y))))
  rw [hop]
  have hs1 : sz (a1 (a2 y)) + sz y < sz y + sz (J z (J y (J y (op (a1 (a2 y)) y)))) := by
    simp only [sz]; omega
  rw [dif_pos hs1] at hp1; subst hp1
  split
  · rename_i h
    obtain ⟨-, -, -, -, -, h6, h7⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6 h7 ⊢
    rcases t with h' | h' | h'
    · rw [h']; rfl
    · have := congrArg sz h7; omega
    · have := congrArg sz h7; omega
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hd.1, hd.2⟩, hs1, rfl⟩

/-- THE LAW: x = y * (z * (y * (y * (x * y)))) -/
theorem law (x y z : M) : op (y) (op (z) (op (y) (op (y) (op (x) (y))))) = x := by
  rcases L1 x y with hP | ⟨hd1, hd2, hx⟩
  · rw [hP, QA, RA, SA, op_R1]
  · subst hx
    rw [Q2free ⟨hd1, hd2⟩, R3free ⟨hd1, hd2⟩, SB ⟨hd1, hd2⟩, op_R2 ⟨hd1, hd2⟩]


theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
