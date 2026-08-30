import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b : G, (b ◇ a) = (a ◇ ((b ◇ b) ◇ b)) := by
    intro a b
    exact (h b a b b)
  have hlem1 : ∀ a b c d : G, (b ◇ c) = (((d ◇ a) ◇ b) ◇ c) := by
    intro a b c d
    exact (h b c (d ◇ a) b).trans ((congrArg (fun t => (c ◇ t)) (h ((d ◇ a) ◇ b) b (d ◇ a) b)).trans ((congrArg (fun t => (c ◇ t)) (h b (((d ◇ a) ◇ b) ◇ ((d ◇ a) ◇ b)) d a)).trans (((hlem0 c ((d ◇ a) ◇ b)).symm))))
  have hlem2 : ∀ a b c d e f : G, (c ◇ d) = (d ◇ c) := by
    intro a b c d e f
    exact (h c d e a).trans ((h d ((e ◇ a) ◇ c) f b).trans (((hlem1 a c ((f ◇ b) ◇ d) e).symm).trans (((h d c f b).symm))))
  have hlem3 : ∀ a b c d e : G, (c ◇ (b ◇ d)) = (d ◇ c) := by
    intro a b c d e
    exact (congrArg (fun t => (c ◇ t)) (hlem1 a b d e)).trans (((h d c (e ◇ a) b).symm))
  have hlem4 : ∀ a b c d e : G, (d ◇ c) = (b ◇ c) := by
    intro a b c d e
    exact ((hlem3 a b c d a).symm).trans ((congrArg (fun t => (c ◇ t)) (h b d e a)).trans ((hlem3 a d c ((e ◇ a) ◇ b) a).trans ((hlem2 a a ((e ◇ a) ◇ b) c a a).trans (((h b c e a).symm)))))
  have hlem5 : ∀ a b c d e : G, (c ◇ d) = (c ◇ b) := by
    intro a b c d e
    exact (h c d e a).trans ((hlem4 a b ((e ◇ a) ◇ c) d a).trans (((h c b e a).symm)))
  have hlem6 : ∀ a b c d : G, (b ◇ d) = (c ◇ a) := by
    intro a b c d
    exact ((hlem4 a b d c a).symm).trans ((hlem5 a a c d a))
  intro x y z
  exact (hlem6 y x y x).trans (((hlem5 x y y z x).symm))
