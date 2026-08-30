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

def R : M → Nat
  | .g _ => 1
  | .J _ _ => 2
def C : M → M
  | .J x _ => x
  | t => t
def E : M → M
  | .J _ x => x
  | t => t
def Q : M → Nat
  | .g _ => 1
  | .J b0 b1 => Q b0 + Q b1 + 1
theorem I (u : M) : Q (C u) ≤ Q u := by cases u <;> simp [C, Q] <;> omega
theorem G (u : M) : Q (E u) ≤ Q u := by cases u <;> simp [E, Q] <;> omega
theorem N {a b : M} (h : a = b) : Q a = Q b := congrArg Q h
theorem j (t : M) (h : R t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [R]
theorem D (t : M) (h : R t = 2) : Q t = Q (C t) + Q (E t) + 1 := by
  obtain ⟨a, b, rfl⟩ := j _ h; simp [Q, C, E]
@[simp] theorem tg_g_eq (n : Nat) : R (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : R (M.J b0 b1) = 2 := rfl
@[simp] theorem j1 (b0 b1 : M) : C (M.J b0 b1) = b0 := rfl
@[simp] theorem j2 (b0 b1 : M) : E (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : C (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : E (M.g n) = M.g n := rfl
attribute [simp] Q
def K (u v : M) : Nat := max (Q u) (Q v) * max (Q u) (Q v) + Q u + Q v
theorem H {a b u v : M} (h : max (Q a) (Q b) < max (Q u) (Q v)) : K a b < K u v := by
  unfold K
  have Z : Q a + Q b ≤ 2 * max (Q a) (Q b) := by omega
  have f : (max (Q a) (Q b) + 1) * (max (Q a) (Q b) + 1) ≤ max (Q u) (Q v) * max (Q u) (Q v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at f
  omega
abbrev P1 (u v : M) : Prop := R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ R (C (E v)) = 2 ∧ u = E (C (E v)) ∧ R (E (E v)) = 2 ∧ u = E (E (E v))
abbrev P2 (u v : M) : Prop := R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ R (C (E v)) = 2 ∧ u = E (C (E v)) ∧ R u = 2
abbrev P3 (u v : M) : Prop := R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ R (E (E v)) = 2 ∧ u = E (E (E v)) ∧ R u = 2
abbrev P4 (u v : M) : Prop := R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ R u = 2
abbrev P5 (u v : M) : Prop := R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ R u = 2 ∧ C u = E u ∧ C u = C (E v)
def op (u v : M) : M :=
  let p1 := if V : K (C u) (u) < K u v then op (C u) (u) else J u v
  let p2 := if hs2 : K (C (E v)) (E v) < K u v then op (C (E v)) (E v) else J u v
  if P1 u v then C (E (E v))
  else if P2 u v ∧ K (C u) (u) < K u v ∧ E (E v) = p1 then C u
  else if P3 u v ∧ K (C u) (u) < K u v ∧ C (E v) = p1 then C (E (E v))
  else if P4 u v ∧ K (C u) (u) < K u v ∧ C (E v) = p1 ∧ E (E v) = p1 then C u
  else if P5 u v ∧ K (C (E v)) (E v) < K u v ∧ C u = p2 then J (E v) (u)
  else J u v
termination_by K u v
decreasing_by
  · assumption
  · assumption

def inst : Magma M := { op := fun a b => op b a }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (op (g 2) (g 2))) (op (op (g 0) (g 1)) (g 0))
  simp (config := {decide := true}) [op.eq_1, Q, P1, P2, P3, P4, P5]

theorem op_cases (u v : M) : ∃ p1 p2 : M,
    p1 = (if V : K (C u) u < K u v then op (C u) u else J u v) ∧
    p2 = (if hs2 : K (C (E v)) (E v) < K u v then op (C (E v)) (E v) else J u v) ∧
    op u v = (
  if P1 u v then C (E (E v))
  else if P2 u v ∧ K (C u) u < K u v ∧ E (E v) = p1 then C u
  else if P3 u v ∧ K (C u) u < K u v ∧ C (E v) = p1 then C (E (E v))
  else if P4 u v ∧ K (C u) u < K u v ∧ C (E v) = p1 ∧ E (E v) = p1 then C u
  else if P5 u v ∧ K (C (E v)) (E v) < K u v ∧ C u = p2 then J (E v) u
  else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

theorem TR5 (u v : M) : op u v = J u v ∨ (R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧ (
    (P1 u v ∧ op u v = C (E (E v))) ∨
    (P2 u v ∧ E (E v) = op (C u) u ∧ op u v = C u) ∨
    (P3 u v ∧ C (E v) = op (C u) u ∧ op u v = C (E (E v))) ∨
    (P4 u v ∧ C (E v) = op (C u) u ∧ E (E v) = op (C u) u ∧ op u v = C u) ∨
    (P5 u v ∧ C u = op (C (E v)) (E v) ∧ op u v = J (E v) u))) := by
  obtain ⟨p1, p2, W, hp2, w⟩ := op_cases u v
  rw [w]
  split
  · rename_i h; exact Or.inr ⟨h.1, h.2.1, h.2.2.1, Or.inl ⟨h, rfl⟩⟩
  · split
    · rename_i Z h
      obtain ⟨f, V, T⟩ := h
      rw [dif_pos V] at W; subst W
      exact Or.inr ⟨f.1, f.2.1, f.2.2.1, Or.inr (Or.inl ⟨f, T, rfl⟩)⟩
    · split
      · rename_i Z f h
        obtain ⟨h3, V, T⟩ := h
        rw [dif_pos V] at W; subst W
        exact Or.inr ⟨h3.1, h3.2.1, h3.2.2.1, Or.inr (Or.inr (Or.inl ⟨h3, T, rfl⟩))⟩
      · split
        · rename_i Z f h3 h
          obtain ⟨l, V, U, he2⟩ := h
          rw [dif_pos V] at W; subst W
          exact Or.inr ⟨l.1, l.2.1, l.2.2.1, Or.inr (Or.inr (Or.inr (Or.inl ⟨l, U, he2, rfl⟩)))⟩
        · split
          · rename_i Z f h3 l h
            obtain ⟨O, hs2, T⟩ := h
            rw [dif_pos hs2] at hp2; subst hp2
            exact Or.inr ⟨O.1, O.2.1, O.2.2.1, Or.inr (Or.inr (Or.inr (Or.inr ⟨O, T, rfl⟩)))⟩
          · left; rfl

theorem TRs (u v : M) : op u v = J u v ∨ (R v = 2 ∧ u = C v ∧ R (E v) = 2 ∧
    (Q (op u v) < Q v ∨ (R u = 2 ∧ C u = E u ∧ C u = C (E v) ∧ C u = op (C (E v)) (E v) ∧ op u v = J (E v) u))) := by
  rcases TR5 u v with h | ⟨Z, f, h3, h⟩
  · exact Or.inl h
  · right; refine ⟨Z, f, h3, ?_⟩
    have s1 := D v Z
    have s2 := D (E v) h3
    have s3 := I (E (E v))
    have s4 := G (E v)
    have s5 := I u
    have s6 : Q u = Q (C v) := by rw [f]
    rcases h with ⟨-, F⟩ | ⟨-, -, F⟩ | ⟨-, -, F⟩ | ⟨-, -, -, F⟩ | ⟨O, T, F⟩
    · left; rw [F]; omega
    · left; rw [F]; omega
    · left; rw [F]; omega
    · left; rw [F]; omega
    · right; exact ⟨O.2.2.2.1, O.2.2.2.2.1, O.2.2.2.2.2, T, F⟩

theorem NF {u v : M} (h : op u v ≠ J u v) : R v = 2 ∧ u = C v ∧ R (E v) = 2 := by
  rcases TR5 u v with h' | ⟨Z, f, h3, -⟩
  · exact absurd h' h
  · exact ⟨Z, f, h3⟩

theorem nf {u v : M} (h : ¬(R v = 2 ∧ u = C v ∧ R (E v) = 2)) : op u v = J u v :=
  Classical.byContradiction fun t => h (NF t)

theorem L1 (x y : M) : op x y = J x y ∨ (R y = 2 ∧ x = C y ∧ R (E y) = 2) := by
  rcases TR5 x y with h | ⟨Z, f, h3, -⟩
  · exact Or.inl h
  · exact Or.inr ⟨Z, f, h3⟩

theorem Dg {c y : M} (hc : C c ≠ y) : op y c = J y c := nf fun t => hc t.2.1.symm

theorem NQ (q : M) : op q (J q q) ≠ q := by
  intro T
  rcases TR5 q (J q q) with h | ⟨-, -, h3, h⟩
  · rw [h] at T; have := N T; simp at this; omega
  · simp at h3
    obtain ⟨q1, q2, rfl⟩ := j q h3
    have s1 := I q1; have s2 := G q1; have s3 := I q2; have s4 := G q2
    rcases h with ⟨-, F⟩ | ⟨-, -, F⟩ | ⟨-, -, F⟩ | ⟨-, -, -, F⟩ | ⟨-, -, F⟩ <;>
      (rw [F] at T; (try simp only [j1, j2] at T); have := N T; simp at this; omega)

theorem NE (u v : M) : op u v ≠ v := by
  intro T
  rcases TRs u v with h | ⟨Z, f, h3, h | ⟨l, O, h6, h7, h8⟩⟩
  · rw [h] at T; have := N T; simp at this; omega
  · have := N T; omega
  · rw [h8] at T
    obtain ⟨v1, v2, rfl⟩ := j v Z
    simp only [j1, j2] at f T h7
    subst f
    obtain ⟨hv, -⟩ := M.J.inj T
    subst hv
    obtain ⟨w1, w2, rfl⟩ := j v2 l
    simp at O h7
    subst O
    exact NQ w1 h7.symm

theorem NQ2 (q : M) : op q (J q (J q q)) ≠ q := by
  intro T
  rcases TR5 q (J q (J q q)) with h | ⟨-, -, -, h⟩
  · rw [h] at T; have := N T; simp at this; omega
  · rcases h with ⟨X, F⟩ | ⟨X, -, F⟩ | ⟨X, r, F⟩ | ⟨X, -, -, F⟩ | ⟨X, -, F⟩
    · obtain ⟨-, -, -, l, O, -, -⟩ := X
      simp at l O
      have := N O; have := D q l; have := G q; omega
    · obtain ⟨-, -, -, l, O, -⟩ := X
      simp at l O
      have := N O; have := D q l; have := G q; omega
    · simp at r
      exact NE (C q) q r.symm
    · obtain ⟨-, -, -, l⟩ := X
      rw [F] at T; have := N T; have := D q l; omega
    · obtain ⟨-, -, -, l, -, h6⟩ := X
      simp at h6
      have := N h6; have := D q l; omega

theorem op_R1 (y z x : M) : op y (J y (J (J z y) (J x y))) = x := by
  obtain ⟨p1, p2, -, -, w⟩ := op_cases y (J y (J (J z y) (J x y)))
  have Z : P1 y (J y (J (J z y) (J x y))) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  rw [w, if_pos Z]
  rfl

theorem CFF (x y z : M) : op (J z y) (J x y) = J (J z y) (J x y) ∨
    (x = J z y ∧ R y = 2 ∧ C y = op z (J z y) ∧ E y = op z (J z y) ∧ op (J z y) (J x y) = z) := by
  rcases TR5 (J z y) (J x y) with h | ⟨-, hu, L, h⟩
  · exact Or.inl h
  · simp at hu L
    subst hu
    have s1 := D y L
    have s2 := I y
    have s3 := G y
    have s4 := G (C y)
    have s5 := G (E y)
    rcases h with ⟨X, -⟩ | ⟨X, -, -⟩ | ⟨X, -, -⟩ | ⟨X, U, he2, F⟩ | ⟨X, -, -⟩
    · obtain ⟨-, -, -, -, O, -, -⟩ := X
      simp at O
      have := N O; simp at this; omega
    · obtain ⟨-, -, -, -, O, -⟩ := X
      simp at O
      have := N O; simp at this; omega
    · obtain ⟨-, -, -, -, O, -⟩ := X
      simp at O
      have := N O; simp at this; omega
    · simp at U he2 F
      exact Or.inr ⟨rfl, L, U, he2, F⟩
    · obtain ⟨-, -, -, -, O, h6⟩ := X
      simp at O h6
      subst O
      have := N h6; omega

theorem TZ {y z : M} (L : R y = 2) (Z : C y = op z (J z y)) (f : E y = op z (J z y)) :
    R z = 2 ∧ C z = C y ∧ op (C y) z = C y := by
  have s1 := D y L
  have s2 := I y
  have s3 := G y
  have s4 := I (E y)
  have s5 := G (C z)
  have s6 := I z
  rcases TR5 z (J z y) with h | ⟨-, -, -, h⟩
  · rw [h] at Z; have := N Z; simp at this; omega
  · rcases h with ⟨X, F⟩ | ⟨X, -, F⟩ | ⟨X, -, F⟩ | ⟨X, U, he2, F⟩ | ⟨X, -, F⟩
    · obtain ⟨-, -, -, -, -, h6, -⟩ := X
      simp at h6 F
      rw [F] at f; have := N f; have := D (E y) h6; omega
    · obtain ⟨-, -, -, -, O, h6⟩ := X
      simp at O F
      rw [F] at Z; rw [Z] at O
      have := N O; have := D z h6; omega
    · obtain ⟨-, -, -, l, -, -⟩ := X
      simp at l F
      rw [F] at f; have := N f; have := D (E y) l; omega
    · obtain ⟨-, -, -, l⟩ := X
      simp at U F
      rw [F] at Z
      refine ⟨l, Z.symm, ?_⟩
      rw [Z] at U ⊢
      exact U.symm
    · simp at F
      rw [F] at Z; have := N Z; simp at this; omega

theorem op_R5 {y z : M} (L : R y = 2) (hyq : C y = E y) (htz : R z = 2) (hz : C z = C y)
    (hq : op (C y) z = C y) : op y (J y z) = J z y := by
  obtain ⟨S, y2, rfl⟩ := j y L
  simp at hyq hz hq
  subst hyq
  obtain ⟨p1, p2, W, hp2, w⟩ := op_cases (J S S) (J (J S S) z)
  have V : K (C (J S S)) (J S S) < K (J S S) (J (J S S) z) :=
    H (by simp; omega)
  have hs2 : K (C (E (J (J S S) z))) (E (J (J S S) z)) < K (J S S) (J (J S S) z) :=
    H (by simp; have := I z; omega)
  rw [dif_pos V] at W; subst W; rw [dif_pos hs2] at hp2; subst hp2
  have s1 := G S
  rw [w]
  split
  · rename_i h
    obtain ⟨-, -, -, -, O, -, -⟩ := h
    simp at O
    rw [hz] at O; have := N O; simp at this; omega
  · split
    · rename_i Z h
      obtain ⟨⟨-, -, -, -, O, -⟩, -, -⟩ := h
      simp at O
      rw [hz] at O; have := N O; simp at this; omega
    · split
      · rename_i Z f h
        obtain ⟨-, -, T⟩ := h
        simp at T
        rw [hz] at T
        exact absurd T.symm (NQ S)
      · split
        · rename_i Z f h3 h
          obtain ⟨-, -, T, -⟩ := h
          simp at T
          rw [hz] at T
          exact absurd T.symm (NQ S)
        · split
          · rfl
          · rename_i Z f h3 l O
            exfalso; apply O
            refine ⟨⟨rfl, rfl, htz, rfl, rfl, hz.symm⟩, hs2, ?_⟩
            show S = op (C z) z
            rw [hz]; exact hq.symm

theorem R24case {y : M} (L : R y = 2) (h7 : y = E (op (C y) y)) : C (op (C y) y) = C y := by
  have s1 := D y L
  have s2 := G (op (C y) y)
  rcases TRs (C y) y with hf | ⟨-, -, -, hs | ⟨-, -, -, -, F⟩⟩
  · rw [hf]; rfl
  · have := N h7; omega
  · rw [F] at h7; simp at h7; have := N h7; have := I y; omega

theorem op_R2 {y : M} (L : R y = 2) (z : M) : op y (J y (J (J z y) (op (C y) y))) = C y := by
  obtain ⟨p1, p2, W, hp2, w⟩ := op_cases y (J y (J (J z y) (op (C y) y)))
  have V : K (C y) y < K y (J y (J (J z y) (op (C y) y))) :=
    H (by simp; have := I y; omega)
  rw [dif_pos V] at W; subst W
  have s1 := D y L
  have s2 := G (op (C y) y)
  rw [w]
  split
  · rename_i h
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp at h7
    exact R24case L h7
  · split
    · rfl
    · rename_i Z f
      exfalso; apply f
      exact ⟨⟨rfl, rfl, rfl, rfl, rfl, L⟩, V, rfl⟩

theorem CNF {y : M} (L : R y = 2) (z : M) : op (J z y) (op (C y) y) = J (J z y) (op (C y) y) := by
  apply nf; intro ⟨_, hu, _⟩
  have s1 := D y L
  have s2 := I y
  have s3 := G y
  have s4 := I (op (C y) y)
  rcases TRs (C y) y with hf | ⟨-, -, -, hs | ⟨-, -, -, -, F⟩⟩
  · rw [hf] at hu; simp at hu; have := N hu; simp at this; omega
  · have := N hu; simp at this; omega
  · rw [F] at hu; simp at hu; have := N hu; simp at this; omega

theorem op_R3 {y : M} (L : R y = 2) (x : M) : op y (J y (J (op (C y) y) (J x y))) = x := by
  obtain ⟨p1, p2, W, hp2, w⟩ := op_cases y (J y (J (op (C y) y) (J x y)))
  have V : K (C y) y < K y (J y (J (op (C y) y) (J x y))) :=
    H (by simp; have := I y; omega)
  rw [dif_pos V] at W; subst W
  rw [w]
  split
  · rfl
  · split
    · rename_i Z h
      exfalso; apply Z
      obtain ⟨⟨-, -, -, l, O, -⟩, -, -⟩ := h
      exact ⟨rfl, rfl, rfl, l, O, rfl, rfl⟩
    · split
      · rfl
      · rename_i Z f h3
        exfalso; apply h3
        exact ⟨⟨rfl, rfl, rfl, rfl, rfl, L⟩, V, rfl⟩

theorem op_R4 {y : M} (L : R y = 2) : op y (J y (J (op (C y) y) (op (C y) y))) = C y := by
  obtain ⟨p1, p2, W, hp2, w⟩ := op_cases y (J y (J (op (C y) y) (op (C y) y)))
  have V : K (C y) y < K y (J y (J (op (C y) y) (op (C y) y))) :=
    H (by simp; have := I y; omega)
  rw [dif_pos V] at W; subst W
  have s1 := D y L
  have s2 := G (op (C y) y)
  rw [w]
  split
  · rename_i h
    obtain ⟨-, -, -, -, O, -, -⟩ := h
    simp at O
    exact R24case L O
  · split
    · rfl
    · split
      · rename_i Z f h
        exfalso; apply f
        obtain ⟨⟨-, -, -, l, O, h6⟩, hs, T⟩ := h
        exact ⟨⟨rfl, rfl, rfl, l, O, h6⟩, hs, T⟩
      · split
        · rfl
        · rename_i Z f h3 l
          exfalso; apply l
          exact ⟨⟨rfl, rfl, rfl, L⟩, V, rfl, rfl⟩

theorem m {A B P : M} (r : M.J A B = op (C P) P) :
    (Q A = Q (C P) ∧ Q B = Q P) ∨ (Q A + Q B + 1 < Q P) ∨ (Q A = Q (E P) ∧ Q B = Q (C P)) := by
  rcases TRs (C P) P with hgf | ⟨-, -, -, hs | ⟨-, -, -, -, hr5⟩⟩
  · rw [hgf] at r; obtain ⟨e1, e2⟩ := M.J.inj r
    exact Or.inl ⟨by rw [e1], by rw [e2]⟩
  · right; left; have := N r; simp at this; omega
  · rw [hr5] at r; obtain ⟨e1, e2⟩ := M.J.inj r
    exact Or.inr (Or.inr ⟨by rw [e1], by rw [e2]⟩)

theorem PPfree {p : M} (hp2 : R p = 2) : op p (J p p) = J p (J p p) ∨
    (C p = op (C p) p ∧ op p (J p p) = C p) ∨ op p (J p p) = J p p := by
  have sp := D p hp2
  rcases TR5 p (J p p) with hqf | ⟨-, -, -, ⟨hP', -⟩ | ⟨hP', -, -⟩ | ⟨hP', -, -⟩ | ⟨-, U, -, hr'⟩ | ⟨-, -, hr'⟩⟩
  · exact Or.inl hqf
  · exfalso; obtain ⟨-, -, -, -, O, -, -⟩ := hP'; simp at O
    have := N O; have := G (C p); omega
  · exfalso; obtain ⟨-, -, -, -, O, -⟩ := hP'; simp at O
    have := N O; have := G (C p); omega
  · exfalso; obtain ⟨-, -, -, -, O, -⟩ := hP'; simp at O
    have := N O; have := G (E p); omega
  · right; left; simp at U; exact ⟨U, hr'⟩
  · right; right; simp at hr'; exact hr'

theorem CFN {y : M} (L : R y = 2) (hta : R (E y) = 2) (x : M) :
    op (op (C y) y) (J x y) = J (op (C y) y) (J x y) := by
  apply Classical.byContradiction; intro h
  obtain ⟨-, hu, -⟩ := NF h
  simp at hu
  subst hu
  obtain ⟨S, y2, rfl⟩ := j y L
  simp at hta
  obtain ⟨s, i, rfl⟩ := j y2 hta
  simp at h
  have tp := TR5 S (J S (J s i))
  generalize hp : op S (J S (J s i)) = p at *
  have s1 := I S; have s2 := G S; have s3 := I s; have s4 := G s
  have s5 := I i; have s6 := G i; have s7 := I p; have s8 := G p
  rcases TR5 p (J p (J S (J s i))) with hf | ⟨-, -, -, hc⟩
  · exact h hf
  have t := TRs (C p) p
  rcases hc with ⟨X, -⟩ | ⟨X, r, -⟩ | ⟨X, r, -⟩ | ⟨X, hg1, o, -⟩ | ⟨X, r, -⟩
  ·
    obtain ⟨-, -, -, c4, c5, -, c7⟩ := X
    simp at c4 c5 c7
    have C1dup : p = C S → E (E (J S (J s i))) = op (C S) S → False := by
      intro F o
      simp at F o
      obtain ⟨c, d, rfl⟩ := j S c4
      simp at F c5 o
      subst F; subst c5
      rw [← c7] at o
      exact NQ p o.symm
    rcases tp with hpf | ⟨-, -, -, ⟨k, F⟩ | ⟨k, o, F⟩ | ⟨k, hg3, F⟩ | ⟨k, hg1, o, F⟩ | ⟨k, hg5, F⟩⟩
    · have := N c7; have := N hpf; simp at *; omega
    · obtain ⟨-, -, -, -, -, q6, -⟩ := k
      simp at q6 F
      have := N c7; have := N F; have := D i q6; omega
    · exact C1dup F o
    · obtain ⟨-, -, -, q4, -, -⟩ := k
      simp at q4 F
      have := N c7; have := N F; have := D i q4; omega
    · exact C1dup F o
    · simp at F
      have := N c7; have := N F; simp at *; omega
  ·
    obtain ⟨-, -, -, c4, c5, c6⟩ := X
    simp at c4 c5 c6 r
    have sp := D p c6
    rcases tp with hpf | ⟨-, -, -, ⟨k, F⟩ | ⟨k, o, F⟩ | ⟨k, hg3, F⟩ | ⟨k, hq1, hq2, F⟩ | ⟨k, hg5, F⟩⟩
    · have := N c5; have := N hpf; simp at *; omega
    · obtain ⟨-, -, -, -, -, q6, q7⟩ := k
      simp at q6 q7 F
      have e1 := D i q6
      have e2 := N F; have e3 := N q7
      rcases m r with ⟨k1, k2⟩ | hk | ⟨k1, k2⟩ <;> omega
    · obtain ⟨-, -, -, q4, q5, q6⟩ := k
      simp at q4 q5 q6 F o
      have e1 := D s q4
      have e2 := D S q6
      have e3 := N F; have e4 := N q5; have e5 := N c5
      rcases m r with ⟨k1, k2⟩ | hk | ⟨k1, k2⟩ <;> omega
    · obtain ⟨-, -, -, q4, q5, q6⟩ := k
      simp at q4 q5 q6 F hg3
      have e1 := D i q4
      have e2 := N F; have e3 := N q5
      rcases m r with ⟨k1, k2⟩ | hk | ⟨k1, k2⟩ <;> omega
    · obtain ⟨-, -, -, q4⟩ := k
      simp at F hq1 hq2
      obtain ⟨c, d, rfl⟩ := j S q4
      simp at F c5 hq1 hq2
      subst F; subst c5
      subst hq1; subst hq2
      rcases t with hgf | ⟨-, -, -, hs | ⟨t4, t5, t6, t7, hr5⟩⟩
      · rw [hgf] at r; obtain ⟨e1, e2⟩ := M.J.inj r; rw [e2] at e1; have := N e1; omega
      · have hsq := N r; simp at hsq
        rcases PPfree c6 with hqf | ⟨U, hr'⟩ | hr'
        · rw [hqf] at hsq; simp at hsq; omega
        · rw [hr', ← U] at r
          have := N r; simp at this; omega
        · rw [hr'] at hsq; simp at hsq; omega
      · rw [hr5] at r; obtain ⟨e1, e2⟩ := M.J.inj r
        rcases PPfree c6 with hqf | ⟨U, hr'⟩ | hr'
        · rw [hqf] at e2; have := N e2; simp at this; omega
        · rw [hr5] at U; have := N U; simp at this; omega
        · rw [hr'] at e2; have := N e2; simp at this; omega
    · simp at F
      have := N c5; have := N F; simp at *; omega
  ·
    obtain ⟨-, -, -, c4, c5, c6⟩ := X
    simp at c4 c5 c6 r
    have sp := D p c6
    have C3dup2 : p = C (E (E (J S (J s i)))) → False := by
      intro F
      simp at F
      have hty22 : R i = 2 := by rw [← c5]; exact c6
      have := N c5; have := N F; have := D i hty22; omega
    have C3dup3 : R S = 2 → p = C S → False := by
      intro q F
      obtain ⟨c, d, rfl⟩ := j S q
      simp at F r
      subst F
      rcases m r with ⟨k1, k2⟩ | hk | ⟨k1, k2⟩ <;> omega
    rcases tp with hpf | ⟨-, -, -, ⟨k, F⟩ | ⟨k, o, F⟩ | ⟨k, hg3, F⟩ | ⟨k, hq1, hq2, F⟩ | ⟨k, hg5, F⟩⟩
    · have := N c5; have := N hpf; simp at *; omega
    · exact C3dup2 F
    · obtain ⟨-, -, -, -, -, q6⟩ := k
      exact C3dup3 q6 F
    · exact C3dup2 F
    · obtain ⟨-, -, -, q4⟩ := k
      exact C3dup3 q4 F
    · simp at F
      have := N c5; have := N F; simp at *; omega
  ·
    obtain ⟨-, -, -, c4⟩ := X
    simp at hg1 o
    have hy : S = J s i := hg1.trans o.symm
    subst hy
    rcases tp with hpf | ⟨-, -, -, ⟨k, F⟩ | ⟨k, hg2', F⟩ | ⟨k, hg3, F⟩ | ⟨-, hq1, hq2, F⟩ | ⟨k, hg5, F⟩⟩
    · rw [hpf] at hg1; simp at hg1
      exact NQ2 (J s i) hg1.symm
    · obtain ⟨-, -, -, -, q5, -, -⟩ := k
      simp at q5
      have := N q5; simp at this; omega
    · obtain ⟨-, -, -, -, q5, -⟩ := k
      simp at q5
      have := N q5; simp at this; omega
    · obtain ⟨-, -, -, -, q5, -⟩ := k
      simp at q5
      have := N q5; simp at this; omega
    · simp at hq1 hq2 F
      have e : s = i := hq1.trans hq2.symm
      subst e
      exact NQ s hq1.symm
    · obtain ⟨-, -, -, -, q5, -⟩ := k
      simp at q5 hg5
      subst q5
      exact NQ s hg5.symm
  ·
    obtain ⟨-, -, -, c4, -, -⟩ := X
    simp at r
    rw [hp] at r
    have := N r; have := D p c4; omega

theorem law (x y z : M) : op (y) (op (y) (op (op (z) (y)) (op (x) (y)))) = x := by
  rcases L1 x y with hA | ⟨L, hx, hta⟩
  · rcases L1 z y with hB | ⟨L, hz, hta⟩
    · rw [hA, hB]
      rcases CFF x y z with hC | ⟨hxe, L, U, he2, hC⟩
      · have hD : op y (J (J z y) (J x y)) = J y (J (J z y) (J x y)) := by
          apply Dg; intro T; have := N T; simp at this; omega
        rw [hC, hD, op_R1]
      · subst hxe
        obtain ⟨htz, hz1, hq⟩ := TZ L U he2
        have hyq : C y = E y := U.trans he2.symm
        have hc : C z ≠ y := by
          rw [hz1]; intro T; have := N T; have := D y L; omega
        rw [hC, Dg hc, op_R5 L hyq htz hz1 hq]
    · subst hz
      have hD : op y (J (op (C y) y) (J x y)) = J y (J (op (C y) y) (J x y)) := Dg (NE (C y) y)
      rw [hA, CFN L hta x, hD, op_R3 L x]
  · rcases L1 z y with hB | ⟨-, hz, -⟩
    · subst hx
      have hD : op y (J (J z y) (op (C y) y)) = J y (J (J z y) (op (C y) y)) := by
        apply Dg; intro T; have := N T; simp at this; omega
      rw [hB, CNF L z, hD, op_R2 L z]
    · subst hx; subst hz
      have hpp : op (op (C y) y) (op (C y) y) = J (op (C y) y) (op (C y) y) := by
        apply nf; intro ⟨htp, hu, _⟩
        have := N hu; have := D _ htp; omega
      have hD : op y (J (op (C y) y) (op (C y) y)) = J y (J (op (C y) y) (op (C y) y)) := Dg (NE (C y) y)
      rw [hpp, hD, op_R4 L]

theorem lhs : @EquationLHS M inst := fun x y z => (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
