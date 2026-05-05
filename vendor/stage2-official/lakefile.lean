import Lake
open Lake DSL

package «stage2-judge»

-- Pinned Mathlib revision (bump deliberately via `lake update`).
-- lake-manifest.json is the source of truth for the exact commit.
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "896cc56a395e1615786fac56564a3fe6bfeebcc4"

lean_lib «JudgeMagma» where
  srcDir := "judge"
  roots := #[`JudgeMagma.Magma]

lean_lib «JudgeDecide» where
  srcDir := "judge"
  roots := #[`JudgeDecide.DecideBang]

lean_lib «JudgeFinOp» where
  srcDir := "judge"
  roots := #[`JudgeFinOp.MemoFinOp]

lean_lib «JudgeSupport» where
  srcDir := "judge"
  roots := #[`JudgeSupport.Inspect]
