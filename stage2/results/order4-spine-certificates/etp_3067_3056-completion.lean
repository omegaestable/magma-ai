import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c : G, ((a ◇ ((a ◇ b) ◇ a)) ◇ c) = ((a ◇ b) ◇ a) := by
    intro a b c
    exact (congrArg (fun t => ((t ◇ ((a ◇ b) ◇ a)) ◇ c)) (h a b ((a ◇ b) ◇ a))).trans (((h ((a ◇ b) ◇ a) a c).symm))
  have hlem1 : ∀ a b c d : G, (a ◇ d) = (a ◇ (((a ◇ c) ◇ a) ◇ a)) := by
    intro a b c d
    exact (congrArg (fun t => (t ◇ d)) (h a c (((((a ◇ c) ◇ a) ◇ a) ◇ b) ◇ (((a ◇ c) ◇ a) ◇ a)))).trans ((hlem0 (((a ◇ c) ◇ a) ◇ a) b d).trans ((congrArg (fun t => (t ◇ (((a ◇ c) ◇ a) ◇ a))) ((h a c b).symm))))
  intro z x y
  exact (hlem1 z x y x).trans (((hlem1 z x y y).symm))
