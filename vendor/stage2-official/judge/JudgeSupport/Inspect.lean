import Lean

open Lean
open Lean.Elab
open Lean.Elab.Command

namespace JudgeSupport

def nameSetToSortedArray (names : NameSet) : Array Name :=
  Id.run do
    let mut collected : Array Name := #[]
    for name in names do
      collected := collected.push name
    pure <| collected.qsort Name.lt

def mkNameArrayJson (names : Array Name) : Json :=
  Json.arr <| names.map fun name => Json.str name.toString

elab "#judge_report " ident:ident nonce:str : command => do
  let constName ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo ident
  let env ← getEnv
  let some constInfo := env.find? constName
    | throwError "unknown declaration {constName}"
  let axioms := (← Lean.collectAxioms constName).qsort Name.lt
  let directDecls := nameSetToSortedArray constInfo.getUsedConstantsAsSet
  let nonceVal := nonce.getString
  let payload := Json.mkObj
    [
      ("nonce", Json.str nonceVal),
      ("target", Json.str constName.toString),
      ("axioms", mkNameArrayJson axioms),
      ("direct_declarations", mkNameArrayJson directDecls),
    ]
  liftIO <| IO.println s!"JUDGE_REPORT {payload.compress}"

end JudgeSupport
