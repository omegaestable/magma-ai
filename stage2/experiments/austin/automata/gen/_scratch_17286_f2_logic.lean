import JudgeProblem

inductive Scratch17286.M : Type where
  | g : Nat → Scratch17286.M
  | J : Scratch17286.M → Scratch17286.M → Scratch17286.M

namespace Scratch17286
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
  | .J x y => sz x + sz y + 1
axiom op : M → M → M

@[simp] theorem a1_J_eq (x y : M) : a1 (J x y) = x := rfl
@[simp] theorem a2_J_eq (x y : M) : a2 (J x y) = y := rfl
@[simp] theorem sz_J (x y : M) : sz (J x y) = sz x + sz y + 1 := rfl

def cds (u c : M) : Prop :=
  tg c = 2 ∧ tg (a2 c) = 2 ∧ a1 c = a1 (a2 c) ∧ op u (a1 c) = a2 (a2 c)

axiom sz_pos (t : M) : 1 ≤ sz t
axiom sz_a2 (t : M) : sz (a2 t) ≤ sz t
axiom sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t
axiom cds_a2_le_payload {u c : M} (h : cds u c) :
  sz (a2 u) ≤ sz (a2 (a2 c))
axiom cds_a2_lt {u c : M} (h : cds u c) : sz (a2 u) < sz c
axiom op_ne_left (u v : M) : op u v ≠ u
axiom op_ne_right (u v : M) : op u v ≠ v
axiom cds_self (u : M) : ¬ cds u u
axiom out_cases {u z P : M} (h : op u z = P) :
  P = J u z ∨ (cds P z ∧ ((tg u = 2 ∧ a2 u = P) ∨ cds u P))
axiom FDiag (z : M) : op z (J z (J z z)) = J z (J z (J z z))

theorem code_eq_recon {c P : M}
    (hc : tg c = 2 ∧ tg (a2 c) = 2 ∧ a1 c = a1 (a2 c))
    (h : a2 c = P) : c = J (a1 P) P := by
  rcases c with c | ⟨a, b⟩
  · simp [tg] at hc
  · simp only [a1_J_eq, a2_J_eq] at hc h ⊢
    subst b
    rw [hc.2.2]

/-- Adjacent right children never have the same value at one argument. -/
theorem a2_fiber_N (n : Nat) : ∀ u v P : M, sz P ≤ n → tg u = 2 →
    op u v = P → op (a2 u) v = P → False := by
  induction n with
  | zero =>
    intro u v P hn
    have hp := sz_pos P
    omega
  | succ n ih =>
    intro u v P hn hu h1 h2
    rcases out_cases h1 with h1f | ⟨hPv1, h1s⟩
    · rcases out_cases h2 with h2f | ⟨hPv2, -⟩
      · have he : u = a2 u := by
          have h := h1f.symm.trans h2f
          injection h
        have hs := sz_a2_lt hu
        rw [← he] at hs
        omega
      · have hs := cds_a2_lt hPv2
        rw [h1f] at hs
        simp only [a2_J_eq] at hs
        omega
    · rcases out_cases h2 with h2f | ⟨hPv2, h2s⟩
      · have hs := cds_a2_lt hPv1
        rw [h2f] at hs
        simp only [a2_J_eq] at hs
        omega
      · rcases h1s with h1d | h1r <;> rcases h2s with h2d | h2r
        · rw [h1d.2] at h2d
          have hs := sz_a2_lt h2d.1
          have he := congrArg sz h2d.2
          omega
        · rw [h1d.2] at h2r
          exact cds_self P h2r
        · have e1 := cds_a2_le_payload h1r
          have e2 := sz_a2_lt h1r.1
          have e3 := sz_a2 (a2 P)
          have e4 := sz_a2 (a2 u)
          have es := congrArg sz h2d.2
          omega
        · have ep1 := sz_a2_lt h1r.1
          have ep2 := sz_a2 (a2 P)
          exact ih u (a1 P) (a2 (a2 P)) (by omega) hu
            h1r.2.2.2 h2r.2.2.2

theorem a2_fiber {u v : M} (hu : tg u = 2) : op u v ≠ op (a2 u) v := by
  intro h
  exact a2_fiber_N (sz (op u v)) u v (op u v) (Nat.le_refl _) hu rfl h.symm

/-- Adjacent inputs cannot send one argument to adjacent outputs. -/
theorem a2_square {u v P : M} (hu : tg u = 2) (hP : tg P = 2)
    (h1 : op u v = P) (h2 : op (a2 u) v = a2 P) : False := by
  rcases out_cases h1 with h1f | ⟨hPv1, -⟩
  · rw [h1f] at h2
    simp only [a2_J_eq] at h2
    exact op_ne_right (a2 u) v h2
  · rcases out_cases h2 with h2f | ⟨hPv2, -⟩
    · have e1 := cds_a2_lt hPv1
      have es := congrArg sz h2f
      simp only [sz_J] at es
      omega
    · apply a2_fiber hP
      exact hPv1.2.2.2.trans hPv2.2.2.2.symm

/-- A code and the right child of its source cannot share an output. -/
theorem code_a2_fiber_N (n : Nat) : ∀ A x z P : M, sz P ≤ n → tg A = 2 →
    cds A x → op (a2 A) z = P → op x z = P → False := by
  induction n with
  | zero =>
    intro A x z P hn
    have hp := sz_pos P
    omega
  | succ n ih =>
    intro A x z P hn hA hAx h1 h2
    rcases out_cases h1 with h1f | ⟨hPz1, h1s⟩
    · rcases out_cases h2 with h2f | ⟨hPz2, -⟩
      · have he : a2 A = x := by
          have h := h1f.symm.trans h2f
          injection h
        have hs := cds_a2_lt hAx
        rw [he] at hs
        omega
      · have hs := cds_a2_lt hPz2
        rw [h1f] at hs
        simp only [a2_J_eq] at hs
        omega
    · rcases out_cases h2 with h2f | ⟨hPz2, h2s⟩
      · have hs := cds_a2_lt hPz1
        rw [h2f] at hs
        simp only [a2_J_eq] at hs
        omega
      · rcases h1s with h1d | h1r <;> rcases h2s with h2d | h2r
        · have e1 := cds_a2_le_payload hAx
          have e2 := sz_a2_lt hAx.2.1
          have e3 := sz_a2 (a2 A)
          have es1 := congrArg sz h1d.2
          have es2 := congrArg sz h2d.2
          omega
        · have e1 := cds_a2_le_payload hAx
          have e2 := sz_a2_lt hAx.2.1
          have e3 := cds_a2_le_payload h2r
          have e4 := sz_a2_lt h2r.1
          have e5 := sz_a2 (a2 P)
          have e6 := sz_a2 (a2 A)
          have es := congrArg sz h1d.2
          omega
        · have hxEq := code_eq_recon
            (⟨hAx.1, hAx.2.1, hAx.2.2.1⟩) h2d.2
          have hp1 : op A (a1 P) = a2 P := by
            have h := hAx.2.2.2
            rw [hxEq] at h
            simpa only [a1_J_eq, a2_J_eq] using h
          exact a2_square hA h1r.2.1 hp1 h1r.2.2.2
        · have ep1 := sz_a2_lt h1r.1
          have ep2 := sz_a2 (a2 P)
          exact ih A x (a1 P) (a2 (a2 P)) (by omega) hA hAx
            h1r.2.2.2 h2r.2.2.2

end Scratch17286
