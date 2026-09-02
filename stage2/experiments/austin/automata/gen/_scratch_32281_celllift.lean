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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ a2 (a1 (a2 (a1 v))) = a2 (a2 (a1 v)) ∧ a2 (a1 (a2 (a1 v))) = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v then op (a1 (a1 (a2 v))) (a2 v) else J u v
  let p2 := if hs2 : msr (p1) (a2 v) < msr u v then op (p1) (a2 v) else J u v
  let p3 := if hs3 : msr (u) (p2) < msr u v then op (u) (p2) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v
  let p5 := if hs5 : msr (p4) (a2 (a2 v)) < msr u v then op (p4) (a2 (a2 v)) else J u v
  let p6 := if hs6 : msr (a1 (a2 v)) (p5) < msr u v then op (a1 (a2 v)) (p5) else J u v
  let p7 := if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v
  let p8 := if hs8 : msr (u) (J (p7) (p5)) < msr u v then op (u) (J (p7) (p5)) else J u v
  let p9 := if hs9 : msr (p8) (a2 v) < msr u v then op (p8) (a2 v) else J u v
  let p10 := if hs10 : msr (p9) (a2 v) < msr u v then op (p9) (a2 v) else J u v
  let p11 := if hs11 : msr (u) (p10) < msr u v then op (u) (p10) else J u v
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ msr (p1) (a2 v) < msr u v ∧ msr (u) (p2) < msr u v ∧ a1 v = p3 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p4) (a2 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (p5) < msr u v ∧ msr (u) (p6) < msr u v ∧ msr (u) (J (p7) (p5)) < msr u v ∧ msr (p8) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ msr (u) (p10) < msr u v ∧ a1 v = p11 then p8
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sA1 {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sA2 {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem mx {a b u v : M} (h : msr a b < msr u v) : max (sz a) (sz b) ≤ max (sz u) (sz v) := by
  apply Classical.byContradiction; intro hc
  have := msr_lt_of_max_lt (a := u) (b := v) (u := a) (v := b) (by omega)
  omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 : M,
    p1 = (if hs1 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v then op (a1 (a1 (a2 v))) (a2 v) else J u v) ∧
    p2 = (if hs2 : msr (p1) (a2 v) < msr u v then op (p1) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (u) (p2) < msr u v then op (u) (p2) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v) ∧
    p5 = (if hs5 : msr (p4) (a2 (a2 v)) < msr u v then op (p4) (a2 (a2 v)) else J u v) ∧
    p6 = (if hs6 : msr (a1 (a2 v)) (p5) < msr u v then op (a1 (a2 v)) (p5) else J u v) ∧
    p7 = (if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v) ∧
    p8 = (if hs8 : msr (u) (J (p7) (p5)) < msr u v then op (u) (J (p7) (p5)) else J u v) ∧
    p9 = (if hs9 : msr (p8) (a2 v) < msr u v then op (p8) (a2 v) else J u v) ∧
    p10 = (if hs10 : msr (p9) (a2 v) < msr u v then op (p9) (a2 v) else J u v) ∧
    p11 = (if hs11 : msr (u) (p10) < msr u v then op (u) (p10) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ msr (p1) (a2 v) < msr u v ∧ msr (u) (p2) < msr u v ∧ a1 v = p3 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p4) (a2 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (p5) < msr u v ∧ msr (u) (p6) < msr u v ∧ msr (u) (J (p7) (p5)) < msr u v ∧ msr (p8) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ msr (u) (p10) < msr u v ∧ a1 v = p11 then p8
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the full one-unfold digest: free, or R1, or R2 (with its gate), or R3 (recursive, with its gate) -/
theorem TR (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a1 (a2 (a1 v)))) ∨
    (tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ op u v = a1 (a1 (a2 v)) ∧
      msr u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v)) < msr u v ∧
      a1 v = op u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))) ∨
    (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q ∧
      msr u (op (op (op u q) (a2 v)) (a2 v)) < msr u v ∧
      a1 v = op u (op (op (op u q) (a2 v)) (a2 v))) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h
      obtain ⟨h2, g1, g2, g3, he⟩ := h
      rw [dif_pos g1] at hp1; subst hp1
      rw [dif_pos g2] at hp2; subst hp2
      rw [dif_pos g3] at hp3; subst hp3
      exact Or.inr (Or.inr (Or.inl ⟨h2.1, h2.2.1, h2.2.2, rfl, g3, he⟩))
    · split
      · rename_i h
        obtain ⟨h3, g1, g2, g3, g4, g5, g6, g7, g8, he⟩ := h
        rw [dif_pos g1] at hp4; subst hp4
        rw [dif_pos g2] at hp5; subst hp5
        rw [dif_pos g3] at hp6; subst hp6
        rw [dif_pos g4] at hp7; subst hp7
        rw [dif_pos g5] at hp8; subst hp8
        rw [dif_pos g6] at hp9; subst hp9
        rw [dif_pos g7] at hp10; subst hp10
        rw [dif_pos g8] at hp11; subst hp11
        exact Or.inr (Or.inr (Or.inr ⟨h3.1, _, g5, rfl, g8, he⟩))
      · exact Or.inl rfl

theorem SUn (n : Nat) : ∀ u v : M, msr u v < n → op u v ≠ J u v → sz u < sz v := by
  induction n with
  | zero => intro u v h; omega
  | succ n ih =>
    intro u v hn hne
    have key : ∀ q : M, tg v = 2 → msr u q < msr u v → a1 v = op u q → sz u < sz v := by
      intro q h1 hg he
      have hv := sA1 h1
      have hm := mx hg
      by_cases hf : op u q = J u q
      · rw [hf] at he; have := congrArg sz he; simp only [sz] at this; omega
      · have := ih u q (by omega) hf; omega
    rcases TR u v with h | ⟨h1, -⟩ | ⟨h1, -, -, -, hg, he⟩ | ⟨h1, q, -, -, hg, he⟩
    · exact absurd h hne
    · have e1 := sz_a1 (a1 v); have e2 := sA1 h1.1; rw [h1.2.2.1]; omega
    · exact key _ h1 hg he
    · exact key _ h1 hg he

theorem SU {u v : M} (h : op u v ≠ J u v) : sz u < sz v := SUn (msr u v + 1) u v (Nat.lt_succ_self _) h

theorem Wf {u v : M} (h : sz v ≤ sz u) : op u v = J u v := by
  apply Classical.byContradiction; intro hc; have := SU hc; omega

theorem oR1 {u v : M} (h : P1 u v) : op u v = a1 (a1 (a2 (a1 v))) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, -, -, -, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  rw [hop, if_pos h]

/-- the result-size bound.  No induction: the recursive rule's own second gate
    `msr u (op (op (op u q) (a2 v)) (a2 v)) < msr u v` already bounds its result. -/
theorem RS (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  by_cases hne : op u v = J u v
  · exact Or.inl hne
  · right
    have hu := SU hne
    rcases TR u v with h | ⟨h1, he⟩ | ⟨h1, -, -, he, -, -⟩ | ⟨h1, q, -, he, hg, -⟩
    · exact absurd h hne
    · rw [he]
      have := sz_a1 (a1 (a2 (a1 v))); have := sz_a1 (a2 (a1 v)); have := sz_a2 (a1 v); have := sA1 h1.1
      omega
    · rw [he]
      have := sz_a1 (a1 (a2 v)); have := sz_a1 (a2 v); have := sA2 h1
      omega
    · rw [← he] at hg
      have hw := sA2 h1
      have hm := mx hg
      by_cases hy : op (op u v) (a2 v) = J (op u v) (a2 v)
      · by_cases hx : op (J (op u v) (a2 v)) (a2 v) = J (J (op u v) (a2 v)) (a2 v)
        · rw [hy, hx] at hm; simp only [sz] at hm; omega
        · have := SU hx; simp only [sz] at this; omega
      · have := SU hy; omega

/-- `op` has no fixed point in its right argument -/
theorem NFX {u v : M} (h : op u v = v) : False := by
  rcases RS u v with hf | hs
  · rw [hf] at h; have := congrArg sz h; simp only [sz] at this; have := sz_pos u; omega
  · rw [h] at hs; exact Nat.lt_irrefl _ hs

/-- the uniform guard.  A decoded product either fires R1 (which pins `u` structurally) or
    leaves `a1 v = op u C` with `C = op (op (op u v) (a2 v)) (a2 v)` — a `C` that depends only
    on `v` and on the *result*, hence the same `C` for every `u` with the same result. -/
theorem GG {u v : M} (h : op u v ≠ J u v) : (P1 u v ∧ op u v = a1 (a1 (a2 (a1 v)))) ∨
    (a1 v = op u (op (op (op u v) (a2 v)) (a2 v)) ∧
      msr u (op (op (op u v) (a2 v)) (a2 v)) < msr u v) := by
  rcases TR u v with h0 | h1 | ⟨-, -, -, hr, hg, he⟩ | ⟨-, q, -, hr, hg, he⟩
  · exact absurd h0 h
  · exact Or.inl h1
  · rw [← hr] at hg he; exact Or.inr ⟨he, hg⟩
  · rw [← hr] at hg he; exact Or.inr ⟨he, hg⟩

/-- R1 at `(u,v)` against R2/R3 at `(u',v)` with the same result.  `P1` pins
    `sz (a1 v) = sz u + sz (op u v) + 2*sz (a2 v) + 3`, while the other rule's guard argument is
    at most `sz (op u v) + 2*sz (a2 v) + 2`, so the guard cannot be decoded and is `J u' C`. -/
theorem MX2 {u u' v : M} (q1 : P1 u v) (q2 : op u v = a1 (a1 (a2 (a1 v))))
    (e : a1 v = op u' (op (op (op u v) (a2 v)) (a2 v))) : u = u' := by
  by_cases hf : op u' (op (op (op u v) (a2 v)) (a2 v)) = J u' (op (op (op u v) (a2 v)) (a2 v))
  · rw [hf] at e
    have h3 := q1.2.2.1
    rw [e] at h3; simpa using h3
  · exfalso
    have hs := (RS u' (op (op (op u v) (a2 v)) (a2 v))).resolve_left hf
    rw [← e] at hs
    obtain ⟨-, t2, t3, t4, t5, t6, t7⟩ := q1
    have s1 := sz_tg _ t2
    have s2 := sz_tg _ t4
    have s3 := sz_tg _ t5
    have c3 := congrArg sz t3
    have c6 := congrArg sz t6
    have c7 := congrArg sz t7
    have c2 := congrArg sz q2
    have hb : sz (op (op (op u v) (a2 v)) (a2 v)) ≤ sz (op u v) + sz (a2 v) + sz (a2 v) + 2 := by
      rcases RS (op (op u v) (a2 v)) (a2 v) with k | k
      · rcases RS (op u v) (a2 v) with k2 | k2
        · rw [k, k2]; simp only [sz]; omega
        · rw [k]; simp only [sz]; omega
      · omega
    have := sz_pos u
    omega

/-- **`op` is injective in its first argument.**  Induction on `sz v`: two free products agree only
    if `u = u'`; free against decoded is refuted by `RS`; two R1s pin both to `a1 (a1 v)`; R1 against
    R2/R3 is `MX2`; and two R2/R3 guards read the *same* `C` (it is a function of `v` and the shared
    result), so `op u C = a1 v = op u' C` and the gate `msr u C < msr u v` gives `sz C < sz v`. -/
theorem INJn (n : Nat) : ∀ v u u' : M, sz v < n → op u v = op u' v → u = u' := by
  induction n with
  | zero => intro v u u' h; omega
  | succ n ih =>
    intro v u u' hn he
    by_cases h1 : op u v = J u v
    · by_cases h2 : op u' v = J u' v
      · have hz := congrArg a1 he; rw [h1, h2] at hz; simpa using hz
      · exfalso
        have hs := (RS u' v).resolve_left h2
        rw [← he, h1] at hs; simp only [sz] at hs; omega
    · by_cases h2 : op u' v = J u' v
      · exfalso
        have hs := (RS u v).resolve_left h1
        rw [he, h2] at hs; simp only [sz] at hs; omega
      · rcases GG h1 with ⟨q1, q2⟩ | ⟨e, g⟩
        · rcases GG h2 with ⟨r1, -⟩ | ⟨e', -⟩
          · rw [q1.2.2.1, r1.2.2.1]
          · rw [← he] at e'; exact MX2 q1 q2 e'
        · rcases GG h2 with ⟨r1, r2⟩ | ⟨e', -⟩
          · exact (MX2 r1 r2 (by rw [← he]; exact e)).symm
          · rw [← he] at e'
            have hsu := SU h1
            have hm := mx g
            have hmax : max (sz u) (sz v) = sz v := Nat.max_eq_right (Nat.le_of_lt hsu)
            have hle : sz (op (op (op u v) (a2 v)) (a2 v)) ≤ sz v := by
              have hz := Nat.le_trans (Nat.le_max_right (sz u)
                (sz (op (op (op u v) (a2 v)) (a2 v)))) hm
              rw [hmax] at hz; exact hz
            have hlt : sz (op (op (op u v) (a2 v)) (a2 v)) < sz v := by
              apply Classical.byContradiction; intro hc
              have heq : sz (op (op (op u v) (a2 v)) (a2 v)) = sz v := by omega
              simp only [msr] at g; rw [heq] at g; exact Nat.lt_irrefl _ g
            exact ih _ u u' (by omega) (e.symm.trans e')

theorem INJ {u u' v : M} (h : op u v = op u' v) : u = u' :=
  INJn (sz v + 1) v u u' (Nat.lt_succ_self _) h

/-- Every common guard retained by `GG`/`GDx` is a strict descent in its
    right parameter.  This is the fuel fact needed by the conditional cell. -/
theorem GLT {u v C : M} (h : op u v ≠ J u v)
    (hg : msr u C < msr u v) : sz C < sz v := by
  have hu := SU h
  have hm := mx hg
  have hmax : max (sz u) (sz v) = sz v := Nat.max_eq_right (Nat.le_of_lt hu)
  have hle : sz C ≤ sz v := by
    have hz := Nat.le_trans (Nat.le_max_right (sz u) (sz C)) hm
    rw [hmax] at hz
    exact hz
  apply Classical.byContradiction
  intro hn
  have he : sz C = sz v := by omega
  simp only [msr] at hg
  rw [he] at hg
  exact Nat.lt_irrefl _ hg

/-- **HOLE 1**: the third chain product `A = op z (op (op x y) y)` is always free.
    Census evidence: free in every one of 139,482 chained-encoding triples and every attack round. -/
theorem AF (x y z : M) : op z (op (op x y) y) = J z (op (op x y) y) := by
  rcases TR z (op (op x y) y) with h | ⟨h1, -⟩ | ⟨-, -, -, -, -, he⟩ | ⟨-, q, -, -, -, he⟩
  · exact h
  · exfalso
    obtain ⟨-, -, -, h4, -, -, h7⟩ := h1
    rcases RS (op x y) y with hQ | hQ
    · rw [hQ] at h4 h7; simp only [a1_J_eq, a2_J_eq] at h4 h7
      rcases RS x y with hp | hp
      · rw [hp] at h4 h7; simp only [a1_J_eq, a2_J_eq] at h4 h7
        have := sA1 h4; have := sz_a2 (a1 y); have := congrArg sz h7; omega
      · have := sz_a2 (op x y); have := sz_a1 (a2 (op x y)); have := sz_a2 (a1 (a2 (op x y)))
        have := congrArg sz h7; omega
    · sorry
  · exfalso
    /- R2 at (z,Q): `a1 Q = op z (op (op (a1 (a1 (a2 Q))) (a2 Q)) (a2 Q))`.  Split `RS (op x y) y` first
       (that makes `a1 Q = op x y` and `a2 Q = y` concrete); then `RS z m` free gives `x = z /\ y = m`,
       killed by `NFX`.  The residue is `op z m` decoded. -/
    sorry
  · exfalso
    /- R3(rec) at (z,Q): same shape with `op z q` in place of `a1 (a1 (a2 Q))`. -/
    sorry

/-- the collapse `x = J z Q` and `op x y = J z Q` force `x = J z x`. -/
theorem SFc {x y z : M} (hxx : x = J z (op (op x y) y))
    (hop : op x y = J z (op (op x y) y)) : False := by
  have hox : op x y = x := hop.trans hxx.symm
  rw [hox, hox] at hxx
  have := congrArg sz hxx
  simp only [sz] at this
  have := sz_pos z; omega

/-- the shared collapse: once `op x y = J z Q` the chain closes.  Used by all three `SFa` branches. -/
theorem SFb {x y z : M} (hQ : sz (op (op x y) y) < sz y)
    (hA : a1 (a1 y) = J z (op (op x y) y)) (hop : op x y = J z (op (op x y) y)) : False := by
  rcases RS x y with hf | hf
  · rw [hf] at hop hQ
    have e4 := congrArg a2 hop
    simp only [a2_J_eq] at e4
    rw [← e4] at hQ; omega
  · rcases TR x y with h2 | ⟨g2, -⟩ | ⟨-, -, -, -, -, gg⟩ | ⟨-, q2, -, -, -, gg⟩
    · have := congrArg sz h2
      simp only [sz] at this
      have := sz_pos x; omega
    · exact SFc (g2.2.2.1.trans hA) hop
    · rcases RS x (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf2 | hf2
      · rw [hf2] at gg
        have hb := congrArg a1 gg
        simp only [a1_J_eq] at hb
        exact SFc (hb.symm.trans hA) hop
      · sorry
    · rcases RS x (op (op (op x q2) (a2 y)) (a2 y)) with hf2 | hf2
      · rw [hf2] at gg
        have hb := congrArg a1 gg
        simp only [a1_J_eq] at hb
        exact SFc (hb.symm.trans hA) hop
      · sorry

/-- shared contradiction for `SF`: `A = J z Q` cannot sit at the decoder slot `a1 (a1 y)`. -/
theorem SFa {x y z : M} (ht : tg y = 2) (hA : a1 (a1 y) = J z (op (op x y) y)) : False := by
  have e1 : sz (a1 (a1 y)) < sz y := by have := sz_a1 (a1 y); have := sA1 ht; omega
  have e2 := congrArg sz hA
  simp only [sz] at e2
  rcases RS (op x y) y with hQ | hQ
  · have e3 := congrArg sz hQ
    simp only [sz] at e3
    have := sz_pos (op x y); have := sz_pos z; omega
  · rcases TR (op x y) y with h | ⟨g1, -⟩ | ⟨-, -, -, -, -, gg⟩ | ⟨-, q, -, -, -, gg⟩
    · have e3 := congrArg sz h
      simp only [sz] at e3
      have := sz_pos (op x y); have := sz_pos z; omega
    · exact SFb hQ hA (g1.2.2.1.trans hA)
    · rcases RS (op x y) (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf | hf
      · rw [hf] at gg
        have hb := congrArg a1 gg
        simp only [a1_J_eq] at hb
        exact SFb hQ hA (hb.symm.trans hA)
      · sorry
    · rcases RS (op x y) (op (op (op (op x y) q) (a2 y)) (a2 y)) with hf | hf
      · rw [hf] at gg
        have hb := congrArg a1 gg
        simp only [a1_J_eq] at hb
        exact SFb hQ hA (hb.symm.trans hA)
      · sorry

/-- **HOLE 2**: the fourth chain product `S = op A y` is always free (same census evidence). -/
theorem SF (x y z : M) : op (J z (op (op x y) y)) y = J (J z (op (op x y) y)) y := by
  rcases TR (J z (op (op x y) y)) y with h | ⟨h1, -⟩ | ⟨h1, -, -, -, -, he⟩ | ⟨h1, q, -, -, -, he⟩
  · exact h
  · exact (SFa h1.1 h1.2.2.1.symm).elim
  · exfalso
    rcases RS (J z (op (op x y) y)) (op (op (a1 (a1 (a2 y))) (a2 y)) (a2 y)) with hf | hf
    · rw [hf] at he
      have h' := congrArg a1 he
      simp only [a1_J_eq] at h'
      exact SFa h1 h'
    · sorry
  · exfalso
    rcases RS (J z (op (op x y) y))
      (op (op (op (J z (op (op x y) y)) q) (a2 y)) (a2 y)) with hf | hf
    · rw [hf] at he
      have h' := congrArg a1 he
      simp only [a1_J_eq] at h'
      exact SFa h1 h'
    · sorry

theorem mxl {a b c d : M} (h1 : sz a < sz d) (h2 : sz b < sz d) :
    max (sz a) (sz b) < max (sz c) (sz d) := by
  rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega

theorem oR2 {u v : M} (h1 : ¬ P1 u v) (h2 : P2 u v)
    (g1 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v)
    (g2 : msr (op (a1 (a1 (a2 v))) (a2 v)) (a2 v) < msr u v)
    (g3 : msr u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v)) < msr u v)
    (he : a1 v = op u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))) : op u v = a1 (a1 (a2 v)) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, hp1, hp2, hp3, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  rw [dif_pos g1] at hp1; subst hp1
  rw [dif_pos g2] at hp2; subst hp2
  rw [dif_pos g3] at hp3; subst hp3
  rw [hop, if_neg h1, if_pos ⟨h2, g1, g2, g3, he⟩]

/-- the top product when `P = op x y` decoded, `x` sits at `a1 (a1 y)`, and `A` is free. -/
theorem TOP {x y z : M} (hy : tg y = 2) (hay : tg (a1 y) = 2) (hx : a1 (a1 y) = x)
    (hPs : sz (op x y) < sz y) (hQ : sz (a2 (a1 (op (op x y) y))) < sz y)
    (hAf : op z (op (op x y) y) = J z (op (op x y) y)) :
    op z (J (J z (op (op x y) y)) y) = x := by
  have hxy : sz x ≤ sz y := by
    rw [← hx]; have := sz_a1 (a1 y); have := sz_a1 y; omega
  have hs : sz (J (J z (op (op x y) y)) y) = sz z + sz (op (op x y) y) + sz y + 2 := by
    simp only [sz]; omega
  have g1 : msr (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)) <
      msr z (J (J z (op (op x y) y)) y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by omega) (by omega))
  have g2 : msr (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
      (a2 (J (J z (op (op x y) y)) y)) < msr z (J (J z (op (op x y) y)) y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by omega) (by omega))
  have g3 : msr z (op (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
      (a2 (J (J z (op (op x y) y)) y))) < msr z (J (J z (op (op x y) y)) y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by have := sz_pos y; have := sz_pos (op (op x y) y); omega)
      (by have := sz_pos y; have := sz_pos z; omega))
  have hn : ¬ P1 z (J (J z (op (op x y) y)) y) := by
    intro h
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h7
    have := congrArg sz h7; omega
  have hg : a1 (J (J z (op (op x y) y)) y) =
      op z (op (op (a1 (a1 (a2 (J (J z (op (op x y) y)) y)))) (a2 (J (J z (op (op x y) y)) y)))
        (a2 (J (J z (op (op x y) y)) y))) := by
    simp only [a1_J_eq, a2_J_eq, hx]; exact hAf.symm
  have hr := oR2 (u := z) (v := J (J z (op (op x y) y)) y) hn ⟨rfl, hy, hay⟩ g1 g2 g3 hg
  rw [hr]; simp only [a2_J_eq, hx]

/-- the decoded trichotomy at `(u,v)`: R1's structural reading, the free-guard reading (which is
    exactly what `TOP` needs), or the level-2 cell where the guard product is itself decoded. -/
theorem GD {u v : M} (h : op u v ≠ J u v) : P1 u v ∨
    (tg v = 2 ∧ tg (a1 v) = 2 ∧ a1 (a1 v) = u) ∨
    (tg v = 2 ∧ ∃ C, a1 v = op u C ∧ op u C ≠ J u C) := by
  have k : ∀ C : M, a1 v = op u C →
      (tg (a1 v) = 2 ∧ a1 (a1 v) = u) ∨ (∃ C, a1 v = op u C ∧ op u C ≠ J u C) := by
    intro C he
    by_cases hf : op u C = J u C
    · rw [hf] at he; exact Or.inl ⟨by rw [he]; rfl, by rw [he]; rfl⟩
    · exact Or.inr ⟨C, he, hf⟩
  rcases TR u v with h0 | ⟨h1, -⟩ | ⟨h1, -, -, -, -, he⟩ | ⟨h1, q, -, -, -, he⟩
  · exact absurd h0 h
  · exact Or.inl h1
  · rcases k _ he with hl | hr
    · exact Or.inr (Or.inl ⟨h1, hl.1, hl.2⟩)
    · exact Or.inr (Or.inr ⟨h1, hr⟩)
  · rcases k _ he with hl | hr
    · exact Or.inr (Or.inl ⟨h1, hl.1, hl.2⟩)
    · exact Or.inr (Or.inr ⟨h1, hr⟩)

/-- The decoded trichotomy with the exact producer retained in its recursive
    cell.  Unlike `GD`, the last disjunct remembers whether `(u,v)` was read by
    R2 or by the recursive R3 rule, as well as the common guard product. -/
theorem GDx {u v : M} (h : op u v ≠ J u v) : P1 u v ∨
    (tg v = 2 ∧ tg (a1 v) = 2 ∧ a1 (a1 v) = u) ∨
    (∃ C, C = op (op (op u v) (a2 v)) (a2 v) ∧
      ((tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧
          op u v = a1 (a1 (a2 v))) ∨
        (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q)) ∧
      msr u C < msr u v ∧ a1 v = op u C ∧ op u C ≠ J u C) := by
  have k : ∀ C : M, C = op (op (op u v) (a2 v)) (a2 v) →
      ((tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧
          op u v = a1 (a1 (a2 v))) ∨
        (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q)) →
      msr u C < msr u v → a1 v = op u C →
      (tg v = 2 ∧ tg (a1 v) = 2 ∧ a1 (a1 v) = u) ∨
      (∃ C, C = op (op (op u v) (a2 v)) (a2 v) ∧
        ((tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧
            op u v = a1 (a1 (a2 v))) ∨
          (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q)) ∧
        msr u C < msr u v ∧ a1 v = op u C ∧ op u C ≠ J u C) := by
    intro C hc hp hg he
    by_cases hf : op u C = J u C
    · rw [hf] at he
      exact Or.inl ⟨hp.elim And.left And.left, by rw [he]; rfl, by rw [he]; rfl⟩
    · exact Or.inr ⟨C, hc, hp, hg, he, hf⟩
  rcases TR u v with h0 | ⟨h1, -⟩ | ⟨h1, h2, h3, hr, hg, he⟩ |
      ⟨h1, q, hq, hr, hg, he⟩
  · exact absurd h0 h
  · exact Or.inl h1
  · rw [← hr] at hg he
    rcases k _ rfl (Or.inl ⟨h1, h2, h3, hr⟩) hg he with hl | ht
    · exact Or.inr (Or.inl hl)
    · exact Or.inr (Or.inr ht)
  · rw [← hr] at hg he
    rcases k _ rfl (Or.inr ⟨h1, q, hq, hr⟩) hg he with hl | ht
    · exact Or.inr (Or.inl hl)
    · exact Or.inr (Or.inr ht)

/-- Size content of the recursive `GDx` cell: both the decoder and the decoded
    guard result lie below the guard parameter, which itself lies below `v`. -/
theorem CellSz {u v C : M} (h : op u v ≠ J u v)
    (hg : msr u C < msr u v) (he : a1 v = op u C)
    (hd : op u C ≠ J u C) :
    sz u < sz C ∧ sz (a1 v) < sz C ∧ sz C < sz v := by
  refine ⟨SU hd, ?_, GLT h hg⟩
  rw [he]
  exact (RS u C).resolve_left hd

theorem CellLift {x y C : M} (hg : msr x C < msr x y)
    (he : a1 y = op x C) (hd : op x C ≠ J x C) :
    exists b, y = J (op x C) b /\ sz x < sz C /\
      sz (a1 y) < sz C /\ sz C < sz y /\ sz b < sz y := by
  have hxc := SU hd
  have hac : sz (a1 y) < sz C := by rw [he]; exact (RS x C).resolve_left hd
  have hcy : sz C < sz y := by
    apply Classical.byContradiction; intro hn
    have hyc : sz y <= sz C := by omega
    have hm1 : max (sz x) (sz C) = sz C := Nat.max_eq_right (Nat.le_of_lt hxc)
    have hm2 : max (sz x) (sz y) <= sz C :=
      (Nat.max_le).2 ⟨Nat.le_trans (Nat.le_of_lt hxc) (Nat.le_refl _), hyc⟩
    have hm3 := Nat.mul_le_mul hm2 hm2
    simp only [msr, hm1] at hg
    omega
  have hty : tg y = 2 := by
    apply Classical.byContradiction
    intro hn
    obtain ⟨n, rfl⟩ := tg_g y hn
    simp only [a1_g_eq] at hac
    omega
  obtain ⟨a,b,rfl⟩ := tg_J y hty
  simp only [a1_J_eq] at he hac
  subst a
  refine ⟨b, rfl, hxc, hac, hcy, ?_⟩
  exact sA2 (t := J (op x C) b) rfl

/-- In a normalized cell, the parent product cannot be free. -/
theorem LiftParentDecoded {x y C P b : M}
    (hy : y = J (op x C) b) (hc : C = op (op P b) b)
    (hp : op x y = P) (hg : msr x C < msr x y)
    (hd : op x C ≠ J x C) : op x y ≠ J x y := by
  intro hf
  have he : a1 y = op x C := by rw [hy]; rfl
  obtain ⟨b', hy', hxc, hac, hcy, hb'⟩ := CellLift hg he hd
  have hby : sz b < sz y := by
    rw [hy]
    exact sA2 (t := J (op x C) b) rfl
  have eP : P = J x y := hp.symm.trans hf
  have hPb : op P b = J P b := by
    apply Wf
    have ePs := congrArg sz eP
    simp only [sz] at ePs
    omega
  have hPPb : op (op P b) b = J (op P b) b := by
    apply Wf
    rw [hPb]
    simp only [sz]
    omega
  have ecs := congrArg sz hc
  rw [hPPb, hPb] at ecs
  simp only [sz] at ecs
  have ePs := congrArg sz eP
  simp only [sz] at ePs
  omega

/-- One exact recursive step from a decoded guard.  The final disjunct is a
    normalized cell for the strictly smaller right parameter `C'`. -/
theorem CellStep {x C : M} (hd : op x C ≠ J x C) :
    P1 x C ∨
    (tg C = 2 ∧ tg (a1 C) = 2 ∧ a1 (a1 C) = x) ∨
    (∃ C', C' = op (op (op x C) (a2 C)) (a2 C) ∧
      ((tg C = 2 ∧ tg (a2 C) = 2 ∧ tg (a1 (a2 C)) = 2 ∧
          op x C = a1 (a1 (a2 C))) ∨
        (tg C = 2 ∧ ∃ q, msr x q < msr x C ∧ op x C = op x q)) ∧
      msr x C' < msr x C ∧ C = J (op x C') (a2 C) ∧
      op x C' ≠ J x C' ∧ sz x < sz C' ∧
      sz (a1 C) < sz C' ∧ sz C' < sz C) := by
  rcases GDx hd with h1 | hs | ⟨C', hc, hp, hg, he, hdec⟩
  · exact Or.inl h1
  · exact Or.inr (Or.inl hs)
  · right
    right
    have ht : tg C = 2 := hp.elim And.left And.left
    have hshape : C = J (op x C') (a2 C) := by
      obtain ⟨a, b, rfl⟩ := tg_J C ht
      simp only [a1_J_eq, a2_J_eq] at he ⊢
      rw [he]
    obtain ⟨hxc, hac, hcC⟩ := CellSz hd hg he hdec
    exact ⟨C', hc, hp, hg, hshape, hdec, hxc, hac, hcC⟩

theorem Jeta {t : M} (h : tg t = 2) : t = J (a1 t) (a2 t) := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h
  rfl

/-- Accessor-free decoding digest. -/
theorem UD {u v : M} (h : op u v ≠ J u v) :
    tg v = 2 ∧ (a1 v = J u (J (J (op u v) (a2 v)) (a2 v)) ∨
      a1 v = op u (op (op (op u v) (a2 v)) (a2 v))) := by
  rcases TR u v with h0 | ⟨h1, he⟩ | ⟨h1, -, -, he, -, hg⟩ |
      ⟨h1, q, -, he, -, hg⟩
  · exact absurd h0 h
  · obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    refine ⟨t1, Or.inl ?_⟩
    have e5 : a1 (a2 (a1 v)) = J (op u v) (a2 v) := by
      rw [Jeta t5, ← he, t7]
    have e4 : a2 (a1 v) = J (J (op u v) (a2 v)) (a2 v) := by
      rw [Jeta t4, e5, ← t6, t7]
    rw [Jeta t2, ← t3, e4]
  · exact ⟨h1, Or.inr (by rw [he]; exact hg)⟩
  · exact ⟨h1, Or.inr (by rw [he]; exact hg)⟩

/-- Exact encoding split for one decoded cell: literal/R1 encoding,
    op-built encoding with a free guard, or a strictly smaller decoded guard. -/
theorem CellStepU {x C : M} (hd : op x C ≠ J x C) :
    let D := op x C
    let c := a2 C
    let C' := op (op D c) c
    C = J (J x (J (J D c) c)) c ∨
      (C = J (J x C') c ∧ op x C' = J x C') ∨
      (C = J (op x C') c ∧ op x C' ≠ J x C' ∧
        msr x C' < msr x C ∧ sz C' < sz C) := by
  dsimp only
  have htC : tg C = 2 := by
    apply Classical.byContradiction
    intro hn
    obtain ⟨k, rfl⟩ := tg_g C hn
    have hs := SU hd
    have hp := sz_pos x
    simp only [sz] at hs
    omega
  rcases GG hd with ⟨h1, he⟩ | ⟨he, hg⟩
  · left
    obtain ⟨t1, t2, t3, t4, t5, t6, t7⟩ := h1
    have e5 : a1 (a2 (a1 C)) = J (op x C) (a2 C) := by
      rw [Jeta t5, ← he, t7]
    have e4 : a2 (a1 C) = J (J (op x C) (a2 C)) (a2 C) := by
      rw [Jeta t4, e5, ← t6, t7]
    have ea : a1 C = J x (J (J (op x C) (a2 C)) (a2 C)) := by
      rw [Jeta t2, ← t3, e4]
    exact (Jeta t1).trans (congrArg (fun q => J q (a2 C)) ea)
  · by_cases hf : op x (op (op (op x C) (a2 C)) (a2 C)) =
        J x (op (op (op x C) (a2 C)) (a2 C))
    · right
      left
      refine ⟨?_, hf⟩
      exact (Jeta htC).trans
        (congrArg (fun q => J q (a2 C)) (he.trans hf))
    · right
      right
      refine ⟨?_, hf, hg, GLT hd hg⟩
      exact (Jeta htC).trans (congrArg (fun q => J q (a2 C)) he)

theorem LiftTailn (n : Nat) : ∀ x P b z C D Y : M,
    sz Y < n → C = op (op P b) b → D = op x C →
    Y = J D b → op x Y = P → msr x C < msr x Y →
    op x C ≠ J x C → op z (op P Y) = J z (op P Y) := by
  induction n with
  | zero => intro x P b z C D Y hn; omega
  | succ n ih =>
    intro x P b z C D Y hn hC hD hY hP hg hd
    have he : a1 Y = op x C := by rw [hY, hD]; rfl
    obtain ⟨b', hY', hxc, hac, hcy, hb'⟩ := CellLift hg he hd
    have hpdec : op x Y ≠ J x Y :=
      LiftParentDecoded (by rw [hY, hD]) hC hP hg hd
    have hPs := (RS x Y).resolve_left hpdec
    rcases CellStepU hd with hc1 | ⟨hc2, hf'⟩ |
        ⟨hc3, hd', hg', hcC⟩
    · sorry
    · sorry
    · let C' := op (op (op x C) (a2 C)) (a2 C)
      have hC' : C' = op (op D (a2 C)) (a2 C) := by
        dsimp only [C']
        rw [← hD]
      have hshape : C = J (op x C') (a2 C) := by exact hc3
      have hlo : ∀ z : M, op z (op D C) = J z (op D C) := by
        intro z'
        exact ih x D (a2 C) z' C' (op x C') C (by omega)
          hC' rfl hshape hD.symm hg' hd'
      sorry

theorem law (x y z : M) : op (z) (op (op (z) (op (op (x) (y)) (y))) (y)) = x := by
  rw [AF x y z, SF x y z]
  by_cases hP : op x y = J x y
  · rw [hP, Wf (u := J x y) (v := y) (by simp only [sz]; have := sz_pos x; omega)]
    exact oR1 ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  · have hPs := (RS x y).resolve_left hP
    have hQ : sz (a2 (a1 (op (op x y) y))) < sz y := by
      rcases RS (op x y) y with h | h
      · rw [h]; simp only [a1_J_eq]; have := sz_a2 (op x y); omega
      · have := sz_a1 (op (op x y) y); have := sz_a2 (a1 (op (op x y) y)); omega
    rcases GD hP with hp | hk | ⟨hy, C, he, hf⟩
    · exact TOP hp.1 hp.2.1 hp.2.2.1.symm hPs hQ (AF x y z)
    · exact TOP hk.1 hk.2.1 hk.2.2 hPs hQ (AF x y z)
    · /- **HOLE 3**, now exact: the level-2 cell.  `a1 y = op x C` with `op x C` itself DECODED, so
         `a1 (a1 y) ≠ x` and R2 cannot answer the top product — R3 must.  See NOTES_32281.md
         SESSION 4 for the full reduction (R3's `p5` is `C` on the nose, `p8 = x` is the law at the
         strictly smaller parameter `C`, and the two open items are the `p6`/`J p7 p5` size gates). -/
      sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
