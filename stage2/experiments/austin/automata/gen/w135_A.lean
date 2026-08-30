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

/- `AF (x y z) : op z (op (op x y) y) = J z (op (op x y) y)` was HOLE 1.  It is FALSE and was
   deleted; `AFbad` in NOTES_32281 refutes it in the kernel.  Its true restriction is `Afree`
   below, which is all the free branch of `law` ever needed. -/

/-- the shared residue of `Afree`: a decoded `op z (op (op c y) y)` is never `J a y`.
    Fuel induction on the R3 gate — every branch dies by size or by `NFX`, and the R3 guard with
    `op c y` free is the same statement one gate down. -/
theorem AFn (n : Nat) : ∀ z c y a : M, msr z (op (op c y) y) < n →
    op z (op (op c y) y) = J a y → False := by
  induction n with
  | zero => intro z c y a h _; omega
  | succ n ih =>
    intro z c y a hn he
    have hd : op z (op (op c y) y) ≠ J z (op (op c y) y) := by
      intro hf
      have h1 := congrArg a2 (hf.symm.trans he)
      simp only [a2_J_eq] at h1
      exact NFX h1
    have hsz := (RS z (op (op c y) y)).resolve_left hd
    rw [he] at hsz
    simp only [sz] at hsz
    rcases RS (op c y) y with hC | hC
    · rw [hC] at hsz he hd hn
      simp only [sz] at hsz
      rcases RS c y with hK | hK
      · rw [hK] at he hd hn
        rcases TR z (J (J c y) y) with h | ⟨h1, -⟩ | ⟨-, -, -, hr, -, -⟩ | ⟨-, q, -, -, hg, hgu⟩
        · exact hd h
        · obtain ⟨-, -, -, h4, -, -, h7⟩ := h1
          simp only [a1_J_eq, a2_J_eq] at h4 h7
          have := sA1 h4; have := sz_a2 (a1 y); have := congrArg sz h7; omega
        · rw [hr] at he
          simp only [a1_J_eq, a2_J_eq] at he
          have := congrArg sz he
          simp only [sz] at this
          have := sz_a1 (a1 y); have := sz_a1 y; omega
        · simp only [a1_J_eq, a2_J_eq] at hg hgu
          exact ih z (op z q) y c (by omega) hgu.symm
      · rcases TR z (J (op c y) y) with h | ⟨-, hr⟩ | ⟨-, -, -, hr, -, -⟩ | ⟨-, q, -, -, -, hgu⟩
        · exact hd h
        · rw [hr] at he
          simp only [a1_J_eq, a2_J_eq] at he
          have := congrArg sz he
          simp only [sz] at this
          have := sz_a1 (a1 (a2 (op c y))); have := sz_a1 (a2 (op c y))
          have := sz_a2 (op c y); omega
        · rw [hr] at he
          simp only [a1_J_eq, a2_J_eq] at he
          have := congrArg sz he
          simp only [sz] at this
          have := sz_a1 (a1 y); have := sz_a1 y; omega
        · /- **THE ONE OPEN CELL.**  `op c y` is decoded (`sz (op c y) < sz y`) and R3's guard reads
             `op c y = op z (op (op (op z q) y) y)`.  The IH does not apply: it needs a conclusion of
             the form `... = J a' y`, and `op c y` has no such form.  This is the guard-decoded
             residue that also blocks `SF`, `SFa`, `SFb`; see NOTES_32281 § SESSION 4. -/
          sorry
    · omega

theorem AFm {z c y a : M} (he : op z (op (op c y) y) = J a y) : False :=
  AFn (msr z (op (op c y) y) + 1) z c y a (Nat.lt_succ_self _) he

/-- `AF`'s TRUE restriction: with `Q` the literal `J (J x y) y` the third chain product IS free.
    0 failures in 294,800 corrected-pool triples; every `AF` failure has `op x y` decoded. -/
theorem Afree (x y z : M) : op z (J (J x y) y) = J z (J (J x y) y) := by
  rcases TR z (J (J x y) y) with h | ⟨h1, -⟩ | ⟨-, -, -, -, -, he⟩ | ⟨-, q, -, -, -, he⟩
  · exact h
  · exfalso
    obtain ⟨-, -, -, h4, -, -, h7⟩ := h1
    simp only [a1_J_eq, a2_J_eq] at h4 h7
    have := sA1 h4; have := sz_a2 (a1 y); have := congrArg sz h7; omega
  · exact absurd he (fun hh => AFm (by simp only [a1_J_eq, a2_J_eq] at hh; exact hh.symm))
  · exact absurd he (fun hh => AFm (by simp only [a1_J_eq, a2_J_eq] at hh; exact hh.symm))

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

/-- with the third chain product left abstract, `P1` at the top is refuted whenever `Q` is decoded:
    `A` free gives `a2 (a1 Q) = y` against `sz Q < sz y`, `A` decoded gives `sz y < sz A < sz Q`. -/
theorem NPAq {x y z : M} (hqd : sz (op (op x y) y) < sz y) :
    ¬ P1 z (J (op z (op (op x y) y)) y) := by
  intro h
  obtain ⟨-, h2, -, h4, h5, -, h7⟩ := h
  simp only [a1_J_eq, a2_J_eq] at h2 h4 h5 h7
  rcases RS z (op (op x y) y) with hf | hf
  · rw [hf] at h7
    simp only [a1_J_eq, a2_J_eq] at h7
    have := congrArg sz h7
    have := sz_a2 (a1 (op (op x y) y)); have := sz_a1 (op (op x y) y)
    omega
  · have e1 := sA2 h2; have e2 := sA1 h4; have e3 := sA2 h5
    have e4 := congrArg sz h7
    omega

/-- `TOP` with the third chain product `A` left ABSTRACT.  `AF` is false (NOTES_32281 § SESSION 4),
    so `A` may not be replaced by `J z Q`; it never needed to be.  R2's guard is `A = A` once
    `a1 (a1 y) = x`, so `TOPg` is strictly weaker in hypotheses than `TOP`. -/
theorem TOPg {x y z A : M} (hy : tg y = 2) (hay : tg (a1 y) = 2) (hx : a1 (a1 y) = x)
    (hPs : sz (op x y) < sz y) (hA : op z (op (op x y) y) = A) (hn : ¬ P1 z (J A y))
    (hz : sz z < sz A + sz y) (hq : sz (op (op x y) y) < sz A + sz y) :
    op z (J A y) = x := by
  have hxy : sz x ≤ sz y := by
    rw [← hx]; have := sz_a1 (a1 y); have := sz_a1 y; omega
  have hs : sz (J A y) = sz A + sz y + 1 := by simp only [sz]
  have g1 : msr (a1 (a1 (a2 (J A y)))) (a2 (J A y)) < msr z (J A y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by omega) (by omega))
  have g2 : msr (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y)) < msr z (J A y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by omega) (by omega))
  have g3 : msr z (op (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y))) < msr z (J A y) := by
    simp only [a1_J_eq, a2_J_eq, hx]
    exact msr_lt_of_max_lt (mxl (by omega) (by omega))
  have hg : a1 (J A y) =
      op z (op (op (a1 (a1 (a2 (J A y)))) (a2 (J A y))) (a2 (J A y))) := by
    simp only [a1_J_eq, a2_J_eq, hx]; exact hA.symm
  rw [oR2 (u := z) (v := J A y) hn ⟨rfl, hy, hay⟩ g1 g2 g3 hg]
  simp only [a2_J_eq, hx]

/-- `P1` at the top is refuted when `A` IS free, from `sz (a2 (a1 Q)) < sz y`.  Together with
    `NPAq` (the `Q` decoded case) this covers everything `AQd` offers. -/
theorem NPAf {x y z : M} (hQ : sz (a2 (a1 (op (op x y) y))) < sz y)
    (hA : op z (op (op x y) y) = J z (op (op x y) y)) :
    ¬ P1 z (J (op z (op (op x y) y)) y) := by
  intro h
  obtain ⟨-, -, -, -, -, -, h7⟩ := h
  simp only [a1_J_eq, a2_J_eq] at h7
  rw [hA] at h7
  simp only [a1_J_eq, a2_J_eq] at h7
  have := congrArg sz h7
  omega

/-- **HOLE (replaces the old `SF`)**: the fourth chain product is free with `A` left ABSTRACT.
    `SF` is this lemma's `A`-free special case.  0 failures in 294,800 corrected-pool triples. -/
theorem SFg (x y z : M) :
    op (op z (op (op x y) y)) y = J (op z (op (op x y) y)) y := by
  sorry

/-- **HOLE**: on the decoded branch, `A` is free or `Q` is decoded — equivalently `A` decoded
    forces `Q` decoded.  0 failures / 0 occurrences of the negation in 294,800 triples. -/
theorem AQd (x y z : M) (hP : op x y ≠ J x y) :
    op z (op (op x y) y) = J z (op (op x y) y) ∨ sz (op (op x y) y) < sz y := by
  sorry

theorem law (x y z : M) : op (z) (op (op (z) (op (op (x) (y)) (y))) (y)) = x := by
  rw [SFg x y z]
  by_cases hP : op x y = J x y
  · rw [show op (op x y) y = J (J x y) y by
      rw [hP]; exact Wf (by simp only [sz]; have := sz_pos x; omega), Afree x y z]
    exact oR1 ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  · have hPs := (RS x y).resolve_left hP
    have hQ : sz (a2 (a1 (op (op x y) y))) < sz y := by
      rcases RS (op x y) y with h | h
      · rw [h]; simp only [a1_J_eq]; have := sz_a2 (op x y); omega
      · have := sz_a1 (op (op x y) y); have := sz_a2 (a1 (op (op x y) y)); omega
    /- **HOLE (agent D)**: `op x y` decoded puts `x` at `a1 (a1 y)`.  FALSE as a conjunction on the
       one level-2 cell where R2's own gate product decodes; must become a disjunction whose second
       arm fires R3 at the top. -/
    have hk : tg y = 2 ∧ tg (a1 y) = 2 ∧ a1 (a1 y) = x := by
      sorry
    have hpa := sz_pos (op z (op (op x y) y))
    rcases AQd x y z hP with hA | hA
    · have e := congrArg sz hA
      simp only [sz] at e
      exact TOPg hk.1 hk.2.1 hk.2.2 hPs rfl (NPAf hQ hA) (by omega) (by omega)
    · have hz : sz z < sz (op z (op (op x y) y)) + sz y := by
        rcases RS z (op (op x y) y) with hf | hf
        · have e := congrArg sz hf; simp only [sz] at e; omega
        · have hne : op z (op (op x y) y) ≠ J z (op (op x y) y) := by
            intro hc; rw [hc] at hf; simp only [sz] at hf; have := sz_pos z; omega
          have := SU hne; omega
      exact TOPg hk.1 hk.2.1 hk.2.2 hPs rfl (NPAq hA) hz (by omega)


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
