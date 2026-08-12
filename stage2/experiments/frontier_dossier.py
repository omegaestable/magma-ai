"""Print the equations and structural facts for the open frontier rows.

Pure inspection: no solving, no budget. Exists so frontier analysis starts from
the actual laws rather than from row ids.

Usage:
    python stage2/experiments/frontier_dossier.py --open
    python stage2/experiments/frontier_dossier.py --ids hard3_0314,hard3_0214
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

from egg_bytes_probe import OPEN_ROWS, load_rows  # noqa: E402


def facts(row: dict) -> dict:
    eq1 = S.parse_equation(str(row["equation1"]))
    eq2 = S.parse_equation(str(row["equation2"]))
    out = {
        "id": row.get("id"),
        "label": row.get("answer"),
        "eq1": eq1["text"],
        "eq2": eq2["text"],
        "eq1_vars": sorted(eq1["variables"]),
        "eq2_vars": sorted(eq2["variables"]),
        "eq1_size": (S._egg_term_size(eq1["lhs"]), S._egg_term_size(eq1["rhs"])),
        "eq2_size": (S._egg_term_size(eq2["lhs"]), S._egg_term_size(eq2["rhs"])),
        "eq1_bare_var_side": S._eq1_has_bare_variable_side(eq1),
    }
    # Which small pivot laws would close this goal for free?
    closers = []
    for name, text in (("collapse", "a = b"),
                       ("left_projection", "a ◇ b = a"),
                       ("right_projection", "a ◇ b = b"),
                       ("product_constant", "a ◇ b = c ◇ d"),
                       ("left_row_constant", "a ◇ b = a ◇ c"),
                       ("right_col_constant", "a ◇ b = c ◇ b")):
        lemma = S.lemma_goal(text)
        if S.lemma_applies_to_goal(lemma, eq2) is not None:
            survives = S.lemma_survives_models(eq1, lemma)
            closers.append(f"{name}{'' if survives else ' (refuted by eq1 model)'}")
    out["goal_closers"] = closers
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()
    rows = load_rows()
    ids = list(OPEN_ROWS) if args.open else [
        i for i in args.ids.split(",") if i.strip()]
    for row_id in ids:
        row = rows.get(row_id)
        if row is None:
            print(json.dumps({"id": row_id, "error": "not found"}))
            continue
        try:
            print(json.dumps(facts(row), ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"id": row_id,
                              "error": f"{type(exc).__name__}: {exc}"}))


if __name__ == "__main__":
    main()
