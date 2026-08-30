import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c d : G, (b ◇ (a ◇ (a ◇ c))) = (((d ◇ a) ◇ a) ◇ b) := by
    intro a b c d
    exact (congrArg (fun t => (b ◇ (a ◇ t))) (h a c d)).trans ((congrArg (fun t => (b ◇ t)) (h a (c ◇ ((d ◇ a) ◇ a)) d)).trans (((h ((d ◇ a) ◇ a) b c).symm)))
  have hlem1 : ∀ a b c d e : G, (a ◇ b) = (((c ◇ a) ◇ a) ◇ b) := by
    intro a b c d e
    exact (h a b (d ◇ a)).trans ((congrArg (fun t => (b ◇ t)) ((hlem0 a a e d).symm)).trans ((hlem0 a b (a ◇ e) c)))
  have hlem2 : ∀ a b c d : G, (a ◇ b) = (b ◇ a) := by
    intro a b c d
    exact (h a b c).trans ((h b ((c ◇ a) ◇ a) d).trans (((hlem1 a ((d ◇ b) ◇ b) c a a).symm).trans (((h b a d).symm))))
  have hlem3 : ∀ a b c : G, (a ◇ (b ◇ b)) = (b ◇ a) := by
    intro a b c
    exact (congrArg (fun t => (a ◇ t)) (hlem1 b b c a a)).trans (((h b a (c ◇ b)).symm))
  have hlem4 : ∀ a b c d : G, (b ◇ (a ◇ (a ◇ c))) = (a ◇ b) := by
    intro a b c d
    exact (congrArg (fun t => (b ◇ (a ◇ t))) (h a c d)).trans ((congrArg (fun t => (b ◇ t)) (h a (c ◇ ((d ◇ a) ◇ a)) d)).trans (((h ((d ◇ a) ◇ a) b c).symm).trans (((hlem1 a b d a a).symm))))
  have hlem5 : ∀ a b : G, (a ◇ b) = (b ◇ (a ◇ (b ◇ a))) := by
    intro a b
    exact (h a b b).trans ((congrArg (fun t => (b ◇ t)) (hlem2 (b ◇ a) a a a)))
  have hlem6 : ∀ a b : G, (a ◇ a) = (a ◇ (a ◇ b)) := by
    intro a b
    exact ((hlem4 a a b a).symm).trans ((congrArg (fun t => (a ◇ t)) ((hlem4 a (a ◇ b) b a).symm)).trans (((hlem5 (a ◇ b) a).symm).trans ((hlem2 (a ◇ b) a a a))))
  have hlem7 : ∀ a b c : G, (b ◇ (a ◇ b)) = (b ◇ b) := by
    intro a b c
    exact (congrArg (fun t => (b ◇ t)) (h a b c)).trans (((hlem6 b ((c ◇ a) ◇ a)).symm))
  have hlem8 : ∀ a b : G, ((a ◇ a) ◇ (a ◇ b)) = (a ◇ a) := by
    intro a b
    exact (congrArg (fun t => ((a ◇ a) ◇ t)) ((hlem3 b a a).symm)).trans ((hlem7 b (a ◇ a) a).trans ((hlem3 (a ◇ a) a a).trans ((hlem3 a a a))))
  have hlem9 : ∀ a b c : G, (b ◇ a) = (a ◇ (b ◇ c)) := by
    intro a b c
    exact ((hlem3 a b a).symm).trans ((congrArg (fun t => (a ◇ t)) ((hlem8 b c).symm)).trans ((congrArg (fun t => (a ◇ (t ◇ (b ◇ c)))) ((hlem8 b c).symm)).trans (((h (b ◇ c) a (b ◇ b)).symm).trans ((hlem2 (b ◇ c) a a a)))))
  have hlem10 : ∀ a b c : G, (a ◇ b) = (b ◇ b) := by
    intro a b c
    exact (hlem9 b a b).trans ((congrArg (fun t => (b ◇ t)) (h a b c)).trans (((hlem6 b ((c ◇ a) ◇ a)).symm)))
  have hlem11 : ∀ a b c : G, (a ◇ b) = (a ◇ a) := by
    intro a b c
    exact (h a b c).trans ((hlem10 b ((c ◇ a) ◇ a) a).trans (((h a ((c ◇ a) ◇ a) c).symm).trans (((h a a c).symm))))
  have hlem12 : ∀ a b : G, (b ◇ b) = (a ◇ a) := by
    intro a b
    exact ((hlem10 a b a).symm).trans ((hlem11 a b a))
  intro x y z
  exact (hlem12 y x).trans (((hlem11 y z x).symm))
