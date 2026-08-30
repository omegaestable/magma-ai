theorem gm {a b u v : M} (ha : sz a ≤ sz u) (hb : sz b < sz v) : W a b < W u v := by
  rcases Nat.lt_or_ge (max (sz a) (sz b)) (max (sz u) (sz v)) with h | h
  · exact wlt h
  · have he : max (sz a) (sz b) = max (sz u) (sz v) :=
      Nat.le_antisymm (Nat.max_le.mpr ⟨Nat.le_trans ha (Nat.le_max_left _ _),
        Nat.le_trans (Nat.le_of_lt hb) (Nat.le_max_right _ _)⟩) h
    unfold W; rw [he]; omega

