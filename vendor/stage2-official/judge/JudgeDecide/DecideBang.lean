/- decideFin! tactic: decides propositions over finite types by exhaustive checking. -/
import Lean

macro "decideFin!" : tactic => `(tactic| decide)
