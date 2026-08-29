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
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v)) ∧ tg u = 2 ∧ a2 (a2 (a2 v)) = a1 u ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ a1 (a2 u) = a1 (a2 (a2 u)) ∧ tg (a2 (a2 (a2 u))) = 2 ∧ a1 (a2 u) = a2 (a2 (a2 (a2 u)))
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
  if P1 u v then a1 v
  else if P2 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 v
  else if P4 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ a2 (a2 v) = p2 then a1 v
  else if P5 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p2) < sz u + sz v ∧ a2 v = p3 then a1 v
  else if P6 u v ∧ sz (a1 (a2 u)) + sz (u) < sz u + sz v ∧ sz (u) + sz (p1) < sz u + sz v ∧ sz (u) + sz (p2) < sz u + sz v ∧ sz (a1 (a2 (p3))) + sz (p3) < sz u + sz v ∧ tg (p3) = 2 ∧ tg (a2 (p3)) = 2 ∧ v = p4 then a1 (a2 (p3))
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



theorem U (u v : M) : ∃ p1 p2 p3 p4 : M,
    (p1 = if hs1 : sz (a1 (a2 u)) + sz u < sz u + sz v then op (a1 (a2 u)) u else J u v) ∧
    (p2 = if hs2 : sz u + sz p1 < sz u + sz v then op u p1 else J u v) ∧
    (p3 = if hs3 : sz u + sz p2 < sz u + sz v then op u p2 else J u v) ∧
    (p4 = if hs4 : sz (a1 (a2 p3)) + sz p3 < sz u + sz v then op (a1 (a2 p3)) p3 else J u v) ∧
    op u v = (if P1 u v then a1 v
      else if P2 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 v
      else if P3 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ a2 (a2 (a2 v)) = p1 then a1 v
      else if P4 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ a2 (a2 v) = p2 then a1 v
      else if P5 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz u + sz p2 < sz u + sz v ∧ a2 v = p3 then a1 v
      else if P6 u v ∧ sz (a1 (a2 u)) + sz u < sz u + sz v ∧ sz u + sz p1 < sz u + sz v ∧ sz u + sz p2 < sz u + sz v ∧ sz (a1 (a2 p3)) + sz p3 < sz u + sz v ∧ tg p3 = 2 ∧ tg (a2 p3) = 2 ∧ v = p4 then a1 (a2 p3)
      else J u v) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the one shape on which `op` is ever non-free: v = J a (J u (J u w)) -/
abbrev SH (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ u = a1 (a2 (a2 v))
/-- the two live rules: R1 (w = J b u) or R2 (w = op (a1 (a2 u)) u) -/
abbrev RL (u v : M) : Prop := (tg (a2 (a2 (a2 v))) = 2 ∧ u = a2 (a2 (a2 (a2 v)))) ∨ (tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 (a2 (a2 v)) = op (a1 (a2 u)) u)
/-- the one-unfold characterisation -/
abbrev TRP (u v : M) : Prop := op u v = J u v ∨ (SH u v ∧ op u v = a1 v ∧ RL u v)

theorem sz_a1_lt {u : M} (h : tg u = 2) : sz (a1 u) < sz u := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz]; omega
theorem sz_a2_lt {u : M} (h : tg u = 2) : sz (a2 u) < sz u := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz]; omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem lt12 {u v : M} (e : u = a1 (a2 v)) (t1 : tg v = 2) (t2 : tg (a2 v) = 2) : sz u < sz v := by
  have := sz_a1 (a2 v); have := sz_a2_lt t1; rw [e]; omega
theorem lt1 {u v : M} (e : u = a1 v) (t : tg v = 2) : sz u < sz v := by
  have := sz_a1_lt t; rw [e]; omega

/-- q := op (a1 (a2 u)) u.  Facts refuting `u = a1 q` / `u = a1 (a2 q)`. -/
theorem nsub2 {u q : M} (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u)) (tq : tg q = 2) (e : u = a1 q) (tu : tg u = 2) : False := by
  rcases ih with rfl | ⟨hs, rfl⟩
  · simp only [a1_J_eq] at e
    have := sz_a1 (a2 u); have := sz_a2_lt tu; have := congrArg sz e; omega
  · have := sz_a1 (a1 u); have := sz_a1_lt tu; have := congrArg sz e; omega
theorem nsub12 {u q : M} (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u)) (tq : tg q = 2) (tq2 : tg (a2 q) = 2) (e : u = a1 (a2 q)) : False := by
  rcases ih with rfl | ⟨hs, rfl⟩
  · simp only [a1_J_eq, a2_J_eq] at e tq2
    have := sz_a1_lt tq2; have := congrArg sz e; omega
  · have := lt12 e tq tq2; have := sz_a1_lt hs.1; omega
theorem tg_of {u q : M} (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u)) (t : tg (a2 q) = 2) : tg u = 2 := by
  rcases ih with rfl | ⟨hs, rfl⟩
  · simpa using t
  · exact hs.1

theorem C2 (u q : M) (hq : op (a1 (a2 u)) u = q) (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u)) :
    op u q = J u q := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u q
  rw [e]
  split
  · rename_i h; exact (nsub12 ih h.1 h.2.1 h.2.2.1).elim
  split
  · rename_i _ h; exact (nsub12 ih h.1.1 h.1.2.1 h.1.2.2.1).elim
  split
  · rename_i _ _ h; exact (nsub12 ih h.1.1 h.1.2.1 h.1.2.2.1).elim
  split
  · rename_i _ _ _ h; exact (nsub12 ih h.1.1 h.1.2.1 h.1.2.2.1).elim
  split
  · rename_i _ _ _ _ h; obtain ⟨-, hs1, hs2, -⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; omega
  split
  · rename_i _ _ _ _ _ h; obtain ⟨-, hs1, hs2, -⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; omega
  rfl

theorem C3 (u q : M) (hq : op (a1 (a2 u)) u = q) (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u))
    (c2 : op u q = J u q) : op u (J u q) = J u (J u q) := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u (J u q)
  rw [e]
  split
  · rename_i h; obtain ⟨-, t2, e1, t3, -⟩ := h; simp only [a1_J_eq, a2_J_eq] at t2 e1 t3
    exact (nsub2 ih t2 e1 (tg_of ih t3)).elim
  split
  · rename_i _ h; obtain ⟨-, t2, e1, t3, -⟩ := h.1; simp only [a1_J_eq, a2_J_eq] at t2 e1 t3
    exact (nsub2 ih t2 e1 (tg_of ih t3)).elim
  split
  · rename_i _ _ h; obtain ⟨-, t2, e1, t3, -⟩ := h.1; simp only [a1_J_eq, a2_J_eq] at t2 e1 t3
    exact (nsub2 ih t2 e1 (tg_of ih t3)).elim
  split
  · rename_i _ _ _ h; obtain ⟨-, t2, e1, tu, -⟩ := h.1; simp only [a1_J_eq, a2_J_eq] at t2 e1
    exact (nsub2 ih t2 e1 tu).elim
  split
  · rename_i _ _ _ _ h; obtain ⟨-, hs1, hs2, hs3, -⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2; omega
  split
  · rename_i _ _ _ _ _ h; obtain ⟨-, hs1, hs2, hs3, -⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2; omega
  rfl

theorem C4 (u q : M) (hq : op (a1 (a2 u)) u = q) (ih : q = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ q = a1 u))
    (c2 : op u q = J u q) (c3 : op u (J u q) = J u (J u q)) : op u (J u (J u q)) = J u (J u (J u q)) := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u (J u (J u q))
  rw [e]
  split
  · rename_i h; obtain ⟨-, -, -, t2, e1, t3, -⟩ := h; simp only [a1_J_eq, a2_J_eq] at t2 e1 t3
    exact (nsub2 ih t2 e1 (tg_of ih t3)).elim
  split
  · rename_i _ h; obtain ⟨-, -, -, t2, e1, tu, -⟩ := h.1; simp only [a1_J_eq, a2_J_eq] at t2 e1
    exact (nsub2 ih t2 e1 tu).elim
  split
  · rename_i _ _ h; obtain ⟨-, -, -, t2, e1, tu, -⟩ := h.1; simp only [a1_J_eq, a2_J_eq] at t2 e1
    exact (nsub2 ih t2 e1 tu).elim
  split
  · rename_i _ _ _ h; obtain ⟨-, hs1, hs2, e2⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    simp only [a2_J_eq] at e2; have := congrArg sz e2; simp only [sz_J] at this; omega
  split
  · rename_i _ _ _ _ h; obtain ⟨-, hs1, hs2, hs3, e3⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    rw [dif_pos hs3, c3] at h3; subst h3
    simp only [a2_J_eq] at e3; have := congrArg sz e3; simp only [sz_J] at this; omega
  split
  · rename_i _ _ _ _ _ h; obtain ⟨-, hs1, hs2, hs3, hs4, -⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    rw [dif_pos hs3, c3] at h3; subst h3
    simp only [a1_J_eq, a2_J_eq] at hs4; omega
  rfl

theorem TR_nog (u v : M) (hs1 : ¬ sz (a1 (a2 u)) + sz u < sz u + sz v) : TRP u v := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u v
  unfold TRP; rw [e]
  split
  · rename_i h; obtain ⟨t1, t2, e1, t3, e2, t4, e4⟩ := h
    exact Or.inr ⟨⟨t1, t2, e1, t3, e2⟩, rfl, Or.inl ⟨t4, e4⟩⟩
  split
  · rename_i _ h; exact (hs1 h.2.1).elim
  split
  · rename_i _ _ h; exact (hs1 h.2.1).elim
  split
  · rename_i _ _ _ h; exact (hs1 h.2.1).elim
  split
  · rename_i _ _ _ _ h; exact (hs1 h.2.1).elim
  split
  · rename_i _ _ _ _ _ h; exact (hs1 h.2.1).elim
  exact Or.inl rfl

theorem TR_aux (u v : M) (hs1 : sz (a1 (a2 u)) + sz u < sz u + sz v) (ih0 : TRP (a1 (a2 u)) u) : TRP u v := by
  have ih : op (a1 (a2 u)) u = J (a1 (a2 u)) u ∨ (SH (a1 (a2 u)) u ∧ op (a1 (a2 u)) u = a1 u) := by
    rcases ih0 with h | ⟨h1, h2, -⟩
    · exact Or.inl h
    · exact Or.inr ⟨h1, h2⟩
  clear ih0
  generalize hq : op (a1 (a2 u)) u = q at ih
  have c2 := C2 u q hq ih
  have c3 := C3 u q hq ih c2
  have c4 := C4 u q hq ih c2 c3
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u v
  unfold TRP; rw [e]
  split
  · rename_i h; obtain ⟨t1, t2, e1, t3, e2, t4, e4⟩ := h
    exact Or.inr ⟨⟨t1, t2, e1, t3, e2⟩, rfl, Or.inl ⟨t4, e4⟩⟩
  split
  · rename_i _ h; obtain ⟨⟨t1, t2, e1, t3, e2, tu, tu2⟩, -, e4⟩ := h
    rw [dif_pos hs1] at h1; subst h1
    exact Or.inr ⟨⟨t1, t2, e1, t3, e2⟩, rfl, Or.inr ⟨tu, tu2, e4⟩⟩
  split
  · rename_i _ _ h; obtain ⟨⟨t1, t2, e1, t3, e2, tu, -, tu2, -⟩, -, e4⟩ := h
    rw [dif_pos hs1] at h1; subst h1
    exact Or.inr ⟨⟨t1, t2, e1, t3, e2⟩, rfl, Or.inr ⟨tu, tu2, e4⟩⟩
  split
  · rename_i _ _ _ h; obtain ⟨⟨t1, t2, e1, tu, tu2⟩, -, hs2, e4⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    refine Or.inr ⟨⟨t1, t2, e1, ?_, ?_⟩, rfl, Or.inr ⟨tu, tu2, ?_⟩⟩
    · rw [e4]; rfl
    · rw [e4]; rfl
    · rw [e4, hq]; rfl
  split
  · rename_i _ _ _ _ h; obtain ⟨⟨t1, tu, tu2⟩, -, hs2, hs3, e4⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    rw [dif_pos hs3, c3] at h3; subst h3
    refine Or.inr ⟨⟨t1, ?_, ?_, ?_, ?_⟩, rfl, Or.inr ⟨tu, tu2, ?_⟩⟩ <;> rw [e4] <;> first | rfl | (rw [hq]; rfl)
  split
  · rename_i _ _ _ _ _ h; obtain ⟨⟨tu, tu2⟩, -, hs2, hs3, hs4, -, -, e4⟩ := h
    rw [dif_pos hs1, hq] at h1; subst h1; rw [dif_pos hs2, c2] at h2; subst h2
    rw [dif_pos hs3, c3] at h3; subst h3
    rw [dif_pos hs4] at h4; simp only [a1_J_eq, a2_J_eq] at h4; rw [c4] at h4; subst h4; subst e4
    exact Or.inr ⟨⟨rfl, rfl, rfl, rfl, rfl⟩, rfl, Or.inr ⟨tu, tu2, hq.symm⟩⟩
  exact Or.inl rfl

theorem TR (u v : M) : TRP u v := by
  by_cases hs1 : sz (a1 (a2 u)) + sz u < sz u + sz v
  · exact TR_aux u v hs1 (TR (a1 (a2 u)) u)
  · exact TR_nog u v hs1
termination_by sz u + sz v
decreasing_by exact hs1

theorem F1 (u a b : M) : op u (J a (J u (J u (J b u)))) = a := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u (J a (J u (J u (J b u))))
  rw [e, if_pos (by unfold P1; exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)]; rfl

theorem F2 (u a w : M) (hw : op (a1 (a2 u)) u = w) (tu : tg u = 2) (tu2 : tg (a2 u) = 2) :
    op u (J a (J u (J u w))) = a := by
  obtain ⟨p1, p2, p3, p4, h1, h2, h3, h4, e⟩ := U u (J a (J u (J u w)))
  have hs1 : sz (a1 (a2 u)) + sz u < sz u + sz (J a (J u (J u w))) := by
    have := sz_a1 (a2 u); have := sz_a2_lt tu; simp only [sz_J]; omega
  rw [dif_pos hs1, hw] at h1; subst h1
  rw [e]
  split
  · rfl
  rw [if_pos ⟨by unfold P2; exact ⟨rfl, rfl, rfl, rfl, rfl, tu, tu2⟩, hs1, rfl⟩]; rfl

/-- products 2, 3, 4 of the law are always free -/
theorem N2 (y z p : M) (hp : p = J z y ∨ (SH z y ∧ p = a1 y)) : op y p = J y p := by
  rcases TR y p with h | ⟨⟨t1, t2, e1, -⟩, -⟩
  · exact h
  · exfalso
    rcases hp with rfl | ⟨hs, rfl⟩
    · simp only [a1_J_eq, a2_J_eq] at e1 t2; have := sz_a1_lt t2; rw [← e1] at this; omega
    · have := lt12 e1 t1 t2; have := sz_a1_lt hs.1; omega

theorem N3 (y z p : M) (hp : p = J z y ∨ (SH z y ∧ p = a1 y)) : op y (J y p) = J y (J y p) := by
  rcases TR y (J y p) with h | ⟨⟨t1, t2, e1, t3, e2⟩, -⟩
  · exact h
  · exfalso
    simp only [a1_J_eq, a2_J_eq] at t2 e1 t3 e2
    rcases hp with rfl | ⟨hs, rfl⟩
    · simp only [a1_J_eq, a2_J_eq] at e2 t3; have := sz_a1_lt t3; rw [← e2] at this; omega
    · have := lt1 e1 t2; have := sz_a1_lt hs.1; omega

theorem N4 (x y z p : M) (hp : p = J z y ∨ (SH z y ∧ p = a1 y)) : op x (J y (J y p)) = J x (J y (J y p)) := by
  rcases TR x (J y (J y p)) with h | ⟨⟨t1, t2, e1, t3, e2⟩, -, ⟨t4, e4⟩ | ⟨tu, tu2, e4⟩⟩
  · exact h
  · exfalso
    simp only [a1_J_eq, a2_J_eq] at e1 t3 e2 t4 e4
    subst e1
    rcases hp with rfl | ⟨hs, rfl⟩
    · simp only [a1_J_eq, a2_J_eq] at e4 t4; have := sz_a2_lt t4; have := congrArg sz e4; omega
    · have := sz_a2 (a2 (a1 x)); have := sz_a2 (a1 x); have := sz_a1_lt hs.1; have := congrArg sz e4; omega
  · exfalso
    simp only [a1_J_eq, a2_J_eq] at e1 t3 e2 e4
    subst e1
    rcases hp with rfl | ⟨hs, rfl⟩
    · simp only [a1_J_eq, a2_J_eq] at e2 e4
      rcases TR (a1 (a2 x)) x with h | ⟨-, h, -⟩
      · rw [h] at e4; have := congrArg sz e4; simp only [sz_J] at this; omega
      · rw [h] at e4; have := congrArg sz e4; have := sz_a1_lt tu; omega
    · have := lt1 e2 t3; have := sz_a1_lt hs.1; omega

/-- THE LAW: x = y * (x * (y * (y * (z * y)))) -/
theorem law (x y z : M) : op (y) (op (x) (op (y) (op (y) (op (z) (y))))) = x := by
  have hp : op z y = J z y ∨ (SH z y ∧ op z y = a1 y) := by
    rcases TR z y with h | ⟨h1, h2, -⟩
    · exact Or.inl h
    · exact Or.inr ⟨h1, h2⟩
  rw [N2 y z _ hp, N3 y z _ hp, N4 x y z _ hp]
  rcases hp with h | ⟨hs, h⟩
  · rw [h]; exact F1 y x z
  · rw [h]; refine F2 y x (a1 y) ?_ hs.1 hs.2.1; rw [← hs.2.2.1]; exact h


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
