#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

import distill
import proof_atlas

ROOT = Path(__file__).resolve().parent
HF_CACHE_DIR = ROOT / "data" / "hf_cache"
DEFAULT_OUT_DIR = ROOT / "results" / "proof_atlas_public"
DEFAULT_VARIANT_DIR = ROOT / "cheatsheets" / "generated_v2" / "atlas_public"
MODEL = "meta-llama/llama-3.3-70b-instruct"
EXPECTED_DATASET_COUNTS = {
    "normal": 1000,
    "hard1": 69,
    "hard2": 200,
    "hard3": 400,
}
PUBLIC_DATASETS = ("normal", "hard1")
HELDOUT_DATASETS = ("hard2", "hard3")


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_problem_set(name: str) -> list[dict]:
    path = HF_CACHE_DIR / f"{name}.jsonl"
    rows = load_jsonl(path)
    return [{**row, "source_subset": name} for row in rows]


def load_all_problem_sets() -> dict[str, list[dict]]:
    datasets = {name: load_problem_set(name) for name in (*PUBLIC_DATASETS, *HELDOUT_DATASETS)}
    for name, expected_count in EXPECTED_DATASET_COUNTS.items():
        actual_count = len(datasets[name])
        if actual_count != expected_count:
            raise ValueError(f"Dataset count mismatch for {name}: expected {expected_count}, found {actual_count}")
    return datasets


def build_dataset_split(datasets: dict[str, list[dict]], dev_ratio: float, seed: int) -> tuple[dict, list[dict]]:
    public_rows: list[dict] = []
    split_manifest: dict = {
        "policy": {
            "train_corpus": list(PUBLIC_DATASETS),
            "held_out_test": list(HELDOUT_DATASETS),
            "dev_ratio": dev_ratio,
            "seed": seed,
        },
        "counts": {},
        "public_ids": [],
        "heldout_ids": [],
    }

    for subset in PUBLIC_DATASETS:
        rows = [{**row, "role": "train_corpus", "source_subset": subset} for row in datasets[subset]]
        by_answer: dict[bool, list[dict]] = defaultdict(list)
        subset_offset = {"normal": 100, "hard1": 200}.get(subset, 0)
        for row in rows:
            by_answer[bool(row["answer"])].append(row)
        subset_counts = {"total": len(rows)}
        for answer, group in by_answer.items():
            answer_offset = 1 if answer else 2
            rng = random.Random(seed + subset_offset + answer_offset)
            ordered = list(group)
            ordered.sort(key=lambda item: item["id"])
            rng.shuffle(ordered)
            dev_count = max(1, round(len(ordered) * dev_ratio))
            dev_ids = {item["id"] for item in ordered[:dev_count]}
            subset_counts[f"{answer}_count"] = len(group)
            subset_counts[f"{answer}_dev"] = dev_count
            for row in rows:
                if bool(row["answer"]) == answer:
                    row["internal_split"] = "dev" if row["id"] in dev_ids else "train"
        public_rows.extend(rows)
        split_manifest["counts"][subset] = subset_counts
        split_manifest["public_ids"].extend(row["id"] for row in rows)

    heldout_rows: list[dict] = []
    for subset in HELDOUT_DATASETS:
        rows = [{**row, "role": "held_out_test", "source_subset": subset, "internal_split": "heldout"} for row in datasets[subset]]
        heldout_rows.extend(rows)
        split_manifest["counts"][subset] = {"total": len(rows)}
        split_manifest["heldout_ids"].extend(row["id"] for row in rows)

    return split_manifest, public_rows + heldout_rows


def ensure_atlas() -> dict:
    atlas_jsonl = proof_atlas.DEFAULT_OUT_DIR / "proof_atlas.jsonl"
    if not atlas_jsonl.exists():
        proof_atlas.build_pipeline(
            out_dir=proof_atlas.DEFAULT_OUT_DIR,
            cheatsheet_path=proof_atlas.DEFAULT_CHEATSHEET_PATH,
            sample_size=12,
            seed=20260326,
            run_eval=False,
        )
    atlas_records = [json.loads(line) for line in atlas_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    equation_metadata = load_json(proof_atlas.DEFAULT_OUT_DIR / "equation_metadata.json")
    raw_entries = proof_atlas.load_json_gz(proof_atlas.EXPORT_DIR / "general_raw_full_entries.json.gz")
    general = proof_atlas.load_json_gz(proof_atlas.EXPORT_DIR / "general.json.gz")
    outcomes = proof_atlas.load_json_gz(proof_atlas.EXPORT_DIR / "general_outcomes.json.gz")
    text_to_equation_id = {
        proof_atlas.normalize_equation_text(meta["text"]): equation_id
        for equation_id, meta in equation_metadata.items()
    }
    return {
        "atlas_records": atlas_records,
        "atlas_by_id": {row["family_id"]: row for row in atlas_records},
        "equation_metadata": equation_metadata,
        "text_to_equation_id": text_to_equation_id,
        "raw_entries": raw_entries,
        "general": general,
        "outcomes": outcomes,
        "explicit_adjacency": proof_atlas.build_explicit_adjacency(general["implications"]),
    }


def prompt_safe_family(record: dict) -> bool:
    family_id = record["family_id"]
    if family_id in {"closure_transitive", "closure_dual"}:
        return False
    base_family = record.get("base_family")
    if base_family in {"hard_case", "automated_reasoner"}:
        return False
    return bool(record.get("cheatsheet_rule"))


def index_public_pairs_by_family(target_pairs: set[tuple[str, str]], raw_entries: list[dict]) -> dict[tuple[str, str], list[str]]:
    rhs_by_lhs: dict[str, set[str]] = defaultdict(set)
    for lhs, rhs in target_pairs:
        rhs_by_lhs[lhs].add(rhs)

    pair_to_families: dict[tuple[str, str], set[str]] = defaultdict(set)
    for entry in raw_entries:
        variant_key = next(iter(entry["variant"]))
        variant = entry["variant"][variant_key]
        polarity = "true" if variant_key == "implication" else "false"
        scope = "finite" if variant.get("finite") or variant.get("facts", {}).get("finite") else "general"
        family_id = proof_atlas.family_key(proof_atlas.classify_entry(entry), polarity, scope)

        if variant_key == "implication":
            pair = (variant["lhs"], variant["rhs"])
            if pair in target_pairs:
                pair_to_families[pair].add(family_id)
            continue

        refs = set(variant["refuted"])
        for lhs in variant["satisfied"]:
            overlap = refs & rhs_by_lhs.get(lhs, set())
            for rhs in overlap:
                pair_to_families[(lhs, rhs)].add(family_id)

    return {pair: sorted(families) for pair, families in pair_to_families.items()}


def find_closure_explanation(eq1_id: str, eq2_id: str, atlas_ctx: dict) -> tuple[list[str], Optional[dict]]:
    path = proof_atlas.bfs_path(atlas_ctx["explicit_adjacency"], eq1_id, eq2_id)
    if path:
        return ["closure_transitive"], {"family_id": "closure_transitive", "path": path}
    dual_map = {meta["equation_id"]: meta["dual_equation_id"] for meta in atlas_ctx["equation_metadata"].values()}
    dual_lhs = dual_map.get(eq1_id)
    dual_rhs = dual_map.get(eq2_id)
    if dual_lhs and dual_rhs:
        dual_path = proof_atlas.bfs_path(atlas_ctx["explicit_adjacency"], dual_lhs, dual_rhs)
        if dual_path:
            return ["closure_dual"], {
                "family_id": "closure_dual",
                "path": dual_path,
                "dual_lhs": dual_lhs,
                "dual_rhs": dual_rhs,
            }
    return [], None


def infer_problem_families(problem: dict, atlas_ctx: dict, pair_family_index: dict[tuple[str, str], list[str]]) -> dict:
    eq1_text = proof_atlas.normalize_equation_text(problem["equation1"])
    eq2_text = proof_atlas.normalize_equation_text(problem["equation2"])
    eq1_id = atlas_ctx["text_to_equation_id"].get(eq1_text)
    eq2_id = atlas_ctx["text_to_equation_id"].get(eq2_text)
    meta1 = atlas_ctx["equation_metadata"].get(eq1_id) if eq1_id else None
    meta2 = atlas_ctx["equation_metadata"].get(eq2_id) if eq2_id else None
    features = distill.extract_pair_features(eq1_text, eq2_text)
    verified_witnesses = distill.find_verified_witnesses(eq1_text, eq2_text)
    outcome_status = None
    if eq1_id and eq2_id:
        outcome_status = atlas_ctx["outcomes"]["outcomes"][int(eq1_id.replace("Equation", "")) - 1][int(eq2_id.replace("Equation", "")) - 1]

    likely_family_ids = set(pair_family_index.get((eq1_id, eq2_id), []))
    closure_trace = None
    if problem["answer"] is True:
        lhs1, rhs1 = proof_atlas.split_equation(eq1_text)
        if lhs1 == "x" and "x" not in distill._var_tokens(rhs1):
            likely_family_ids.add("singleton_rewrite:true:general")
        if eq1_id and eq2_id and not likely_family_ids:
            closure_families, closure_trace = find_closure_explanation(eq1_id, eq2_id, atlas_ctx)
            likely_family_ids.update(closure_families)
        if eq1_id and eq2_id and outcome_status and outcome_status.endswith("_true"):
            likely_family_ids.add("rewrite_metatheorem:true:general")
    else:
        if features["new_vars_in_e2"] or features["lp_obstruction"] or features["rp_obstruction"]:
            likely_family_ids.add("projection_family_counterexamples:false:general")
        if verified_witnesses:
            if any(fam.startswith("all4x4_table_counterexamples:") for fam in likely_family_ids):
                pass
            elif any(fam.startswith("central_groupoid_counterexamples:") for fam in likely_family_ids):
                pass
            else:
                likely_family_ids.add("small_finite_magma:false:finite")
        if not verified_witnesses and not likely_family_ids and outcome_status and outcome_status.endswith("_false"):
            likely_family_ids.add("canonizer_confluence:false:general")

    if not likely_family_ids:
        likely_family_ids.add(f"hard_case:{'true' if problem['answer'] else 'false'}:general")

    atlas_by_id = atlas_ctx["atlas_by_id"]
    answer_aligned = [
        fam for fam in sorted(likely_family_ids)
        if (fam in {"closure_transitive", "closure_dual"} and problem["answer"] is True)
        or atlas_by_id.get(fam, {}).get("polarity") == ("true" if problem["answer"] else "false")
    ]
    prompt_safe = [fam for fam in answer_aligned if fam in atlas_by_id and prompt_safe_family(atlas_by_id[fam])]

    return {
        "problem_id": problem["id"],
        "source_subset": problem["source_subset"],
        "role": problem["role"],
        "internal_split": problem["internal_split"],
        "difficulty": problem.get("difficulty"),
        "answer": bool(problem["answer"]),
        "equation1": eq1_text,
        "equation2": eq2_text,
        "equation1_id": eq1_id,
        "equation2_id": eq2_id,
        "equation1_meta": {
            "equation_id": meta1["equation_id"],
            "equivalence_class_representative": meta1["equivalence_class_representative"],
            "equivalence_class_size": meta1["equivalence_class_size"],
            "is_literal_x_target": meta1["is_literal_x_target"],
            "dual_equation_id": meta1["dual_equation_id"],
        } if meta1 else None,
        "equation2_meta": {
            "equation_id": meta2["equation_id"],
            "equivalence_class_representative": meta2["equivalence_class_representative"],
            "equivalence_class_size": meta2["equivalence_class_size"],
            "is_literal_x_target": meta2["is_literal_x_target"],
            "dual_equation_id": meta2["dual_equation_id"],
        } if meta2 else None,
        "outcome_status": outcome_status,
        "shape_flags": {
            "eq1_literal_x_target": bool(meta1 and meta1["is_literal_x_target"]),
            "eq2_literal_x_target": bool(meta2 and meta2["is_literal_x_target"]),
            "fresh_variables_in_e2": features["new_vars_in_e2"],
            "lp_obstruction": features["lp_obstruction"],
            "rp_obstruction": features["rp_obstruction"],
            "verified_witness_names": [item["name"] for item in verified_witnesses],
        },
        "features": features,
        "verified_witnesses": verified_witnesses,
        "likely_family_ids": sorted(likely_family_ids),
        "answer_aligned_family_ids": answer_aligned,
        "prompt_safe_family_ids": prompt_safe,
        "closure_trace": closure_trace,
        "unresolved": len(answer_aligned) == 0,
    }


def build_public_family_report(alignments: list[dict], atlas_ctx: dict) -> dict:
    report: dict[str, dict] = {}
    for family_id, record in atlas_ctx["atlas_by_id"].items():
        report[family_id] = {
            "family_id": family_id,
            "title": record["title"],
            "prompt_safe": prompt_safe_family(record),
            "aligned_problem_count": 0,
            "true_problem_count": 0,
            "false_problem_count": 0,
            "train_problem_count": 0,
            "dev_problem_count": 0,
            "sample_problem_ids": [],
            "public_failure_opportunity_count": None,
        }
    for family_id in ["closure_transitive", "closure_dual"]:
        report.setdefault(family_id, {
            "family_id": family_id,
            "title": family_id,
            "prompt_safe": False,
            "aligned_problem_count": 0,
            "true_problem_count": 0,
            "false_problem_count": 0,
            "train_problem_count": 0,
            "dev_problem_count": 0,
            "sample_problem_ids": [],
            "public_failure_opportunity_count": None,
        })
    for alignment in alignments:
        if alignment["role"] != "train_corpus":
            continue
        for family_id in alignment["answer_aligned_family_ids"]:
            item = report.setdefault(family_id, {
                "family_id": family_id,
                "title": family_id,
                "prompt_safe": False,
                "aligned_problem_count": 0,
                "true_problem_count": 0,
                "false_problem_count": 0,
                "train_problem_count": 0,
                "dev_problem_count": 0,
                "sample_problem_ids": [],
                "public_failure_opportunity_count": None,
            })
            item["aligned_problem_count"] += 1
            if alignment["answer"]:
                item["true_problem_count"] += 1
            else:
                item["false_problem_count"] += 1
            if alignment["internal_split"] == "train":
                item["train_problem_count"] += 1
            elif alignment["internal_split"] == "dev":
                item["dev_problem_count"] += 1
            if len(item["sample_problem_ids"]) < 5:
                item["sample_problem_ids"].append(alignment["problem_id"])
    ranked = sorted(report.values(), key=lambda row: (-row["aligned_problem_count"], row["family_id"]))
    return {"families": ranked}


def family_report_index(report: dict) -> dict[str, dict]:
    return {row["family_id"]: row for row in report["families"]}


def build_rule_catalog(report: dict, atlas_ctx: dict) -> dict[str, dict]:
    report_by_family = family_report_index(report)
    rules: dict[str, dict] = {}

    def register_rule(
        rule_id: str,
        text: str,
        family_ids: list[str],
        section: str,
        internal_family_ids: Optional[list[str]] = None,
    ) -> None:
        internal_family_ids = internal_family_ids or []
        rules[rule_id] = {
            "rule_id": rule_id,
            "text": text,
            "family_ids": family_ids,
            "internal_family_ids": internal_family_ids,
            "section": section,
            "public_alignment_count": sum(report_by_family.get(family_id, {}).get("aligned_problem_count", 0) for family_id in family_ids),
            "internal_alignment_count": sum(report_by_family.get(family_id, {}).get("aligned_problem_count", 0) for family_id in internal_family_ids),
        }

    for family_id, record in atlas_ctx["atlas_by_id"].items():
        if not prompt_safe_family(record):
            continue
        section = "true_families" if record["polarity"] == "true" else "refutation_families"
        if record.get("base_family") == "singleton_rewrite":
            section = "fast_eliminators"
        if record.get("base_family") == "exceptional_hard" and report_by_family.get(family_id, {}).get("aligned_problem_count", 0) <= 0:
            continue
        rule_text = record["cheatsheet_rule"]
        if family_id == "singleton_rewrite:true:general":
            rule_text = "[F01 singleton_rewrite] If E1 is literally x = T and x is absent from T, use that singleton-strength collapse explicitly and answer TRUE."
        elif family_id == "projection_family_counterexamples:false:general":
            rule_text = "[F10 projection_family] If E1 preserves the left or right boundary variable and E2 breaks it, test LP/RP immediately; if one separates, answer FALSE with that named witness."
        elif family_id == "small_finite_magma:false:finite":
            rule_text = "[F11 small_finite_magma] After LP/RP, try compact witnesses in a fixed ladder (C0, XOR, XNOR, AND, OR); FALSE needs one named magma and assignment showing E1 true, E2 false."
        elif family_id == "all4x4_table_counterexamples:false:finite":
            rule_text = "[F13 all4x4_tables] Use 4x4 tables only as an escalation after easier witnesses fail, and still report one explicit separating table/assignment."
        elif family_id == "rewrite_metatheorem:true:general":
            rule_text = "[F20 rewrite_metatheorem] Answer TRUE only from an explicit substitution or short rewrite chain from E1 to E2; variable-count similarity or failed witness search is not enough."
        elif family_id == "canonizer_confluence:false:general":
            rule_text = "[F30 canonizer_confluence] Use this FALSE lane only when you can name the invariant or normal-form feature that E1 preserves and E2 breaks."
        register_rule(
            rule_id=f"family::{family_id}",
            text=rule_text,
            family_ids=[family_id],
            section=section,
        )

    supplemental = [
        ("supp::fresh_var", "[S01 fresh_var] If E2 introduces fresh variables not in E1, treat that as a FALSE-search trigger: test LP/RP first and do not drift into a TRUE guess from shape alone.", ["projection_family_counterexamples:false:general", "small_finite_magma:false:finite"], "fast_eliminators", []),
        ("supp::projection_first", "[S02 projection_first] When left/right boundary variables differ, test LP then RP before any broader finite witness search.", ["projection_family_counterexamples:false:general"], "refutation_families", []),
        ("supp::structured_finite", "[S03 structured_finite] Only after LP/RP and canned witnesses fail should you escalate to 4x4 or structured finite tables; still report one explicit witness.", ["all4x4_table_counterexamples:false:finite"], "refutation_families", []),
        ("supp::anti_fake_false", "[S04 anti_fake_false] FALSE requires one explicit witness, with a named operation or table and an assignment/check showing E1 holds and E2 fails.", ["small_finite_magma:false:finite", "projection_family_counterexamples:false:general"], "blockers", []),
        ("supp::anti_fake_true", "[S05 anti_fake_true] TRUE requires an exact rewrite chain, singleton-strength collapse, or exact closure chain; 'no witness found' is never enough.", ["rewrite_metatheorem:true:general", "singleton_rewrite:true:general"], "blockers", ["closure_transitive"]),
        ("supp::finite_scope", "[S06 finite_scope] Never promote a finite-only counterexample family into a general implication claim.", ["small_finite_magma:false:finite", "all4x4_table_counterexamples:false:finite"], "blockers", []),
        ("supp::closure_exact", "[S07 closure_exact] Closure language is only safe when you can name the exact backbone step or chain carrying E1 to E2; otherwise fall back to a direct rewrite.", ["rewrite_metatheorem:true:general"], "true_families", ["closure_transitive"]),
        ("supp::rewrite_chain", "[S08 rewrite_chain] For TRUE, write a short concrete substitution/rewrite chain, not broad algebraic commentary.", ["rewrite_metatheorem:true:general"], "true_families", []),
        ("supp::projection_witness", "[S09 projection_witness] If LP or RP satisfies E1 but falsifies E2, stop there and output FALSE with that named witness and assignment.", ["projection_family_counterexamples:false:general"], "refutation_families", []),
        ("supp::finite_ladder", "[S10 finite_ladder] If projection fails, try C0, XOR, XNOR, AND, OR in that order and keep the first explicit separating witness.", ["small_finite_magma:false:finite"], "refutation_families", []),
        ("supp::fresh_var_true_guard", "[S11 fresh_var_true_guard] Fresh variables in E2 do not block TRUE if you can explicitly derive E2 from E1; without that derivation, stay in FALSE-search mode.", ["rewrite_metatheorem:true:general"], "true_families", ["closure_transitive"]),
        ("supp::canonizer_guard", "[S12 canonizer_guard] Use canonizer/confluence only with a named invariant or normal-form mismatch that E1 preserves and E2 breaks.", ["canonizer_confluence:false:general"], "refutation_families", []),
    ]
    for rule_id, text, family_ids, section, internal_family_ids in supplemental:
        register_rule(rule_id, text, family_ids, section, internal_family_ids=internal_family_ids)
    return rules


def ranked_family_ids(report: dict, atlas_ctx: dict, polarity: str) -> list[str]:
    items = []
    for row in report["families"]:
        family_id = row["family_id"]
        record = atlas_ctx["atlas_by_id"].get(family_id)
        if not record or not prompt_safe_family(record):
            continue
        if record["polarity"] != polarity:
            continue
        if row["aligned_problem_count"] <= 0:
            continue
        items.append((row["aligned_problem_count"], record.get("priority", 0), family_id))
    items.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [item[2] for item in items]


def build_bundle_catalog(report: dict, alignments: list[dict], atlas_ctx: dict) -> list[dict]:
    report_by_family = family_report_index(report)
    problem_ids_by_family: dict[str, set[str]] = defaultdict(set)
    for row in alignments:
        if row["role"] != "train_corpus":
            continue
        for family_id in row["answer_aligned_family_ids"]:
            problem_ids_by_family[family_id].add(row["problem_id"])

    bundle_defs = [
        {
            "bundle_id": "false_witness_routing",
            "title": "False Witness Routing",
            "description": "Projection and fresh-variable cues dominate FALSE search and should terminate early when LP/RP separates.",
            "rule_ids": [
                "supp::fresh_var",
                "family::projection_family_counterexamples:false:general",
                "supp::projection_first",
                "supp::projection_witness",
                "supp::anti_fake_false",
            ],
            "family_ids": [
                "projection_family_counterexamples:false:general",
                "small_finite_magma:false:finite",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "finite_witness_core",
            "title": "Finite Witness Core",
            "description": "Compact explicit finite witnesses cover most remaining public FALSE cases once projection is checked.",
            "rule_ids": [
                "family::small_finite_magma:false:finite",
                "supp::finite_ladder",
                "supp::finite_scope",
            ],
            "family_ids": [
                "small_finite_magma:false:finite",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "finite_witness_escalation",
            "title": "Finite Witness Escalation",
            "description": "A small tail of FALSE cases needs structured finite tables after the compact witness ladder fails.",
            "rule_ids": [
                "supp::structured_finite",
                "family::all4x4_table_counterexamples:false:finite",
            ],
            "family_ids": [
                "all4x4_table_counterexamples:false:finite",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "invariant_false_lane",
            "title": "Invariant False Lane",
            "description": "Canonizer and invariant-based refutations are real, but only safe when the invariant is stated concretely.",
            "rule_ids": [
                "family::canonizer_confluence:false:general",
                "supp::canonizer_guard",
            ],
            "family_ids": [
                "canonizer_confluence:false:general",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "safe_true_core",
            "title": "Safe True Core",
            "description": "Most public TRUE cases are rewrite-backed and should be expressed as explicit short derivations.",
            "rule_ids": [
                "family::rewrite_metatheorem:true:general",
                "supp::anti_fake_true",
                "supp::rewrite_chain",
            ],
            "family_ids": [
                "rewrite_metatheorem:true:general",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "singleton_shortcut",
            "title": "Singleton Shortcut",
            "description": "Singleton-strength E1 equations give a high-yield, low-risk TRUE shortcut when applied literally.",
            "rule_ids": [
                "family::singleton_rewrite:true:general",
            ],
            "family_ids": [
                "singleton_rewrite:true:general",
            ],
            "internal_family_ids": [],
        },
        {
            "bundle_id": "closure_guardrails",
            "title": "Closure Guardrails",
            "description": "Closure facts are real on the public corpus, but the prompt should only allow exact, traceable closure references.",
            "rule_ids": [
                "supp::closure_exact",
            ],
            "family_ids": [
                "rewrite_metatheorem:true:general",
            ],
            "internal_family_ids": [
                "closure_transitive",
            ],
        },
        {
            "bundle_id": "fresh_var_true_override",
            "title": "Fresh-Variable True Override",
            "description": "Fresh variables should bias search toward FALSE, but they do not block TRUE when there is an exact derivation.",
            "rule_ids": [
                "supp::fresh_var_true_guard",
            ],
            "family_ids": [
                "rewrite_metatheorem:true:general",
            ],
            "internal_family_ids": [
                "closure_transitive",
            ],
        },
    ]

    annotated: list[dict] = []
    for item in bundle_defs:
        prompt_count = sum(report_by_family.get(family_id, {}).get("aligned_problem_count", 0) for family_id in item["family_ids"])
        internal_count = sum(report_by_family.get(family_id, {}).get("aligned_problem_count", 0) for family_id in item["internal_family_ids"])
        union_ids: set[str] = set()
        for family_id in (*item["family_ids"], *item["internal_family_ids"]):
            union_ids.update(problem_ids_by_family.get(family_id, set()))
        annotated.append({
            **item,
            "public_alignment_count": prompt_count,
            "internal_alignment_count": internal_count,
            "union_problem_count": len(union_ids),
            "evidence_families": [
                {
                    "family_id": family_id,
                    "aligned_problem_count": report_by_family.get(family_id, {}).get("aligned_problem_count", 0),
                    "prompt_safe": report_by_family.get(family_id, {}).get("prompt_safe", False),
                }
                for family_id in item["family_ids"]
            ],
            "internal_only_families": [
                {
                    "family_id": family_id,
                    "aligned_problem_count": report_by_family.get(family_id, {}).get("aligned_problem_count", 0),
                    "prompt_safe": report_by_family.get(family_id, {}).get("prompt_safe", False),
                }
                for family_id in item["internal_family_ids"]
            ],
        })
    annotated.sort(key=lambda row: (-row["union_problem_count"], row["bundle_id"]))
    return annotated


def select_variant_bundle_ids(variant_name: str) -> list[str]:
    bundle_ids = [
        "false_witness_routing",
        "finite_witness_core",
        "invariant_false_lane",
        "safe_true_core",
        "singleton_shortcut",
        "closure_guardrails",
    ]
    if variant_name == "false_recall_boost":
        bundle_ids.append("finite_witness_escalation")
    elif variant_name == "true_support_boost":
        bundle_ids.append("fresh_var_true_override")
    return bundle_ids


def select_variant_rule_ids(variant_name: str, bundle_catalog: list[dict], rules: dict[str, dict]) -> tuple[list[str], list[str]]:
    selected_bundle_ids = select_variant_bundle_ids(variant_name)
    bundle_by_id = {row["bundle_id"]: row for row in bundle_catalog}
    deduped: list[str] = []
    for bundle_id in selected_bundle_ids:
        for rule_id in bundle_by_id[bundle_id]["rule_ids"]:
            if rule_id in rules and rule_id not in deduped:
                deduped.append(rule_id)
    return deduped, selected_bundle_ids


def render_variant_prompt(rule_ids: list[str], rules: dict[str, dict]) -> tuple[str, list[dict]]:
    sections = {
        "fast_eliminators": [],
        "refutation_families": [],
        "true_families": [],
        "blockers": [],
    }
    selected_rules: list[dict] = []
    for rule_id in rule_ids:
        rule = rules[rule_id]
        sections[rule["section"]].append(rule["text"])
        selected_rules.append(rule)

    lines = [
        "E1 is {{ equation1 }} and E2 is {{ equation2 }}",
        "",
        "OUTPUT LOCK",
        "- First line: VERDICT: TRUE or VERDICT: FALSE",
        "- Then brief REASONING, PROOF, COUNTEREXAMPLE.",
        "- FALSE requires a named witness with assignment/check.",
        "- TRUE requires a concrete rewrite, singleton-strength reason, or exact closure argument.",
        "",
        "FAST ELIMINATORS",
    ]
    lines.extend(sections["fast_eliminators"])
    lines.extend(["", "REFUTATION FAMILIES"])
    lines.extend(sections["refutation_families"])
    lines.extend(["", "TRUE FAMILIES"])
    lines.extend(sections["true_families"])
    lines.extend(["", "BLOCKERS"])
    lines.extend(sections["blockers"])
    return "\n".join(lines).strip() + "\n", selected_rules


def aggregate_result_payloads(payloads: list[dict]) -> dict:
    totals = Counter()
    elapsed_total = 0.0
    for payload in payloads:
        summary = payload["summary"]
        for key in ["total", "correct", "incorrect", "unparsed", "tp", "fp", "fn", "tn", "prompt_tokens", "completion_tokens", "reasoning_tokens"]:
            totals[key] += int(summary.get(key, 0))
        elapsed_total += float(summary.get("total_time_s", 0.0))
    total = totals["total"]
    tp, fp, fn = totals["tp"], totals["fp"], totals["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "total": total,
        "accuracy": totals["correct"] / total if total else 0.0,
        "f1_score": 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0,
        "precision": precision,
        "recall": recall,
        "parse_success_rate": (total - totals["unparsed"]) / total if total else 0.0,
        "true_accuracy": tp / (tp + fn) if (tp + fn) else 0.0,
        "false_accuracy": totals["tn"] / (totals["tn"] + fp) if (totals["tn"] + fp) else 0.0,
        "avg_time_s": elapsed_total / total if total else 0.0,
        "prompt_tokens": totals["prompt_tokens"],
        "completion_tokens": totals["completion_tokens"],
        "reasoning_tokens": totals["reasoning_tokens"],
    }


def run_sim_eval(dataset_path: Path, cheatsheet_path: Path, output_path: Path) -> dict:
    command = [
        sys.executable,
        str(ROOT / "sim_lab.py"),
        "--data", str(dataset_path),
        "--cheatsheet", str(cheatsheet_path),
        "--openrouter",
        "--quiet",
        "--output", str(output_path),
    ]
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=3600,
    )
    return {
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-800:],
        "stderr_tail": completed.stderr[-800:],
        "output_path": str(output_path),
    }


def qualifies_for_heldout(candidate_metrics: dict, baseline_metrics: list[dict], byte_size: int) -> bool:
    if byte_size > 10_240 or not baseline_metrics:
        return False
    best_accuracy = max(item["accuracy"] for item in baseline_metrics)
    best_f1 = max(item["f1_score"] for item in baseline_metrics)
    best_parse = max(item["parse_success_rate"] for item in baseline_metrics)
    return (
        candidate_metrics["parse_success_rate"] >= best_parse - 1e-6
        and candidate_metrics["accuracy"] >= best_accuracy - 0.005
        and candidate_metrics["f1_score"] >= best_f1
    )


def build_public_workflow(out_dir: Path, variant_dir: Path, dev_ratio: float, seed: int, evaluate_public: bool, evaluate_heldout: bool) -> dict:
    datasets = load_all_problem_sets()
    split_manifest, all_rows = build_dataset_split(datasets, dev_ratio=dev_ratio, seed=seed)
    atlas_ctx = ensure_atlas()

    public_pairs = set()
    for row in all_rows:
        eq1_id = atlas_ctx["text_to_equation_id"].get(proof_atlas.normalize_equation_text(row["equation1"]))
        eq2_id = atlas_ctx["text_to_equation_id"].get(proof_atlas.normalize_equation_text(row["equation2"]))
        if eq1_id and eq2_id:
            public_pairs.add((eq1_id, eq2_id))
    pair_family_index = index_public_pairs_by_family(public_pairs, atlas_ctx["raw_entries"])

    alignments = [infer_problem_families(row, atlas_ctx, pair_family_index) for row in all_rows]
    public_report = build_public_family_report(alignments, atlas_ctx)
    bundle_catalog = build_bundle_catalog(public_report, alignments, atlas_ctx)
    rules = build_rule_catalog(public_report, atlas_ctx)
    bundle_by_id = {row["bundle_id"]: row for row in bundle_catalog}
    variant_dir.mkdir(parents=True, exist_ok=True)
    variants: list[dict] = []
    for variant_name in ["core_balanced", "false_recall_boost", "true_support_boost"]:
        rule_ids, selected_bundle_ids = select_variant_rule_ids(variant_name, bundle_catalog, rules)
        prompt_text, selected_rules = render_variant_prompt(rule_ids, rules)
        prompt_path = variant_dir / f"competition_v2_{variant_name}.txt"
        prompt_path.write_text(prompt_text, encoding="utf-8", newline="\n")
        selected_family_ids = sorted({family_id for rule in selected_rules for family_id in rule["family_ids"]})
        selected_internal_family_ids = sorted({family_id for rule in selected_rules for family_id in rule.get("internal_family_ids", [])})
        variants.append({
            "name": variant_name,
            "path": str(prompt_path),
            "selected_bundle_ids": selected_bundle_ids,
            "selected_bundles": [bundle_by_id[bundle_id] for bundle_id in selected_bundle_ids],
            "selected_rule_ids": rule_ids,
            "selected_family_ids": selected_family_ids,
            "selected_internal_family_ids": selected_internal_family_ids,
            "selected_rules": [
                {
                    "rule_id": rule["rule_id"],
                    "text": rule["text"],
                    "family_ids": rule["family_ids"],
                    "internal_family_ids": rule.get("internal_family_ids", []),
                    "public_alignment_count": rule["public_alignment_count"],
                    "internal_alignment_count": rule["internal_alignment_count"],
                }
                for rule in selected_rules
            ],
            "byte_size": prompt_path.stat().st_size,
            "fits_budget": prompt_path.stat().st_size <= 10_240,
            "public_eval_metrics": None,
            "heldout_eval": {},
            "qualifies_for_heldout": False,
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "dataset_split.json", split_manifest)
    write_jsonl(out_dir / "public_corpus_alignment.jsonl", [row for row in alignments if row["role"] == "train_corpus"])
    write_json(out_dir / "public_corpus_family_report.json", public_report)

    md_lines = [
        "# Public Corpus Family Report",
        "",
        "## Dataset Policy",
        "",
        f"- Train corpus: {', '.join(PUBLIC_DATASETS)}",
        f"- Held-out test: {', '.join(HELDOUT_DATASETS)}",
        f"- Dev ratio: {dev_ratio}",
        "",
        "## Ranked Families",
        "",
    ]
    for row in public_report["families"][:30]:
        md_lines.append(f"### {row['family_id']}")
        md_lines.append(f"- Prompt safe: {row['prompt_safe']}")
        md_lines.append(f"- Aligned problems: {row['aligned_problem_count']}")
        md_lines.append(f"- TRUE / FALSE: {row['true_problem_count']} / {row['false_problem_count']}")
        md_lines.append(f"- Internal train / dev: {row['train_problem_count']} / {row['dev_problem_count']}")
        md_lines.append(f"- Samples: {row['sample_problem_ids']}")
        md_lines.append("")
    md_lines.extend([
        "## Ranked Rule Bundles",
        "",
    ])
    for row in bundle_catalog:
        md_lines.append(f"### {row['bundle_id']}")
        md_lines.append(f"- Union problems covered: {row['union_problem_count']}")
        md_lines.append(f"- Prompt-family alignments: {row['public_alignment_count']}")
        md_lines.append(f"- Internal-only alignments: {row['internal_alignment_count']}")
        md_lines.append(f"- Prompt evidence families: {[item['family_id'] for item in row['evidence_families']]}")
        md_lines.append(f"- Internal-only families: {[item['family_id'] for item in row['internal_only_families']]}")
        md_lines.append("")
    (out_dir / "public_corpus_family_report.md").write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")

    eval_manifest = {
        "public_evaluation": {"executed": False, "datasets": list(PUBLIC_DATASETS), "results": []},
        "heldout_evaluation": {"executed": False, "datasets": list(HELDOUT_DATASETS), "results": []},
    }
    baseline_paths = {
        "v19_noncollapse": ROOT / "cheatsheets" / "v19_noncollapse.txt",
        "v13_proof_required": ROOT / "cheatsheets" / "v13_proof_required.txt",
    }
    if evaluate_public and os.environ.get("OPENROUTER_API_KEY"):
        eval_manifest["public_evaluation"]["executed"] = True
        public_metrics: dict[str, dict] = {}
        for label, path in {**baseline_paths, **{item["name"]: Path(item["path"]) for item in variants}}.items():
            payloads = []
            for dataset_name in PUBLIC_DATASETS:
                output_path = out_dir / "evals" / "public" / f"{label}__{dataset_name}.json"
                run_record = run_sim_eval(HF_CACHE_DIR / f"{dataset_name}.jsonl", path, output_path)
                run_record["dataset"] = dataset_name
                eval_manifest["public_evaluation"]["results"].append({"label": label, **run_record})
                if run_record["returncode"] == 0 and Path(run_record["output_path"]).exists():
                    payloads.append(load_json(Path(run_record["output_path"])))
            if payloads:
                public_metrics[label] = aggregate_result_payloads(payloads)

        baseline_metrics = [metrics for label, metrics in public_metrics.items() if label in baseline_paths]
        for item in variants:
            metrics = public_metrics.get(item["name"])
            item["public_eval_metrics"] = metrics
            if metrics:
                item["qualifies_for_heldout"] = qualifies_for_heldout(metrics, baseline_metrics, item["byte_size"])

        if evaluate_heldout:
            eval_manifest["heldout_evaluation"]["executed"] = True
            for item in variants:
                if not item["qualifies_for_heldout"]:
                    continue
                candidate_path = Path(item["path"])
                hard2_output = out_dir / "evals" / "heldout" / f"{item['name']}__hard2.json"
                hard2_run = run_sim_eval(HF_CACHE_DIR / "hard2.jsonl", candidate_path, hard2_output)
                eval_manifest["heldout_evaluation"]["results"].append({"label": item["name"], "stage": "hard2", **hard2_run})
                if hard2_run["returncode"] == 0 and hard2_output.exists():
                    hard2_payload = load_json(hard2_output)
                    item["heldout_eval"]["hard2"] = aggregate_result_payloads([hard2_payload])
                    hard3_output = out_dir / "evals" / "heldout" / f"{item['name']}__hard3.json"
                    hard3_run = run_sim_eval(HF_CACHE_DIR / "hard3.jsonl", candidate_path, hard3_output)
                    eval_manifest["heldout_evaluation"]["results"].append({"label": item["name"], "stage": "hard3", **hard3_run})
                    if hard3_run["returncode"] == 0 and hard3_output.exists():
                        item["heldout_eval"]["hard3"] = aggregate_result_payloads([load_json(hard3_output)])

    previous_prompt_safe_family_ids = {
        "subgraph_seed:true:general",
        "linear_translation:false:finite",
        "central_groupoid_counterexamples:false:general",
        "rewrite_metatheorem:false:general",
        "exceptional_hard:false:general",
    }
    active_family_ids = {family_id for item in variants for family_id in item["selected_family_ids"]}
    write_json(out_dir / "variant_decisions.json", {
        "bundle_catalog": bundle_catalog,
        "family_decisions": {
            "strengthened_family_ids": sorted(active_family_ids),
            "removed_from_prompt_family_ids": sorted(previous_prompt_safe_family_ids - active_family_ids),
            "internal_only_family_ids": sorted({
                "closure_transitive",
                "closure_dual",
                "automated_reasoner:true:general",
                "hard_case:false:finite",
                "hard_case:false:general",
            }),
        },
        "variants": variants,
    })
    write_json(out_dir / "eval_manifest.json", eval_manifest)
    return {
        "split_manifest": split_manifest,
        "alignments": alignments,
        "public_report": public_report,
        "bundle_catalog": bundle_catalog,
        "variants": variants,
        "eval_manifest": eval_manifest,
        "out_dir": out_dir,
        "variant_dir": variant_dir,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atlas-guided prompt development over full normal + hard1 with held-out hard2 + hard3.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directory for public-corpus atlas development artifacts.")
    parser.add_argument("--variant-dir", default=str(DEFAULT_VARIANT_DIR), help="Directory for generated cheatsheet variants.")
    parser.add_argument("--dev-ratio", type=float, default=0.2, help="Internal dev split ratio inside normal + hard1.")
    parser.add_argument("--seed", type=int, default=20260326, help="Random seed for deterministic public/dev split.")
    parser.add_argument("--evaluate-public", action="store_true", help="Run full normal + hard1 evaluations for baselines and generated variants.")
    parser.add_argument("--evaluate-heldout", action="store_true", help="Run hard2 then hard3 for promoted generated variants.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_public_workflow(
        out_dir=Path(args.out_dir),
        variant_dir=Path(args.variant_dir),
        dev_ratio=args.dev_ratio,
        seed=args.seed,
        evaluate_public=args.evaluate_public,
        evaluate_heldout=args.evaluate_heldout,
    )
    public_alignment_count = sum(1 for row in result["alignments"] if row["role"] == "train_corpus")
    unresolved = sum(1 for row in result["alignments"] if row["role"] == "train_corpus" and row["unresolved"])
    print(f"Public corpus problems aligned: {public_alignment_count}")
    print(f"Public unresolved alignments: {unresolved}")
    print(f"Generated variants: {len(result['variants'])}")
    for variant in result["variants"]:
        print(f"  - {variant['name']}: {variant['byte_size']} bytes")
    print(f"Artifacts: {rel(result['out_dir'])}, {rel(result['variant_dir'])}")


if __name__ == "__main__":
    main()
