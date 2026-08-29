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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a1 (a2 v)) ∧ tg u = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ u = a2 (a2 (a2 v)) ∧ tg u = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg u = 2 ∧ a1 u = a2 u ∧ a1 u = a1 (a2 v)
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  let p2 := if hs2 : msr (a1 (a2 v)) (a2 v) < msr u v then op (a1 (a2 v)) (a2 v) else J u v
  if P1 u v then a1 (a2 (a2 v))
  else if P2 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 (a2 v) = p1 then a1 u
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a1 (a2 v) = p1 then a1 (a2 (a2 v))
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ a1 (a2 v) = p1 ∧ a2 (a2 v) = p1 then a1 u
  else if P5 u v ∧ msr (a1 (a2 v)) (a2 v) < msr u v ∧ a1 u = p2 then J (a2 v) (u)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 2) (g 2))) (op (op (g 0) (g 1)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5]

/-- the unfolding of `op` with the two nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 : M,
    p1 = (if hs1 : msr (a1 u) u < msr u v then op (a1 u) u else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 v)) (a2 v) < msr u v then op (a1 (a2 v)) (a2 v) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 (a2 v))
  else if P2 u v ∧ msr (a1 u) u < msr u v ∧ a2 (a2 v) = p1 then a1 u
  else if P3 u v ∧ msr (a1 u) u < msr u v ∧ a1 (a2 v) = p1 then a1 (a2 (a2 v))
  else if P4 u v ∧ msr (a1 u) u < msr u v ∧ a1 (a2 v) = p1 ∧ a2 (a2 v) = p1 then a1 u
  else if P5 u v ∧ msr (a1 (a2 v)) (a2 v) < msr u v ∧ a1 u = p2 then J (a2 v) u
  else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the five rules with its guards -/
theorem TR5 (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ (
    (P1 u v ∧ op u v = a1 (a2 (a2 v))) ∨
    (P2 u v ∧ a2 (a2 v) = op (a1 u) u ∧ op u v = a1 u) ∨
    (P3 u v ∧ a1 (a2 v) = op (a1 u) u ∧ op u v = a1 (a2 (a2 v))) ∨
    (P4 u v ∧ a1 (a2 v) = op (a1 u) u ∧ a2 (a2 v) = op (a1 u) u ∧ op u v = a1 u) ∨
    (P5 u v ∧ a1 u = op (a1 (a2 v)) (a2 v) ∧ op u v = J (a2 v) u))) := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr ⟨h.1, h.2.1, h.2.2.1, Or.inl ⟨h, rfl⟩⟩
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr ⟨h2.1, h2.2.1, h2.2.2.1, Or.inr (Or.inl ⟨h2, he, rfl⟩)⟩
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs1, he⟩ := h
        rw [dif_pos hs1] at hp1; subst hp1
        exact Or.inr ⟨h3.1, h3.2.1, h3.2.2.1, Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩))⟩
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs1, he1, he2⟩ := h
          rw [dif_pos hs1] at hp1; subst hp1
          exact Or.inr ⟨h4.1, h4.2.1, h4.2.2.1, Or.inr (Or.inr (Or.inr (Or.inl ⟨h4, he1, he2, rfl⟩)))⟩
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨h5, hs2, he⟩ := h
            rw [dif_pos hs2] at hp2; subst hp2
            exact Or.inr ⟨h5.1, h5.2.1, h5.2.2.1, Or.inr (Or.inr (Or.inr (Or.inr ⟨h5, he, rfl⟩)))⟩
          · left; rfl

/-- size form: a decode is strictly smaller than `v`, except the R5 result `J (a2 v) u` (same size as `v`) -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧
    (sz (op u v) < sz v ∨ (tg u = 2 ∧ a1 u = a2 u ∧ a1 u = a1 (a2 v) ∧ a1 u = op (a1 (a2 v)) (a2 v) ∧ op u v = J (a2 v) u))) := by
  rcases TR5 u v with h | ⟨h1, h2, h3, h⟩
  · exact Or.inl h
  · right; refine ⟨h1, h2, h3, ?_⟩
    have s1 := sz_tg v h1
    have s2 := sz_tg (a2 v) h3
    have s3 := sz_a1 (a2 (a2 v))
    have s4 := sz_a2 (a2 v)
    have s5 := sz_a1 u
    have s6 : sz u = sz (a1 v) := by rw [h2]
    rcases h with ⟨-, hr⟩ | ⟨-, -, hr⟩ | ⟨-, -, hr⟩ | ⟨-, -, -, hr⟩ | ⟨h5, he, hr⟩
    · left; rw [hr]; omega
    · left; rw [hr]; omega
    · left; rw [hr]; omega
    · left; rw [hr]; omega
    · right; exact ⟨h5.2.2.2.1, h5.2.2.2.2.1, h5.2.2.2.2.2, he, hr⟩

theorem NF {u v : M} (h : op u v ≠ J u v) : tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 := by
  rcases TR5 u v with h' | ⟨h1, h2, h3, -⟩
  · exact absurd h' h
  · exact ⟨h1, h2, h3⟩

theorem L1 (x y : M) : op x y = J x y ∨ (tg y = 2 ∧ x = a1 y ∧ tg (a2 y) = 2) := by
  rcases TR5 x y with h | ⟨h1, h2, h3, -⟩
  · exact Or.inl h
  · exact Or.inr ⟨h1, h2, h3⟩

/-- a product `op y c` is free whenever `a1 c ≠ y` -/
theorem Dg {c y : M} (hc : a1 c ≠ y) : op y c = J y c := by
  by_contra h
  obtain ⟨-, hu, -⟩ := NF h
  exact hc hu.symm

/-- `q` never decodes `J q q` to itself -/
theorem NQ (q : M) : op q (J q q) ≠ q := by
  intro he
  rcases TR5 q (J q q) with h | ⟨-, -, h3, h⟩
  · rw [h] at he; have := congrArg sz he; simp only [sz] at this; omega
  · simp only [a2_J_eq] at h3
    obtain ⟨q1, q2, rfl⟩ := tg_J q h3
    have s1 := sz_a1 q1; have s2 := sz_a2 q1; have s3 := sz_a1 q2; have s4 := sz_a2 q2
    rcases h with ⟨-, hr⟩ | ⟨-, -, hr⟩ | ⟨-, -, hr⟩ | ⟨-, -, -, hr⟩ | ⟨-, -, hr⟩ <;>
      (rw [hr] at he; (try simp only [a1_J_eq, a2_J_eq] at he); have := congrArg sz he; simp only [sz] at this; omega)

/-- a product never returns its right argument -/
theorem NE (u v : M) : op u v ≠ v := by
  intro he
  rcases TRs u v with h | ⟨h1, h2, h3, h | ⟨h4, h5, h6, h7, h8⟩⟩
  · rw [h] at he; have := congrArg sz he; simp only [sz] at this; omega
  · have := congrArg sz he; omega
  · rw [h8] at he
    obtain ⟨v1, v2, rfl⟩ := tg_J v h1
    simp only [a1_J_eq, a2_J_eq] at h2 he h7
    subst h2
    obtain ⟨hv, -⟩ := M.J.inj he
    subst hv
    obtain ⟨w1, w2, rfl⟩ := tg_J v2 h4
    simp only [a1_J_eq, a2_J_eq] at h5 h7
    subst h5
    exact NQ w1 h7.symm

theorem NQ2 (q : M) : op q (J q (J q q)) ≠ q := by
  intro he
  rcases TR5 q (J q (J q q)) with h | ⟨-, -, -, h⟩
  · rw [h] at he; have := congrArg sz he; simp only [sz] at this; omega
  · rcases h with ⟨hP, hr⟩ | ⟨hP, -, hr⟩ | ⟨hP, hg, hr⟩ | ⟨hP, -, -, hr⟩ | ⟨hP, -, hr⟩
    · obtain ⟨-, -, -, h4, h5, -, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h4 h5
      have := congrArg sz h5; have := sz_tg q h4; have := sz_a2 q; omega
    · obtain ⟨-, -, -, h4, h5, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h4 h5
      have := congrArg sz h5; have := sz_tg q h4; have := sz_a2 q; omega
    · simp only [a1_J_eq, a2_J_eq] at hg
      exact NE (a1 q) q hg.symm
    · obtain ⟨-, -, -, h4⟩ := hP
      rw [hr] at he; have := congrArg sz he; have := sz_tg q h4; omega
    · obtain ⟨-, -, -, h4, -, h6⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h6
      have := congrArg sz h6; have := sz_tg q h4; omega

theorem op_R1 (y z x : M) : op y (J y (J (J z y) (J x y))) = x := by
  obtain ⟨p1, p2, -, -, hop⟩ := op_cases y (J y (J (J z y) (J x y)))
  have h1 : P1 y (J y (J (J z y) (J x y))) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [hop, if_pos h1]
  rfl

/-- the middle product when both `x*y` and `z*y` are free: free, or the R4 coincidence `x = z*y` -/
theorem CFF (x y z : M) : op (J z y) (J x y) = J (J z y) (J x y) ∨
    (x = J z y ∧ tg y = 2 ∧ a1 y = op z (J z y) ∧ a2 y = op z (J z y) ∧ op (J z y) (J x y) = z) := by
  rcases TR5 (J z y) (J x y) with h | ⟨-, hu, hty, h⟩
  · exact Or.inl h
  · simp only [a1_J_eq, a2_J_eq] at hu hty
    subst hu
    have s1 := sz_tg y hty
    have s2 := sz_a1 y
    have s3 := sz_a2 y
    have s4 := sz_a2 (a1 y)
    have s5 := sz_a2 (a2 y)
    rcases h with ⟨hP, -⟩ | ⟨hP, -, -⟩ | ⟨hP, -, -⟩ | ⟨hP, he1, he2, hr⟩ | ⟨hP, -, -⟩
    · obtain ⟨-, -, -, -, h5, -, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h5
      have := congrArg sz h5; simp only [sz] at this; omega
    · obtain ⟨-, -, -, -, h5, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h5
      have := congrArg sz h5; simp only [sz] at this; omega
    · obtain ⟨-, -, -, -, h5, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h5
      have := congrArg sz h5; simp only [sz] at this; omega
    · simp only [a1_J_eq, a2_J_eq] at he1 he2 hr
      exact Or.inr ⟨rfl, hty, he1, he2, hr⟩
    · obtain ⟨-, -, -, -, h5, h6⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h5 h6
      subst h5
      have := congrArg sz h6; omega

/-- the R4 coincidence forces `a1 z = a1 y` and `op (a1 y) z = a1 y` -/
theorem TZ {y z : M} (hty : tg y = 2) (h1 : a1 y = op z (J z y)) (h2 : a2 y = op z (J z y)) :
    tg z = 2 ∧ a1 z = a1 y ∧ op (a1 y) z = a1 y := by
  have s1 := sz_tg y hty
  have s2 := sz_a1 y
  have s3 := sz_a2 y
  have s4 := sz_a1 (a2 y)
  have s5 := sz_a2 (a1 z)
  have s6 := sz_a1 z
  rcases TR5 z (J z y) with h | ⟨-, -, -, h⟩
  · rw [h] at h1; have := congrArg sz h1; simp only [sz] at this; omega
  · rcases h with ⟨hP, hr⟩ | ⟨hP, -, hr⟩ | ⟨hP, -, hr⟩ | ⟨hP, he1, he2, hr⟩ | ⟨hP, -, hr⟩
    · obtain ⟨-, -, -, -, -, h6, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h6 hr
      rw [hr] at h2; have := congrArg sz h2; have := sz_tg (a2 y) h6; omega
    · obtain ⟨-, -, -, -, h5, h6⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h5 hr
      rw [hr] at h1; rw [h1] at h5
      have := congrArg sz h5; have := sz_tg z h6; omega
    · obtain ⟨-, -, -, h4, -, -⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at h4 hr
      rw [hr] at h2; have := congrArg sz h2; have := sz_tg (a2 y) h4; omega
    · obtain ⟨-, -, -, h4⟩ := hP
      simp only [a1_J_eq, a2_J_eq] at he1 hr
      rw [hr] at h1
      refine ⟨h4, h1.symm, ?_⟩
      rw [h1] at he1 ⊢
      exact he1.symm
    · simp only [a1_J_eq, a2_J_eq] at hr
      rw [hr] at h1; have := congrArg sz h1; simp only [sz] at this; omega

/-- R5 fires on `op y (J y z)` when `y = J q q`, `a1 z = q`, `op q z = q` -/
theorem op_R5 {y z : M} (hty : tg y = 2) (hyq : a1 y = a2 y) (htz : tg z = 2) (hz : a1 z = a1 y)
    (hq : op (a1 y) z = a1 y) : op y (J y z) = J z y := by
  obtain ⟨y1, y2, rfl⟩ := tg_J y hty
  simp only [a1_J_eq, a2_J_eq] at hyq hz hq
  subst hyq
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases (J y1 y1) (J (J y1 y1) z)
  have hs1 : msr (a1 (J y1 y1)) (J y1 y1) < msr (J y1 y1) (J (J y1 y1) z) :=
    msr_lt_of_max_lt (by simp only [a1_J_eq, sz]; omega)
  have hs2 : msr (a1 (a2 (J (J y1 y1) z))) (a2 (J (J y1 y1) z)) < msr (J y1 y1) (J (J y1 y1) z) :=
    msr_lt_of_max_lt (by simp only [a2_J_eq, sz]; have := sz_a1 z; omega)
  rw [dif_pos hs1] at hp1; rw [dif_pos hs2] at hp2; subst hp1; subst hp2
  have s1 := sz_a2 y1
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, -, -, h5, -, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h5
    rw [hz] at h5; have := congrArg sz h5; simp only [sz] at this; omega
  · split
    · rename_i h1 h
      obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
      simp only [a1_J_eq, a2_J_eq] at h5
      rw [hz] at h5; have := congrArg sz h5; simp only [sz] at this; omega
    · split
      · rename_i h1 h2 h
        obtain ⟨-, -, he⟩ := h
        simp only [a1_J_eq, a2_J_eq] at he
        rw [hz] at he
        exact absurd he.symm (NQ y1)
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨-, -, he, -⟩ := h
          simp only [a1_J_eq, a2_J_eq] at he
          rw [hz] at he
          exact absurd he.symm (NQ y1)
        · split
          · rfl
          · rename_i h1 h2 h3 h4 h5
            exfalso; apply h5
            refine ⟨⟨rfl, rfl, htz, rfl, rfl, hz.symm⟩, hs2, ?_⟩
            show y1 = op (a1 z) z
            rw [hz]; exact hq.symm

/-- R2: `op y (J y (J (J z y) p))` with `p = op (a1 y) y` returns `a1 y` -/
theorem op_R2 {y : M} (hty : tg y = 2) (z : M) : op y (J y (J (J z y) (op (a1 y) y))) = a1 y := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases y (J y (J (J z y) (op (a1 y) y)))
  have hs1 : msr (a1 y) y < msr y (J y (J (J z y) (op (a1 y) y))) :=
    msr_lt_of_max_lt (by simp only [sz]; have := sz_a1 y; omega)
  rw [dif_pos hs1] at hp1; subst hp1
  have s1 := sz_tg y hty
  have s2 := sz_a2 (op (a1 y) y)
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h7 ⊢
    rcases TRs (a1 y) y with hf | ⟨-, -, -, hs | ⟨-, -, -, -, hr⟩⟩
    · rw [hf]; rfl
    · have := congrArg sz h7; omega
    · rw [hr] at h7; simp only [a2_J_eq] at h7; have := congrArg sz h7; have := sz_a1 y; omega
  · split
    · rfl
    · rename_i h1 h2
      exfalso; apply h2
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hty⟩, hs1, rfl⟩

/-- the middle product when `z*y` is free and `x*y = p` is free -/
theorem CNF {y : M} (hty : tg y = 2) (z : M) : op (J z y) (op (a1 y) y) = J (J z y) (op (a1 y) y) := by
  by_contra h
  obtain ⟨-, hu, -⟩ := NF h
  have s1 := sz_tg y hty
  have s2 := sz_a1 y
  have s3 := sz_a2 y
  have s4 := sz_a1 (op (a1 y) y)
  rcases TRs (a1 y) y with hf | ⟨-, -, -, hs | ⟨-, -, -, -, hr⟩⟩
  · rw [hf] at hu; simp only [a1_J_eq] at hu; have := congrArg sz hu; simp only [sz] at this; omega
  · have := congrArg sz hu; simp only [sz] at this; omega
  · rw [hr] at hu; simp only [a1_J_eq] at hu; have := congrArg sz hu; simp only [sz] at this; omega

/-- R3 (or R1): `op y (J y (J p (J x y)))` with `p = op (a1 y) y` returns `x` -/
theorem op_R3 {y : M} (hty : tg y = 2) (x : M) : op y (J y (J (op (a1 y) y) (J x y))) = x := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases y (J y (J (op (a1 y) y) (J x y)))
  have hs1 : msr (a1 y) y < msr y (J y (J (op (a1 y) y) (J x y))) :=
    msr_lt_of_max_lt (by simp only [sz]; have := sz_a1 y; omega)
  rw [dif_pos hs1] at hp1; subst hp1
  rw [hop]
  split
  · rfl
  · split
    · rename_i h1 h
      exfalso; apply h1
      obtain ⟨⟨-, -, -, h4, h5, -⟩, -, -⟩ := h
      exact ⟨rfl, rfl, rfl, h4, h5, rfl, rfl⟩
    · split
      · rfl
      · rename_i h1 h2 h3
        exfalso; apply h3
        exact ⟨⟨rfl, rfl, rfl, rfl, rfl, hty⟩, hs1, rfl⟩

/-- R4 (or R1/R2): `op y (J y (J p p))` with `p = op (a1 y) y` returns `a1 y` -/
theorem op_R4 {y : M} (hty : tg y = 2) : op y (J y (J (op (a1 y) y) (op (a1 y) y))) = a1 y := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases y (J y (J (op (a1 y) y) (op (a1 y) y)))
  have hs1 : msr (a1 y) y < msr y (J y (J (op (a1 y) y) (op (a1 y) y))) :=
    msr_lt_of_max_lt (by simp only [sz]; have := sz_a1 y; omega)
  rw [dif_pos hs1] at hp1; subst hp1
  have s1 := sz_tg y hty
  have s2 := sz_a2 (op (a1 y) y)
  rw [hop]
  split
  · rename_i h
    obtain ⟨-, -, -, -, h5, -, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h5 ⊢
    rcases TRs (a1 y) y with hf | ⟨-, -, -, hs | ⟨-, -, -, -, hr⟩⟩
    · rw [hf]; rfl
    · have := congrArg sz h5; omega
    · rw [hr] at h5; simp only [a2_J_eq] at h5; have := congrArg sz h5; have := sz_a1 y; omega
  · split
    · rfl
    · split
      · rename_i h1 h2 h
        exfalso; apply h2
        obtain ⟨⟨-, -, -, h4, h5, h6⟩, hs, he⟩ := h
        exact ⟨⟨rfl, rfl, rfl, h4, h5, h6⟩, hs, he⟩
      · split
        · rfl
        · rename_i h1 h2 h3 h4
          exfalso; apply h4
          exact ⟨⟨rfl, rfl, rfl, hty⟩, hs1, rfl, rfl⟩

/-- THE HARD ONE: with `p = op (a1 y) y`, the product `op p (J x y)` is free (the only candidate is `x = p`,
and every rule on `(p, J p y)` contradicts the derivation of `p`) -/
theorem CFN {y : M} (hty : tg y = 2) (hta : tg (a2 y) = 2) (x : M) :
    op (op (a1 y) y) (J x y) = J (op (a1 y) y) (J x y) := by
  by_contra h
  obtain ⟨-, hu, -⟩ := NF h
  simp only [a1_J_eq] at hu
  subst hu
  obtain ⟨y1, y2, rfl⟩ := tg_J y hty
  simp only [a2_J_eq] at hta
  obtain ⟨y21, y22, rfl⟩ := tg_J y2 hta
  simp only [a1_J_eq, a2_J_eq] at h
  have tp := TR5 y1 (J y1 (J y21 y22))
  generalize hp : op y1 (J y1 (J y21 y22)) = p at *
  have s1 := sz_a1 y1; have s2 := sz_a2 y1; have s3 := sz_a1 y21; have s4 := sz_a2 y21
  have s5 := sz_a1 y22; have s6 := sz_a2 y22; have s7 := sz_a1 p; have s8 := sz_a2 p
  rcases TR5 p (J p (J y1 (J y21 y22))) with hf | ⟨-, -, -, hc⟩
  · exact h hf
  have t := TRs (a1 p) p
  rcases hc with ⟨hP, -⟩ | ⟨hP, hg, -⟩ | ⟨hP, hg, -⟩ | ⟨hP, hg1, hg2, -⟩ | ⟨hP, hg, -⟩
  · -- C1: p = a2 y1, p = y22, tg y1 = 2
    obtain ⟨-, -, -, c4, c5, -, c7⟩ := hP
    simp only [a1_J_eq, a2_J_eq] at c4 c5 c7
    rcases tp with hpf | ⟨-, -, -, ⟨hQ, hr⟩ | ⟨hQ, hg2, hr⟩ | ⟨hQ, hg3, hr⟩ | ⟨hQ, hg1, hg2, hr⟩ | ⟨hQ, hg5, hr⟩⟩
    · have := congrArg sz c7; have := congrArg sz hpf; simp only [sz] at *; omega
    · obtain ⟨-, -, -, -, -, q6, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q6 hr
      have := congrArg sz c7; have := congrArg sz hr; have := sz_tg y22 q6; omega
    · simp only [a1_J_eq, a2_J_eq] at hr hg2
      obtain ⟨c, d, rfl⟩ := tg_J y1 c4
      simp only [a1_J_eq, a2_J_eq] at hr c5 hg2
      subst hr; subst c5
      rw [← c7] at hg2
      exact NQ p hg2.symm
    · obtain ⟨-, -, -, q4, -, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q4 hr
      have := congrArg sz c7; have := congrArg sz hr; have := sz_tg y22 q4; omega
    · simp only [a1_J_eq, a2_J_eq] at hr hg1 hg2
      obtain ⟨c, d, rfl⟩ := tg_J y1 c4
      simp only [a1_J_eq, a2_J_eq] at hr c5 hg2
      subst hr; subst c5
      rw [← c7] at hg2
      exact NQ p hg2.symm
    · simp only [a1_J_eq, a2_J_eq] at hr
      have := congrArg sz c7; have := congrArg sz hr; simp only [sz] at *; omega
  · -- C2: tg y1 = 2, p = a2 y1, tg p = 2, guard J y21 y22 = op (a1 p) p
    obtain ⟨-, -, -, c4, c5, c6⟩ := hP
    simp only [a1_J_eq, a2_J_eq] at c4 c5 c6 hg
    have sp := sz_tg p c6
    rcases tp with hpf | ⟨-, -, -, ⟨hQ, hr⟩ | ⟨hQ, hg2, hr⟩ | ⟨hQ, hg3, hr⟩ | ⟨hQ, hq1, hq2, hr⟩ | ⟨hQ, hg5, hr⟩⟩
    · have := congrArg sz c5; have := congrArg sz hpf; simp only [sz] at *; omega
    · obtain ⟨-, -, -, -, -, q6, q7⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q6 q7 hr
      have e1 := sz_tg y22 q6
      have e2 := congrArg sz hr; have e3 := congrArg sz q7
      rcases t with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨-, e4⟩ := M.J.inj hg; have := congrArg sz e4; omega
      · have := congrArg sz hg; simp only [sz] at this; omega
      · rw [hr5] at hg; obtain ⟨-, e4⟩ := M.J.inj hg; have := congrArg sz e4; omega
    · obtain ⟨-, -, -, q4, q5, q6⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q4 q5 q6 hr hg2
      have e1 := sz_tg y21 q4
      have e2 := sz_tg y1 q6
      have e3 := congrArg sz hr; have e4 := congrArg sz q5; have e5 := congrArg sz c5
      rcases t with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨e6, -⟩ := M.J.inj hg; have := congrArg sz e6; omega
      · have := congrArg sz hg; simp only [sz] at this; omega
      · rw [hr5] at hg; obtain ⟨e6, -⟩ := M.J.inj hg; have := congrArg sz e6; omega
    · obtain ⟨-, -, -, q4, q5, q6⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q4 q5 q6 hr hg3
      have e1 := sz_tg y22 q4
      have e2 := congrArg sz hr; have e3 := congrArg sz q5
      rcases t with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨-, e4⟩ := M.J.inj hg; have := congrArg sz e4; omega
      · have := congrArg sz hg; simp only [sz] at this; omega
      · rw [hr5] at hg; obtain ⟨-, e4⟩ := M.J.inj hg; have := congrArg sz e4; omega
    · obtain ⟨-, -, -, q4⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at hr hq1 hq2
      obtain ⟨c, d, rfl⟩ := tg_J y1 q4
      simp only [a1_J_eq, a2_J_eq] at hr c5 hq1 hq2
      subst hr; subst c5
      subst hq1; subst hq2
      rcases t with hgf | ⟨-, -, -, hs | ⟨t4, t5, t6, t7, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨e1, e2⟩ := M.J.inj hg; rw [e2] at e1; have := congrArg sz e1; omega
      · have hsq := congrArg sz hg; simp only [sz] at hsq
        rcases TR5 p (J p p) with hqf | ⟨-, -, -, ⟨hP', -⟩ | ⟨hP', -, -⟩ | ⟨hP', -, -⟩ | ⟨-, he1, -, hr'⟩ | ⟨-, -, hr'⟩⟩
        · rw [hqf] at hsq; simp only [sz] at hsq; omega
        · obtain ⟨-, -, -, -, h5, -, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a1 p); omega
        · obtain ⟨-, -, -, -, h5, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a1 p); omega
        · obtain ⟨-, -, -, -, h5, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a2 p); omega
        · simp only [a1_J_eq, a2_J_eq] at he1
          rw [hr', ← he1] at hg
          have := congrArg sz hg; simp only [sz] at this; omega
        · simp only [a1_J_eq, a2_J_eq] at hr'
          rw [hr'] at hsq; simp only [sz] at hsq; omega
      · rw [hr5] at hg; obtain ⟨e1, e2⟩ := M.J.inj hg
        rcases TR5 p (J p p) with hqf | ⟨-, -, -, ⟨hP', -⟩ | ⟨hP', -, -⟩ | ⟨hP', -, -⟩ | ⟨-, he1, -, -⟩ | ⟨-, -, hr'⟩⟩
        · rw [hqf] at e2; have := congrArg sz e2; simp only [sz] at this; omega
        · obtain ⟨-, -, -, -, h5, -, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a1 p); omega
        · obtain ⟨-, -, -, -, h5, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a1 p); omega
        · obtain ⟨-, -, -, -, h5, -⟩ := hP'
          simp only [a1_J_eq, a2_J_eq] at h5
          have := congrArg sz h5; have := sz_a2 (a2 p); omega
        · simp only [a1_J_eq, a2_J_eq] at he1
          rw [hr5] at he1; have := congrArg sz he1; simp only [sz] at this; omega
        · simp only [a1_J_eq, a2_J_eq] at hr'
          rw [hr'] at e2; have := congrArg sz e2; simp only [sz] at this; omega
    · simp only [a1_J_eq, a2_J_eq] at hr
      have := congrArg sz c5; have := congrArg sz hr; simp only [sz] at *; omega
  · -- C3: tg y22 = 2, p = y22, tg p = 2, guard y1 = op (a1 p) p
    obtain ⟨-, -, -, c4, c5, c6⟩ := hP
    simp only [a1_J_eq, a2_J_eq] at c4 c5 c6 hg
    have sp := sz_tg p c6
    rcases tp with hpf | ⟨-, -, -, ⟨hQ, hr⟩ | ⟨hQ, hg2, hr⟩ | ⟨hQ, hg3, hr⟩ | ⟨hQ, hq1, hq2, hr⟩ | ⟨hQ, hg5, hr⟩⟩
    · have := congrArg sz c5; have := congrArg sz hpf; simp only [sz] at *; omega
    · simp only [a1_J_eq, a2_J_eq] at hr
      have := congrArg sz c5; have := congrArg sz hr; have := sz_tg y22 c4; omega
    · obtain ⟨-, -, -, -, -, q6⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at hr q6
      obtain ⟨c, d, rfl⟩ := tg_J y1 q6
      simp only [a1_J_eq, a2_J_eq] at hr hg
      subst hr
      rcases t with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨e1, -⟩ := M.J.inj hg; have := congrArg sz e1; omega
      · have := congrArg sz hg; simp only [sz] at this; omega
      · rw [hr5] at hg; obtain ⟨e1, -⟩ := M.J.inj hg; have := congrArg sz e1; omega
    · simp only [a1_J_eq, a2_J_eq] at hr
      have := congrArg sz c5; have := congrArg sz hr; have := sz_tg y22 c4; omega
    · obtain ⟨-, -, -, q4⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at hr
      obtain ⟨c, d, rfl⟩ := tg_J y1 q4
      simp only [a1_J_eq, a2_J_eq] at hr hg
      subst hr
      rcases t with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
      · rw [hgf] at hg; obtain ⟨e1, -⟩ := M.J.inj hg; have := congrArg sz e1; omega
      · have := congrArg sz hg; simp only [sz] at this; omega
      · rw [hr5] at hg; obtain ⟨e1, -⟩ := M.J.inj hg; have := congrArg sz e1; omega
    · simp only [a1_J_eq, a2_J_eq] at hr
      have := congrArg sz c5; have := congrArg sz hr; simp only [sz] at *; omega
  · -- C4: tg p = 2, guards y1 = op (a1 p) p = J y21 y22
    obtain ⟨-, -, -, c4⟩ := hP
    simp only [a1_J_eq, a2_J_eq] at hg1 hg2
    have hy : y1 = J y21 y22 := hg1.trans hg2.symm
    subst hy
    rcases tp with hpf | ⟨-, -, -, ⟨hQ, hr⟩ | ⟨hQ, hg2', hr⟩ | ⟨hQ, hg3, hr⟩ | ⟨-, hq1, hq2, hr⟩ | ⟨hQ, hg5, hr⟩⟩
    · rw [hpf] at hg1; simp only [a1_J_eq, a2_J_eq] at hg1
      exact NQ2 (J y21 y22) hg1.symm
    · obtain ⟨-, -, -, -, q5, -, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q5
      have := congrArg sz q5; simp only [sz] at this; omega
    · obtain ⟨-, -, -, -, q5, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q5
      have := congrArg sz q5; simp only [sz] at this; omega
    · obtain ⟨-, -, -, -, q5, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q5
      have := congrArg sz q5; simp only [sz] at this; omega
    · simp only [a1_J_eq, a2_J_eq] at hq1 hq2 hr
      have e : y21 = y22 := hq1.trans hq2.symm
      subst e
      exact NQ y21 hq1.symm
    · obtain ⟨-, -, -, -, q5, -⟩ := hQ
      simp only [a1_J_eq, a2_J_eq] at q5 hg5
      subst q5
      exact NQ y21 hg5.symm
  · -- C5: a1 p = op (a1 Y) Y = p
    obtain ⟨-, -, -, c4, -, -⟩ := hP
    simp only [a1_J_eq, a2_J_eq] at hg
    rw [hp] at hg
    have := congrArg sz hg; have := sz_tg p c4; omega

/-- THE LAW: x = (((y * x) * (y * z)) * y) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (y) (op (y) (op (op (z) (y)) (op (x) (y)))) = x := by
  rcases L1 x y with hA | ⟨hty, hx, hta⟩
  · rcases L1 z y with hB | ⟨hty, hz, hta⟩
    · rw [hA, hB]
      rcases CFF x y z with hC | ⟨hxe, hty, he1, he2, hC⟩
      · have hD : op y (J (J z y) (J x y)) = J y (J (J z y) (J x y)) := by
          apply Dg; intro he; have := congrArg sz he; simp only [a1_J_eq, sz] at this; omega
        rw [hC, hD, op_R1]
      · subst hxe
        obtain ⟨htz, hz1, hq⟩ := TZ hty he1 he2
        have hyq : a1 y = a2 y := he1.trans he2.symm
        have hc : a1 z ≠ y := by
          rw [hz1]; intro he; have := congrArg sz he; have := sz_tg y hty; omega
        rw [hC, Dg hc, op_R5 hty hyq htz hz1 hq]
    · subst hz
      have hD : op y (J (op (a1 y) y) (J x y)) = J y (J (op (a1 y) y) (J x y)) := Dg (NE (a1 y) y)
      rw [hA, CFN hty hta x, hD, op_R3 hty x]
  · rcases L1 z y with hB | ⟨-, hz, -⟩
    · subst hx
      have hD : op y (J (J z y) (op (a1 y) y)) = J y (J (J z y) (op (a1 y) y)) := by
        apply Dg; intro he; have := congrArg sz he; simp only [a1_J_eq, sz] at this; omega
      rw [hB, CNF hty z, hD, op_R2 hty z]
    · subst hx; subst hz
      have hpp : op (op (a1 y) y) (op (a1 y) y) = J (op (a1 y) y) (op (a1 y) y) := by
        by_contra h
        obtain ⟨htp, hu, -⟩ := NF h
        have := congrArg sz hu; have := sz_tg _ htp; omega
      have hD : op y (J (op (a1 y) y) (op (a1 y) y)) = J y (J (op (a1 y) y) (op (a1 y) y)) := Dg (NE (a1 y) y)
      rw [hpp, hD, op_R4 hty]


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
