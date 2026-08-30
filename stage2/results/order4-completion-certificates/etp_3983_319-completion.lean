import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b : G, (a ◇ b) = ((b ◇ (b ◇ b)) ◇ a) := by
    intro a b
    exact (h a b b b)
  have hlem1 : ∀ a b c d : G, (b ◇ c) = (b ◇ (c ◇ (d ◇ a))) := by
    intro a b c d
    exact (h b c c (d ◇ a)).trans ((congrArg (fun t => (t ◇ b)) (h c (c ◇ (d ◇ a)) c (d ◇ a))).trans ((congrArg (fun t => (t ◇ b)) (h ((c ◇ (d ◇ a)) ◇ (c ◇ (d ◇ a))) c d a)).trans (((hlem0 b (c ◇ (d ◇ a))).symm))))
  have hlem2 : ∀ a b c d e f : G, (d ◇ c) = (c ◇ d) := by
    intro a b c d e f
    exact (h d c e a).trans ((h (c ◇ (e ◇ a)) d f b).trans (((hlem1 a (d ◇ (f ◇ b)) c e).symm).trans (((h c d f b).symm))))
  have hlem3 : ∀ a b c d e : G, (b ◇ (c ◇ d)) = (b ◇ c) := by
    intro a b c d e
    exact ((hlem2 a a b (c ◇ d) a a).symm).trans ((congrArg (fun t => (t ◇ b)) (hlem1 a c d e)).trans (((h b c d (e ◇ a)).symm)))
  have hlem4 : ∀ a b c d e : G, (b ◇ c) = (b ◇ d) := by
    intro a b c d e
    exact ((hlem3 a b c d a).symm).trans ((congrArg (fun t => (b ◇ t)) (h c d e a)).trans ((hlem3 a b (d ◇ (e ◇ a)) c a).trans ((hlem3 a b d (e ◇ a) a))))
  have hlem5 : ∀ a b c d e : G, (b ◇ d) = (c ◇ d) := by
    intro a b c d e
    exact (h b d e a).trans ((hlem4 a (d ◇ (e ◇ a)) b c a).trans (((h c d e a).symm)))
  have hlem6 : ∀ a b c d : G, (b ◇ d) = (c ◇ a) := by
    intro a b c d
    exact ((hlem4 a b a d a).symm).trans ((hlem5 a b c a a))
  intro x y z
  exact (hlem6 y x y x).trans (((hlem4 x y z y x).symm))
