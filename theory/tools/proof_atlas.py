#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import scoreboard

ROOT = Path(__file__).resolve().parent
EXPORT_DIR = ROOT / "data" / "exports"
MANUAL_DISTILL_DIR = ROOT / "results" / "manual_distill"
DEFAULT_OUT_DIR = ROOT / "results" / "proof_atlas"
DEFAULT_CHEATSHEET_PATH = ROOT / "cheatsheets" / "generated_v2" / "cheatsheet_competition_v1.txt"
RULESET_PATH = ROOT / "RULESET.md"
CURRENT_MANIFEST_PATH = ROOT / "results" / "vnext_search_v2" / "champions" / "current.json"
EQUATION_RE = re.compile(r"Equation(\d+)")
VAR_RE = re.compile(r"\b([a-z])\b")


FAMILY_TEMPLATES: dict[str, dict] = {
    "singleton_rewrite": {
        "title": "Singleton Rewrite",
        "family_group": "rewrite/metatheorem families",
        "description": "Singleton-strength equations collapse the model immediately and are high-confidence TRUE sources.",
        "trigger_features": [
            "E1 literally has the form x = term",
            "x does not occur on the RHS of E1",
            "often lands in the large singleton equivalence class",
        ],
        "known_blockers": [
            "do not use when x still appears in the RHS",
            "do not promote approximate similarity into singleton strength",
        ],
        "paper_refs": ["paper/intro.tex", "paper/metatheorems.tex"],
        "cheatsheet_rule": "[F01 singleton_rewrite] If E1 is literally x = T and x is absent from T, treat E1 as singleton-strength and answer TRUE.",
        "priority": 100,
    },
    "rewrite_metatheorem": {
        "title": "Rewrite / Metatheorem",
        "family_group": "rewrite/metatheorem families",
        "description": "Direct substitution and trivial rewrite schemas cover a large fraction of explicit positive implications.",
        "trigger_features": [
            "syntactic weakening of E1 into E2",
            "single-step or bounded-step rewrite files",
            "trivial-bruteforce theorem provenance",
        ],
        "known_blockers": [
            "do not call a rewrite valid unless the concrete chain is visible",
            "structural resemblance alone is not a proof",
        ],
        "paper_refs": ["paper/intro.tex", "paper/metatheorems.tex"],
        "cheatsheet_rule": "[F20 rewrite_metatheorem] Prefer a short explicit rewrite/substitution chain; do not answer TRUE from prose alone.",
        "priority": 90,
    },
    "subgraph_seed": {
        "title": "Subgraph Seed Implications",
        "family_group": "rewrite/metatheorem families",
        "description": "Seed implications anchor the closure graph and often act as short canonical witnesses for broad regions of the graph.",
        "trigger_features": [
            "explicit subgraph theorem provenance",
            "basic backbone edges reused by transitive closure",
        ],
        "known_blockers": ["many downstream truths are closure facts, not standalone seed theorems"],
        "paper_refs": ["paper/foundations.tex", "paper/data.tex"],
        "cheatsheet_rule": "[F21 closure_awareness] Many TRUE implications are closure facts; if you invoke a backbone rule, state the exact symmetry or transitive step.",
        "priority": 60,
    },
    "automated_reasoner": {
        "title": "Automated Equational Reasoner",
        "family_group": "rewrite/metatheorem families",
        "description": "ATP and e-graph generated proofs contribute a sizable explicit theorem backbone even when the human summary should stay compact.",
        "trigger_features": [
            "VampireProven or MagmaEgg provenance",
            "syntactic or automated equational closure",
        ],
        "known_blockers": ["the cheatsheet should compress these into reusable patterns, not cite solver names as proof"],
        "paper_refs": ["paper/automated.tex", "paper/intro.tex"],
        "cheatsheet_rule": "[F22 automated_reasoner] If a truth looks solver-like, compress it into a concrete rewrite pattern instead of citing automation.",
        "priority": 55,
    },
    "canonizer_confluence": {
        "title": "Canonizer / Confluence",
        "family_group": "canonizers/free-magma arguments",
        "description": "Confluence and canonizer arguments preserve matching invariants and certify many FALSE implications without small finite witnesses.",
        "trigger_features": [
            "Confluence provenance",
            "matching invariant or canonizer signal",
            "free-magma / normal-form asymmetry",
        ],
        "known_blockers": [
            "do not use this lane unless the invariant is stated concretely",
            "avoid vague claims about normal forms or confluence",
        ],
        "paper_refs": ["paper/metatheorems.tex", "paper/intro.tex"],
        "cheatsheet_rule": "[F30 canonizer_confluence] If E1 preserves a concrete invariant that E2 breaks, that is a valid FALSE lane; otherwise do not bluff this family.",
        "priority": 75,
    },
    "linear_translation": {
        "title": "Linear / Translation-Invariant Countermodels",
        "family_group": "linear/translation-invariant constructions",
        "description": "Linear and translation-invariant constructions explain finite refutations that are resistant to tiny table witnesses.",
        "trigger_features": [
            "LinearOps provenance",
            "affine or translation-invariant construction",
            "finite-only countermodel scope",
        ],
        "known_blockers": [
            "finite-only constructions must not be promoted to general implications",
            "this is not the first refutation lane for easy pairs",
        ],
        "paper_refs": ["paper/constructions.tex", "paper/intro.tex"],
        "cheatsheet_rule": "[F14 linear_translation] Reserve linear/translation-style refutations for hard asymmetric pairs; never treat them as a generic proof shortcut.",
        "priority": 65,
    },
    "projection_family_counterexamples": {
        "title": "Projection / Absorption Counterexamples",
        "family_group": "projection/absorption families",
        "description": "Projection-style witnesses and leaf-anchoring asymmetries are the highest-yield FALSE families on the current benchmark trail.",
        "trigger_features": [
            "LP/RP obstruction",
            "leftmost or rightmost leaf mismatch",
            "fresh variables in E2",
        ],
        "known_blockers": [
            "FALSE still requires a named witness and concrete check",
            "projection cues are search priorities, not standalone proofs",
        ],
        "paper_refs": ["paper/spectrum.tex", "paper/intro.tex"],
        "cheatsheet_rule": "[F10 projection_family] If E1 preserves leftmost/rightmost x but E2 breaks it, check LP/RP before any TRUE fallback.",
        "priority": 98,
    },
    "small_finite_magma": {
        "title": "Small Finite Magma Counterexamples",
        "family_group": "small finite magma families",
        "description": "Explicit small magmas and compact witness tables cover most false implications and dominate current benchmark failures.",
        "trigger_features": [
            "small Cayley-table witness",
            "XOR/XNOR/C0/AND/OR style counterexamples",
            "manually sampled or Z3-assisted finite refutations",
        ],
        "known_blockers": [
            "the witness must show E1 holds and E2 fails on a concrete assignment",
            "do not report a family without the actual check",
        ],
        "paper_refs": ["paper/constructions.tex", "paper/intro.tex", "RULESET.md"],
        "cheatsheet_rule": "[F11 small_finite_magma] After LP/RP, try compact finite witnesses (C0, XOR, XNOR, AND, OR); FALSE requires one explicit magma and assignment.",
        "priority": 97,
    },
    "all4x4_table_counterexamples": {
        "title": "All4x4 Table Counterexamples",
        "family_group": "small finite magma families",
        "description": "Brute-force small-table counterexamples compress large banks of finite refutations that are especially valuable for FALSE coverage.",
        "trigger_features": [
            "All4x4Tables provenance",
            "explicit finite table macro refutations",
            "many refuted targets packed into one witness family",
        ],
        "known_blockers": [
            "finite-only tables must not be promoted to general claims",
            "keep this family as a witness source, not as free-form prose",
        ],
        "paper_refs": ["paper/constructions.tex", "paper/intro.tex", "RULESET.md"],
        "cheatsheet_rule": "[F13 all4x4_tables] Compact finite tables can refute many pairs at once; use them only as explicit FALSE witnesses, never as general proof claims.",
        "priority": 96,
    },
    "central_groupoid_counterexamples": {
        "title": "Central Groupoid Counterexamples",
        "family_group": "small finite magma families",
        "description": "Central-groupoid style finite constructions capture structured hard FALSE regions that are not well described by the smallest canned witnesses alone.",
        "trigger_features": [
            "CentralGroupoids or ThreeC2 provenance",
            "structured finite witness family beyond tiny canned tables",
        ],
        "known_blockers": [
            "treat as finite-only witness families",
            "do not compress these into vague algebraic jargon in the prompt",
        ],
        "paper_refs": ["paper/constructions.tex", "paper/conclusions.tex"],
        "cheatsheet_rule": "[F15 central_groupoid] Some hard FALSE pairs need structured finite witnesses beyond LP/RP/XOR; keep that lane explicit and finite-scoped.",
        "priority": 72,
    },
    "modified_lifted_magma": {
        "title": "Modified / Lifted Magma Families",
        "family_group": "modified/enlarged/extended magma constructions",
        "description": "Lifting, extension, and modification families package many refutations into macro counterexample objects.",
        "trigger_features": [
            "instLiftingMagmaFamily provenance",
            "base magma modified or extended to refute many targets",
        ],
        "known_blockers": ["compress as reusable witness families, not pair-by-pair anecdotes"],
        "paper_refs": ["paper/intro.tex", "paper/constructions.tex"],
        "cheatsheet_rule": "[F12 macro_counterexample] Facts-style counterexamples refute many targets at once; prefer reusable witness families over ad hoc prose.",
        "priority": 78,
    },
    "exceptional_hard": {
        "title": "Exceptional / Hard Cases",
        "family_group": "exceptional hard cases",
        "description": "Named constructions and residual hard files capture the pairs that resist easy rewrite and tiny finite-witness compression.",
        "trigger_features": [
            "Asterix/Austin/InfModel or equation-specific provenance",
            "immune or hard-case behavior",
        ],
        "known_blockers": [
            "do not overgeneralize from one named hard construction",
            "prefer conservative fallback when the family trigger is unclear",
        ],
        "paper_refs": ["paper/intro.tex", "paper/conclusions.tex", "paper/project.tex"],
        "cheatsheet_rule": "[F33 hard_case] If a pair resists the common families, stay conservative and do not invent a deep algebraic explanation.",
        "priority": 45,
    },
    "hard_case": {
        "title": "Unclassified Hard Bucket",
        "family_group": "exceptional hard cases",
        "description": "Fallback bucket for explicit entries that remain low-support or weakly classified after provenance analysis.",
        "trigger_features": ["unmatched theorem provenance", "low-support family assignment"],
        "known_blockers": ["this bucket exists to avoid false compression confidence"],
        "paper_refs": ["paper/conclusions.tex"],
        "cheatsheet_rule": "[F34 conservative_fallback] Unknown family means no compression shortcut; require a concrete witness or rewrite before committing.",
        "priority": 40,
    },
}


SYNTHETIC_FAMILIES = [
    {
        "family_id": "closure_transitive",
        "title": "Transitive Closure",
        "family_group": "closure/index layer",
        "polarity": "true",
        "scope": "general",
        "closure_mode": "transitive",
        "description": "Many TRUE pairs in the full matrix are derived by chaining explicit backbone implications.",
        "trigger_features": [
            "pair is TRUE in the outcomes matrix",
            "pair is not itself an explicit theorem edge",
            "a path exists through explicit theorem edges",
        ],
        "known_blockers": ["do not pretend the derived pair has its own standalone proof file"],
        "paper_refs": ["paper/foundations.tex", "paper/data.tex"],
        "canonical_exemplars": [],
        "supporting_theorems": [],
        "benchmark_relevance": {"score": 0, "signals": []},
        "entry_count": 0,
        "pair_count": 0,
        "macro_pair_capacity": 0,
    },
    {
        "family_id": "closure_dual",
        "title": "Duality Closure",
        "family_group": "closure/index layer",
        "polarity": "true",
        "scope": "general",
        "closure_mode": "dual",
        "description": "Duality transports proven implications across the opposite operation by reversing both sides of the laws.",
        "trigger_features": ["dual(lhs) -> dual(rhs) is explicit or transitively derivable"],
        "known_blockers": ["duality is exact structural symmetry, not loose resemblance"],
        "paper_refs": ["paper/foundations.tex", "paper/intro.tex"],
        "canonical_exemplars": [],
        "supporting_theorems": [],
        "benchmark_relevance": {"score": 0, "signals": []},
        "entry_count": 0,
        "pair_count": 0,
        "macro_pair_capacity": 0,
    },
]


@dataclass
class DSU:
    parent: list[int]
    size: list[int]

    @classmethod
    def build(cls, n: int) -> "DSU":
        return cls(parent=list(range(n)), size=[1] * n)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json_gz(path: Path) -> dict | list:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


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


def normalize_equation_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("â—‡", "*").replace("◇", "*")).strip()


def var_tokens(expr: str) -> list[str]:
    return VAR_RE.findall(expr)


def split_equation(eq: str) -> tuple[str, str]:
    parts = normalize_equation_text(eq).split(" = ", 1)
    if len(parts) != 2:
        return normalize_equation_text(eq), ""
    return parts[0].strip(), parts[1].strip()


def find_matching(expr: str, start: int) -> int:
    depth = 0
    for idx, char in enumerate(expr[start:], start=start):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return idx
    return -1


def parse_expr(expr: str):
    expr = expr.strip()
    if expr.startswith("(") and find_matching(expr, 0) == len(expr) - 1:
        expr = expr[1:-1].strip()
    depth = 0
    last_star = -1
    for idx, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "*" and depth == 0:
            last_star = idx
    if last_star >= 0:
        return ("*", parse_expr(expr[:last_star]), parse_expr(expr[last_star + 1:]))
    return ("var", expr)


def parse_equation_tree(eq: str):
    lhs, rhs = split_equation(eq)
    return parse_expr(lhs), parse_expr(rhs)


def tree_to_expr(tree) -> str:
    if tree[0] == "var":
        return tree[1]
    return f"({tree_to_expr(tree[1])} * {tree_to_expr(tree[2])})"


def dual_tree(tree):
    if tree[0] == "var":
        return tree
    return ("*", dual_tree(tree[2]), dual_tree(tree[1]))


def dualize_equation(eq: str) -> str:
    lhs, rhs = parse_equation_tree(eq)
    return normalize_equation_text(f"{tree_to_expr(dual_tree(lhs))} = {tree_to_expr(dual_tree(rhs))}")


def leftmost_leaf(expr: str) -> Optional[str]:
    tokens = var_tokens(expr)
    return tokens[0] if tokens else None


def rightmost_leaf(expr: str) -> Optional[str]:
    tokens = var_tokens(expr)
    return tokens[-1] if tokens else None


def is_literal_x_target(eq: str) -> bool:
    lhs, rhs = split_equation(eq)
    return lhs == "x" and rhs != ""


def multiplicities(eq: str) -> dict[str, int]:
    counts = Counter(var_tokens(eq))
    return {key: counts[key] for key in sorted(counts)}


def classify_entry(entry: dict) -> str:
    filename = entry["filename"].lower()
    name = entry["name"].lower()
    if "singleton" in filename:
        return "singleton_rewrite"
    if "generated/constant" in filename or filename.endswith("/constant.lean"):
        return "rewrite_metatheorem"
    if "trivialbruteforce" in filename:
        return "rewrite_metatheorem"
    if "subgraph.lean" in filename:
        return "subgraph_seed"
    if "magmaegg" in filename or "vampireproven" in filename:
        return "automated_reasoner"
    if "confluence" in filename or "canon" in name:
        return "canonizer_confluence"
    if "linearops" in filename:
        return "linear_translation"
    if "all4x4tables" in filename:
        return "all4x4_table_counterexamples"
    if "centralgroupoids" in filename:
        return "central_groupoid_counterexamples"
    if "finitepoly" in filename:
        return "small_finite_magma"
    if "instliftingmagmafamilyrightproj" in filename or "instliftingmagmafamilyleftproj" in filename:
        return "projection_family_counterexamples"
    if "instliftingmagmafamily" in filename:
        return "modified_lifted_magma"
    if "threec2" in filename:
        return "central_groupoid_counterexamples"
    if "smallmagmas" in filename or "manuallysampled" in filename or "z3counterexamples" in filename:
        return "small_finite_magma"
    if "stringmagmas" in filename or "weakcentralgroupoids" in filename:
        return "exceptional_hard"
    if any(marker in filename for marker in [
        "asterix",
        "austin",
        "obelix",
        "greedy",
        "infmodel",
        "equation1661",
        "equation1076",
        "equation1692",
        "eq511",
        "eq707",
        "eq883",
        "eq1112",
    ]):
        return "exceptional_hard"
    basename = Path(filename).name
    if basename.startswith(("rewrite", "apply", "combined", "nthrewrites", "equation1")):
        return "rewrite_metatheorem"
    return "hard_case"


def family_key(base_family: str, polarity: str, scope: str) -> str:
    return f"{base_family}:{polarity}:{scope}"


def load_equation_texts() -> dict[int, str]:
    lines = read_text(EXPORT_DIR / "equations.txt").splitlines()
    return {idx + 1: normalize_equation_text(line) for idx, line in enumerate(lines) if line.strip()}


def build_equation_metadata(equation_texts: dict[int, str], outcomes: dict) -> dict[int, dict]:
    labels = outcomes["equations"]
    rows = outcomes["outcomes"]
    dsu = DSU.build(len(labels))
    for i in range(len(labels)):
        row_i = rows[i]
        for j in range(i + 1, len(labels)):
            if row_i[j].endswith("_true") and rows[j][i].endswith("_true"):
                dsu.union(i, j)

    class_members: dict[int, list[int]] = defaultdict(list)
    for idx in range(len(labels)):
        class_members[dsu.find(idx)].append(idx + 1)

    normalized_lookup = {normalize_equation_text(text): eq_num for eq_num, text in equation_texts.items()}
    metadata: dict[int, dict] = {}
    for eq_num, text in equation_texts.items():
        lhs, rhs = split_equation(text)
        rep = dsu.find(eq_num - 1)
        dual_text = dualize_equation(text)
        metadata[eq_num] = {
            "equation_id": f"Equation{eq_num}",
            "equation_number": eq_num,
            "text": text,
            "lhs": lhs,
            "rhs": rhs,
            "is_literal_x_target": is_literal_x_target(text),
            "lhs_leftmost": leftmost_leaf(lhs),
            "lhs_rightmost": rightmost_leaf(lhs),
            "rhs_leftmost": leftmost_leaf(rhs),
            "rhs_rightmost": rightmost_leaf(rhs),
            "variable_profile": {
                "vars_lhs": sorted(set(var_tokens(lhs))),
                "vars_rhs": sorted(set(var_tokens(rhs))),
                "vars_all": sorted(set(var_tokens(text))),
                "multiplicity": multiplicities(text),
            },
            "equivalence_class_representative": f"Equation{min(class_members[rep])}",
            "equivalence_class_size": len(class_members[rep]),
            "dual_equation_id": f"Equation{normalized_lookup[dual_text]}" if dual_text in normalized_lookup else None,
        }
    return metadata


def supporting_theorem(entry: dict) -> dict:
    return {"name": entry["name"], "file": entry["filename"], "line": entry["line"]}


def canonical_exemplar(entry: dict) -> dict:
    variant_key = next(iter(entry["variant"]))
    variant = entry["variant"][variant_key]
    if variant_key == "implication":
        return {
            "kind": "implication",
            "lhs": variant["lhs"],
            "rhs": variant["rhs"],
            "finite": bool(variant.get("finite")),
            "file": entry["filename"],
            "line": entry["line"],
        }
    satisfied = list(variant["satisfied"])
    refuted = list(variant["refuted"])
    return {
        "kind": "facts",
        "satisfied": satisfied[:5],
        "refuted": refuted[:5],
        "finite": bool(variant.get("finite")),
        "macro_pair_capacity": len(satisfied) * len(refuted),
        "file": entry["filename"],
        "line": entry["line"],
    }


def aggregate_benchmark_alignment() -> dict:
    patterns = Counter()
    witnesses = Counter()
    failure_ids = Counter()
    for path in MANUAL_DISTILL_DIR.rglob("*_pattern_library.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("ranked_patterns", []):
            patterns[item["pattern"]] += int(item["count"])
            for example in item.get("examples", []):
                failure_ids[example["id"]] += 1
    for path in MANUAL_DISTILL_DIR.rglob("*_witness_library.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("ranked_witnesses", []):
            witnesses[item["witness"]] += int(item["count"])
            for example in item.get("examples", []):
                failure_ids[example["id"]] += 1

    manifest_failures = []
    if CURRENT_MANIFEST_PATH.exists():
        manifest = json.loads(CURRENT_MANIFEST_PATH.read_text(encoding="utf-8"))
        for gate_run in manifest.get("gate_runs", []):
            manifest_failures.extend(gate_run.get("failures", []))

    current_cheatsheets = {}
    for path in [ROOT / "cheatsheets" / "v19_noncollapse.txt", ROOT / "cheatsheets" / "v13_proof_required.txt"]:
        if path.exists():
            current_cheatsheets[path.stem] = path.stat().st_size

    return {
        "patterns": patterns,
        "witnesses": witnesses,
        "failure_ids": failure_ids,
        "manifest_failure_count": len(manifest_failures),
        "current_cheatsheet_sizes": current_cheatsheets,
    }


def benchmark_relevance_for_family(base_family: str, benchmark_alignment: dict) -> dict:
    patterns: Counter = Counter(benchmark_alignment["patterns"])
    witnesses: Counter = Counter(benchmark_alignment["witnesses"])
    score = 0
    signals: list[str] = []
    if base_family == "projection_family_counterexamples":
        for key in ["fp_new_variable_trap", "fp_lp_obstruction_missed", "fp_rp_obstruction_missed", "fp_both_projections_missed"]:
            if patterns[key]:
                score += patterns[key]
                signals.append(f"pattern:{key}={patterns[key]}")
        for key in ["LP", "RP"]:
            if witnesses[key]:
                score += witnesses[key]
                signals.append(f"witness:{key}={witnesses[key]}")
    elif base_family == "small_finite_magma":
        for key in ["C0", "XOR", "XNOR", "AND", "OR", "A2", "T3L", "T3R", "Z3A"]:
            if witnesses[key]:
                score += witnesses[key]
                signals.append(f"witness:{key}={witnesses[key]}")
        if patterns["fp_new_variable_trap"]:
            signals.append(f"shared-pattern:fp_new_variable_trap={patterns['fp_new_variable_trap']}")
    elif base_family == "rewrite_metatheorem":
        for key in ["fn_no_projection_handle", "fn_projection_both_hold"]:
            if patterns[key]:
                score += patterns[key]
                signals.append(f"pattern:{key}={patterns[key]}")
    elif base_family == "exceptional_hard":
        for key in ["generic_fp", "generic_fn"]:
            if patterns[key]:
                score += patterns[key]
                signals.append(f"pattern:{key}={patterns[key]}")
    elif base_family == "singleton_rewrite":
        score += 1
        signals.append("heuristic:high-value TRUE eliminator")
    elif base_family == "canonizer_confluence":
        score += 1
        signals.append("heuristic:important when finite witnesses fail")
    elif base_family == "linear_translation":
        score += 1
        signals.append("heuristic:used for harder finite-only refutations")
    elif base_family == "modified_lifted_magma":
        score += 1
        signals.append("heuristic:facts macros compress many false pairs at once")
    elif base_family == "subgraph_seed":
        score += 1
        signals.append("heuristic:backbone closure family")
    elif base_family == "automated_reasoner":
        score += 1
        signals.append("heuristic:useful provenance, low direct prompt value")
    else:
        signals.append("heuristic:conservative residual family")
    return {"score": score, "signals": signals}


def initialize_family_record(base_family: str, polarity: str, scope: str, closure_mode: str, benchmark_alignment: dict) -> dict:
    template = FAMILY_TEMPLATES[base_family]
    return {
        "family_id": family_key(base_family, polarity, scope),
        "base_family": base_family,
        "title": template["title"],
        "family_group": template["family_group"],
        "description": template["description"],
        "polarity": polarity,
        "scope": scope,
        "closure_mode": closure_mode,
        "trigger_features": list(template["trigger_features"]),
        "known_blockers": list(template["known_blockers"]),
        "paper_refs": list(template["paper_refs"]),
        "benchmark_relevance": benchmark_relevance_for_family(base_family, benchmark_alignment),
        "supporting_theorems": [],
        "canonical_exemplars": [],
        "entry_count": 0,
        "pair_count": 0,
        "macro_pair_capacity": 0,
        "priority": template["priority"],
        "cheatsheet_rule": template["cheatsheet_rule"],
    }


def add_unique_item(items: list[dict], candidate: dict, limit: int) -> None:
    if candidate in items:
        return
    if len(items) < limit:
        items.append(candidate)


def build_atlas_records(raw_entries: list[dict], benchmark_alignment: dict) -> tuple[list[dict], list[dict]]:
    families: dict[str, dict] = {}
    coverage_rows: list[dict] = []
    for entry in raw_entries:
        base_family = classify_entry(entry)
        variant_key = next(iter(entry["variant"]))
        variant = entry["variant"][variant_key]
        polarity = "true" if variant_key == "implication" else "false"
        scope = "finite" if variant.get("finite") or variant.get("facts", {}).get("finite") else "general"
        closure_mode = "explicit" if variant_key == "implication" else "facts"
        key = family_key(base_family, polarity, scope)
        if key not in families:
            families[key] = initialize_family_record(base_family, polarity, scope, closure_mode, benchmark_alignment)
        record = families[key]
        record["entry_count"] += 1
        add_unique_item(record["supporting_theorems"], supporting_theorem(entry), limit=8)
        add_unique_item(record["canonical_exemplars"], canonical_exemplar(entry), limit=4)
        if variant_key == "implication":
            record["pair_count"] += 1
        else:
            satisfied = list(variant["satisfied"])
            refuted = list(variant["refuted"])
            record["pair_count"] += len(refuted)
            record["macro_pair_capacity"] += len(satisfied) * len(refuted)
        coverage_rows.append({
            "entry_name": entry["name"],
            "file": entry["filename"],
            "line": entry["line"],
            "family_id": record["family_id"],
            "base_family": base_family,
            "variant": variant_key,
        })

    atlas_records = list(families.values()) + SYNTHETIC_FAMILIES
    atlas_records.sort(
        key=lambda item: (
            -item.get("benchmark_relevance", {}).get("score", 0),
            -item.get("entry_count", 0),
            -item.get("priority", 0),
            item["family_id"],
        )
    )
    return atlas_records, coverage_rows


def build_explicit_adjacency(explicit_implications: list[dict]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for item in explicit_implications:
        adjacency[item["lhs"]].add(item["rhs"])
    return adjacency


def bfs_path(adjacency: dict[str, set[str]], start: str, goal: str, max_depth: int = 6) -> Optional[list[str]]:
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        if len(path) > max_depth:
            continue
        for nxt in adjacency.get(node, ()):
            if nxt in seen:
                continue
            next_path = path + [nxt]
            if nxt == goal:
                return next_path
            seen.add(nxt)
            queue.append((nxt, next_path))
    return None


def sample_closure_traces(outcomes: dict, explicit_implications: list[dict], metadata: dict[int, dict], sample_size: int, seed: int) -> list[dict]:
    explicit_pairs = {(item["lhs"], item["rhs"]) for item in explicit_implications}
    dual_map = {meta["equation_id"]: meta["dual_equation_id"] for meta in metadata.values()}
    adjacency = build_explicit_adjacency(explicit_implications)
    rows = outcomes["outcomes"]
    labels = outcomes["equations"]
    candidates: list[tuple[str, str]] = []
    for i, lhs in enumerate(labels):
        for j, rhs in enumerate(labels):
            if i == j or not rows[i][j].endswith("_true"):
                continue
            if (lhs, rhs) in explicit_pairs:
                continue
            candidates.append((lhs, rhs))

    rng = random.Random(seed)
    rng.shuffle(candidates)
    traces: list[dict] = []
    for lhs, rhs in candidates:
        if len(traces) >= sample_size:
            break
        path = bfs_path(adjacency, lhs, rhs)
        if path:
            traces.append({"lhs": lhs, "rhs": rhs, "closure_family": "closure_transitive", "path": path})
            continue
        dual_lhs = dual_map.get(lhs)
        dual_rhs = dual_map.get(rhs)
        if dual_lhs and dual_rhs:
            dual_path = bfs_path(adjacency, dual_lhs, dual_rhs)
            if dual_path:
                traces.append({
                    "lhs": lhs,
                    "rhs": rhs,
                    "closure_family": "closure_dual",
                    "path": dual_path,
                    "dual_lhs": dual_lhs,
                    "dual_rhs": dual_rhs,
                })
    return traces


def build_validation_report(raw_entries: list[dict], atlas_records: list[dict], coverage_rows: list[dict], explicit_implications: list[dict], explicit_nonimplications: list[dict], closure_traces: list[dict], cheatsheet_path: Path) -> dict:
    explicit_family_count = sum(1 for item in atlas_records if item["family_id"] not in {"closure_transitive", "closure_dual"})
    hard_case_entries = sum(1 for row in coverage_rows if row["base_family"] == "hard_case")
    cheatsheet_bytes = cheatsheet_path.stat().st_size if cheatsheet_path.exists() else 0
    return {
        "coverage": {
            "raw_entry_count": len(raw_entries),
            "mapped_entry_count": len(coverage_rows),
            "unmapped_entry_count": len(raw_entries) - len(coverage_rows),
            "hard_case_entry_count": hard_case_entries,
        },
        "compression": {
            "explicit_family_count": explicit_family_count,
            "raw_to_family_ratio": round(len(raw_entries) / explicit_family_count, 2) if explicit_family_count else None,
            "cheatsheet_bytes": cheatsheet_bytes,
            "cheatsheet_budget": 10240,
            "fits_budget": cheatsheet_bytes <= 10240,
        },
        "closure": {
            "explicit_implication_count": len(explicit_implications),
            "explicit_nonimplication_count": len(explicit_nonimplications),
            "sampled_true_closure_traces": closure_traces,
            "sampled_trace_count": len(closure_traces),
        },
        "fidelity": {
            "families_with_supporting_theorems": sum(1 for item in atlas_records if item.get("supporting_theorems")),
            "families_with_exemplars": sum(1 for item in atlas_records if item.get("canonical_exemplars")),
        },
        "submission_eval": {
            "implemented": True,
            "executed": False,
            "reason": "Evaluation requires OpenRouter access and is only run when --evaluate is passed with credentials available.",
        },
    }


def cheatsheet_sections(atlas_records: list[dict]) -> list[list[str]]:
    record_lookup = {item["base_family"]: item for item in atlas_records if "base_family" in item}
    fast = [
        record_lookup["singleton_rewrite"]["cheatsheet_rule"],
        "[F02 target_fresh_var] If E2 introduces variables absent from E1, treat that as a strong FALSE cue and search witnesses before any TRUE fallback.",
        record_lookup["projection_family_counterexamples"]["cheatsheet_rule"],
    ]
    refutations = [
        record_lookup["small_finite_magma"]["cheatsheet_rule"],
        record_lookup["modified_lifted_magma"]["cheatsheet_rule"],
        record_lookup["linear_translation"]["cheatsheet_rule"],
    ]
    truths = [
        record_lookup["rewrite_metatheorem"]["cheatsheet_rule"],
        record_lookup["subgraph_seed"]["cheatsheet_rule"],
        record_lookup["automated_reasoner"]["cheatsheet_rule"],
    ]
    blockers = [
        record_lookup["canonizer_confluence"]["cheatsheet_rule"],
        "[F31 anti_fake_false] FALSE needs one named witness with an explicit assignment/check showing E1 holds and E2 fails.",
        "[F32 anti_fake_true] TRUE needs a concrete rewrite family, singleton-strength reason, or exact closure/symmetry argument; 'no counterexample found' is not enough.",
        "[F33 finite_scope] Never promote a finite-only witness family into a general proof claim.",
        record_lookup["exceptional_hard"]["cheatsheet_rule"],
    ]
    exemplars = [
        "[E1] Singleton pattern: x = f(y,z,...) with no x on the RHS is singleton-strength.",
        "[E2] Projection pattern: E1 keeps leftmost/rightmost x but E2 breaks it; test LP/RP first.",
        "[E3] Fresh-variable trap: extra variables in E2 are usually FALSE-leaning until disproven.",
    ]
    return [fast, refutations, truths, blockers, exemplars]


def render_cheatsheet(atlas_records: list[dict]) -> str:
    sections = cheatsheet_sections(atlas_records)
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
    lines.extend(sections[0])
    lines.extend(["", "REFUTATION FAMILIES"])
    lines.extend(sections[1])
    lines.extend(["", "TRUE FAMILIES"])
    lines.extend(sections[2])
    lines.extend(["", "BLOCKERS"])
    lines.extend(sections[3])
    lines.extend(["", "TINY EXEMPLARS"])
    lines.extend(sections[4])
    return "\n".join(lines).strip() + "\n"


def write_markdown_summary(out_path: Path, atlas_records: list[dict], validation: dict, benchmark_alignment: dict, metadata: dict[int, dict]) -> None:
    family_groups: dict[str, list[dict]] = defaultdict(list)
    for item in atlas_records:
        family_groups[item["family_group"]].append(item)

    lines = [
        "# Proof Atlas",
        "",
        "## Summary",
        "",
        f"- Equations indexed: {len(metadata):,}",
        f"- Explicit atlas families: {validation['compression']['explicit_family_count']:,}",
        f"- Raw theorem/facts entries compressed: {validation['coverage']['raw_entry_count']:,}",
        f"- Hard-case bucket entries: {validation['coverage']['hard_case_entry_count']:,}",
        f"- Cheatsheet bytes: {validation['compression']['cheatsheet_bytes']:,} / 10,240",
        "",
        "## Benchmark Alignment",
        "",
        f"- Aggregated manual-distill patterns: {sum(benchmark_alignment['patterns'].values()):,}",
        f"- Aggregated witness hits: {sum(benchmark_alignment['witnesses'].values()):,}",
        f"- Current cheatsheet sizes: {benchmark_alignment['current_cheatsheet_sizes']}",
        "",
    ]
    for group_name in sorted(family_groups):
        lines.append(f"## {group_name.title()}")
        lines.append("")
        for family in sorted(family_groups[group_name], key=lambda item: (-item.get('benchmark_relevance', {}).get('score', 0), -item.get('entry_count', 0), item['family_id'])):
            lines.append(f"### {family['family_id']}")
            lines.append("")
            lines.append(f"- Title: {family['title']}")
            lines.append(f"- Polarity / Scope / Closure: {family['polarity']} / {family['scope']} / {family['closure_mode']}")
            lines.append(f"- Description: {family['description']}")
            lines.append(f"- Entry count: {family.get('entry_count', 0):,}")
            lines.append(f"- Pair count: {family.get('pair_count', 0):,}")
            if family.get("macro_pair_capacity"):
                lines.append(f"- Macro pair capacity: {family['macro_pair_capacity']:,}")
            lines.append(f"- Trigger features: {', '.join(family['trigger_features'])}")
            lines.append(f"- Known blockers: {', '.join(family['known_blockers'])}")
            lines.append(f"- Paper refs: {', '.join(family['paper_refs'])}")
            lines.append(f"- Benchmark relevance: score={family.get('benchmark_relevance', {}).get('score', 0)} signals={family.get('benchmark_relevance', {}).get('signals', [])}")
            if family.get("canonical_exemplars"):
                lines.append(f"- Canonical exemplars: {json.dumps(family['canonical_exemplars'][:2], ensure_ascii=True)}")
            if family.get("supporting_theorems"):
                lines.append(f"- Supporting theorems: {json.dumps(family['supporting_theorems'][:3], ensure_ascii=True)}")
            lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def maybe_run_eval(cheatsheet_path: Path, benchmark_paths: list[Path]) -> list[dict]:
    results = []
    api_key = bool(__import__("os").environ.get("OPENROUTER_API_KEY"))
    if not api_key:
        return results
    for benchmark_path in benchmark_paths:
        command = [
            sys.executable,
            str(ROOT / "sim_lab.py"),
            "--data", str(benchmark_path),
            "--cheatsheet", str(cheatsheet_path),
            "--openrouter",
            "--quiet",
        ]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=3600)
        results.append({
            "benchmark": benchmark_path.name,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-800:],
            "stderr_tail": completed.stderr[-800:],
        })
    return results


def build_pipeline(out_dir: Path, cheatsheet_path: Path, sample_size: int, seed: int, run_eval: bool) -> dict:
    raw_entries = load_json_gz(EXPORT_DIR / "general_raw_full_entries.json.gz")
    general = load_json_gz(EXPORT_DIR / "general.json.gz")
    outcomes = load_json_gz(EXPORT_DIR / "general_outcomes.json.gz")
    equation_texts = load_equation_texts()
    metadata = build_equation_metadata(equation_texts, outcomes)
    benchmark_alignment = aggregate_benchmark_alignment()
    atlas_records, coverage_rows = build_atlas_records(raw_entries, benchmark_alignment)
    closure_traces = sample_closure_traces(outcomes, general["implications"], metadata, sample_size=sample_size, seed=seed)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "proof_atlas.jsonl", atlas_records)
    write_json(out_dir / "proof_atlas_summary.json", {
        "benchmark_alignment": {
            "patterns": dict(benchmark_alignment["patterns"]),
            "witnesses": dict(benchmark_alignment["witnesses"]),
            "current_cheatsheet_sizes": benchmark_alignment["current_cheatsheet_sizes"],
            "manifest_failure_count": benchmark_alignment["manifest_failure_count"],
        },
        "closure_sample_size": sample_size,
    })
    write_json(out_dir / "coverage_map.json", coverage_rows)
    write_json(out_dir / "equation_metadata.json", {f"Equation{eq_num}": metadata[eq_num] for eq_num in sorted(metadata)})
    write_json(out_dir / "closure_trace_samples.json", closure_traces)

    cheatsheet = render_cheatsheet(atlas_records)
    cheatsheet_path.parent.mkdir(parents=True, exist_ok=True)
    cheatsheet_path.write_text(cheatsheet, encoding="utf-8", newline="\n")

    validation = build_validation_report(raw_entries, atlas_records, coverage_rows, general["implications"], general["nonimplications"], closure_traces, cheatsheet_path)
    if run_eval:
        benchmark_paths = sorted((ROOT / "data" / "benchmark").glob("normal_balanced10_true5_false5_seed0.jsonl"))
        validation["submission_eval"] = {"implemented": True, "executed": True, "results": maybe_run_eval(cheatsheet_path, benchmark_paths)}
    write_json(out_dir / "validation_report.json", validation)
    write_markdown_summary(out_dir / "proof_atlas.md", atlas_records, validation, benchmark_alignment, metadata)
    return {"atlas_records": atlas_records, "validation": validation, "cheatsheet_path": cheatsheet_path, "out_dir": out_dir}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a hybrid proof atlas and render a competition cheatsheet.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directory for atlas artifacts.")
    parser.add_argument("--cheatsheet-out", default=str(DEFAULT_CHEATSHEET_PATH), help="Path to write the rendered cheatsheet.")
    parser.add_argument("--closure-sample-size", type=int, default=12, help="Number of derived TRUE pairs to sample for closure tracing.")
    parser.add_argument("--seed", type=int, default=20260326, help="Random seed for closure sampling.")
    parser.add_argument("--evaluate", action="store_true", help="Run a small OpenRouter evaluation if credentials are available.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_pipeline(Path(args.out_dir), Path(args.cheatsheet_out), args.closure_sample_size, args.seed, args.evaluate)
    validation = result["validation"]
    print(f"Atlas families: {validation['compression']['explicit_family_count']}")
    print(f"Coverage: {validation['coverage']['mapped_entry_count']} / {validation['coverage']['raw_entry_count']}")
    print(f"Hard-case bucket entries: {validation['coverage']['hard_case_entry_count']}")
    print(f"Cheatsheet bytes: {validation['compression']['cheatsheet_bytes']} / 10240")
    print(f"Artifacts: {rel(result['out_dir'])}, {rel(result['cheatsheet_path'])}")


if __name__ == "__main__":
    main()
