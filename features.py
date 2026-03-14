"""Research-only feature extraction for ML implication prediction."""

import csv
import json
import logging
import pickle
from pathlib import Path
from typing import Optional

import numpy as np

from config import MLConfig, FEATURES_DIR, EQUATIONS_FILE, RAW_IMPL_CSV
from analyze_equations import (
    parse_equation, get_vars, count_ops, get_depth, term_size,
    count_var_occ, get_dual, is_specialization, can_prove_by_rewriting,
    find_counterexample, check_magma, matches_pattern, PATTERNS,
)

logger = logging.getLogger(__name__)


# ── Per-Equation Features ─────────────────────────────────────────

def equation_features(eq_str: str) -> dict:
    """Extract features from a single equation."""
    try:
        lhs, rhs = parse_equation(eq_str)
    except Exception:
        return _null_eq_features()

    vars_l = get_vars(lhs)
    vars_r = get_vars(rhs)
    all_vars = vars_l | vars_r

    ops_l = count_ops(lhs)
    ops_r = count_ops(rhs)
    depth_l = get_depth(lhs)
    depth_r = get_depth(rhs)
    size_l = term_size(lhs)
    size_r = term_size(rhs)

    # Variable balance: max occurrences of any variable
    max_occ_l = max((count_var_occ(lhs, v) for v in all_vars), default=0)
    max_occ_r = max((count_var_occ(rhs, v) for v in all_vars), default=0)

    # Duality: does eq equal its dual?
    dual_l = get_dual(lhs)
    dual_r = get_dual(rhs)
    is_self_dual = (lhs == dual_l and rhs == dual_r) or (lhs == dual_r and rhs == dual_l)

    # Pattern matching
    try:
        eq_parsed = (lhs, rhs)
        pattern_flags = {f"pat_{name}": matches_pattern(eq_parsed, name) for name in PATTERNS}
    except Exception:
        pattern_flags = {f"pat_{name}": False for name in PATTERNS}

    feats = {
        "n_vars": len(all_vars),
        "n_vars_lhs": len(vars_l),
        "n_vars_rhs": len(vars_r),
        "vars_shared": len(vars_l & vars_r),
        "vars_lhs_only": len(vars_l - vars_r),
        "vars_rhs_only": len(vars_r - vars_l),
        "vars_balanced": vars_l == vars_r,
        "ops_lhs": ops_l,
        "ops_rhs": ops_r,
        "ops_total": ops_l + ops_r,
        "ops_diff": abs(ops_l - ops_r),
        "depth_lhs": depth_l,
        "depth_rhs": depth_r,
        "depth_max": max(depth_l, depth_r),
        "depth_diff": abs(depth_l - depth_r),
        "size_lhs": size_l,
        "size_rhs": size_r,
        "size_total": size_l + size_r,
        "size_diff": abs(size_l - size_r),
        "max_var_occ_lhs": max_occ_l,
        "max_var_occ_rhs": max_occ_r,
        "is_identity": lhs == rhs,
        "lhs_is_var": isinstance(lhs, str),
        "rhs_is_var": isinstance(rhs, str),
        "is_self_dual": is_self_dual,
    }
    feats.update(pattern_flags)
    return feats


def _null_eq_features() -> dict:
    feats = {k: 0 for k in [
        "n_vars", "n_vars_lhs", "n_vars_rhs", "vars_shared",
        "vars_lhs_only", "vars_rhs_only", "vars_balanced",
        "ops_lhs", "ops_rhs", "ops_total", "ops_diff",
        "depth_lhs", "depth_rhs", "depth_max", "depth_diff",
        "size_lhs", "size_rhs", "size_total", "size_diff",
        "max_var_occ_lhs", "max_var_occ_rhs",
        "is_identity", "lhs_is_var", "rhs_is_var", "is_self_dual",
    ]}
    feats.update({f"pat_{name}": False for name in PATTERNS})
    return feats


# ── Pair Features ─────────────────────────────────────────────────

def pair_features(
    eq1_str: str,
    eq2_str: str,
    config: MLConfig = None,
) -> dict:
    """Extract features for an (eq1, eq2) pair.

    Combines per-equation structural features with pairwise algebraic features:
    - Specialization check (does eq1 directly imply eq2 by substitution?)
    - Rewriting check (BFS proof search)
    - Counterexample search (small magmas)
    - Structural comparisons (complexity delta, variable overlap, etc.)
    """
    if config is None:
        from config import DEFAULT_ML_CONFIG
        config = DEFAULT_ML_CONFIG

    # Per-equation features (prefixed e1_/e2_)
    f1 = equation_features(eq1_str)
    f2 = equation_features(eq2_str)
    feats = {}
    for k, v in f1.items():
        feats[f"e1_{k}"] = v
    for k, v in f2.items():
        feats[f"e2_{k}"] = v

    # Parse for algebraic checks
    try:
        eq1 = parse_equation(eq1_str)
        eq2 = parse_equation(eq2_str)
        parsed_ok = True
    except Exception:
        parsed_ok = False

    # ── Structural pair features ──
    feats["same_equation"] = eq1_str.strip() == eq2_str.strip()
    feats["n_vars_diff"] = f1["n_vars"] - f2["n_vars"]
    feats["ops_diff_signed"] = f1["ops_total"] - f2["ops_total"]
    feats["depth_diff_signed"] = f1["depth_max"] - f2["depth_max"]
    feats["size_diff_signed"] = f1["size_total"] - f2["size_total"]
    feats["complexity_ratio"] = (f1["ops_total"] + 1) / (f2["ops_total"] + 1)

    # Eq2 uses variables not in eq1?
    feats["e2_has_extra_vars"] = f2["vars_rhs_only"] > 0 or (f2["n_vars"] > f1["n_vars"])

    # Trivial cases
    feats["e1_is_trivial_identity"] = f1["is_identity"]  # x=x
    feats["e2_is_trivial_identity"] = f2["is_identity"]
    feats["e1_forces_singleton"] = f1["lhs_is_var"] and f1["rhs_is_var"] and f1["n_vars"] == 2
    feats["e2_forces_singleton"] = f2["lhs_is_var"] and f2["rhs_is_var"] and f2["n_vars"] == 2

    # ── Algebraic features ──
    if parsed_ok and config.use_algebraic:
        # Direct specialization
        try:
            feats["is_specialization"] = is_specialization(eq1, eq2)
        except Exception:
            feats["is_specialization"] = False

        # Reverse specialization (eq2 implies eq1 — useful as negative signal)
        try:
            feats["is_reverse_spec"] = is_specialization(eq2, eq1)
        except Exception:
            feats["is_reverse_spec"] = False

        # BFS rewriting proof
        try:
            feats["rewriting_proved"] = can_prove_by_rewriting(
                eq1, eq2, max_steps=config.rewrite_max_steps
            )
        except Exception:
            feats["rewriting_proved"] = False
    else:
        feats["is_specialization"] = False
        feats["is_reverse_spec"] = False
        feats["rewriting_proved"] = False

    # ── Counterexample features ──
    if parsed_ok and config.use_counterexample:
        try:
            cex = find_counterexample(eq1, eq2, magma_sizes=config.counterexample_sizes)
            feats["has_counterexample"] = cex is not None
            feats["counterexample_size"] = len(cex) if cex else 0
        except Exception:
            feats["has_counterexample"] = False
            feats["counterexample_size"] = 0
    else:
        feats["has_counterexample"] = False
        feats["counterexample_size"] = 0

    return feats


# ── Dataset Construction ──────────────────────────────────────────

def load_raw_implication_matrix(filepath: str = None) -> dict:
    """Load the raw implications CSV. Returns {(eq1_idx, eq2_idx): bool}.

    The CSV has rows of comma-separated integers.
    Each row i has 4694 values: positive value at position j means Eq(i+1) implies Eq(j+1).
    """
    if filepath is None:
        filepath = str(RAW_IMPL_CSV)

    logger.info(f"Loading implication matrix from {filepath}...")
    matrix = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for row_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            values = line.split(',')
            eq1 = row_idx + 1
            for col_idx, val_str in enumerate(values):
                try:
                    val = int(val_str.strip())
                except ValueError:
                    continue
                eq2 = col_idx + 1
                if eq1 != eq2:
                    matrix[(eq1, eq2)] = val > 0
    logger.info(f"Loaded {len(matrix)} pairs")
    return matrix


def build_dataset_from_jsonl(
    filepath: str,
    equations: list,
    config: MLConfig = None,
) -> tuple:
    """Build feature matrix from JSONL training data.

    Returns (X: np.ndarray, y: np.ndarray, feature_names: list, meta: list)
    """
    if config is None:
        from config import DEFAULT_ML_CONFIG
        config = DEFAULT_ML_CONFIG

    # Load problems
    problems = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            eq1_idx = int(rec.get('equation1_index', rec.get('eq1', 0)))
            eq2_idx = int(rec.get('equation2_index', rec.get('eq2', 0)))
            label = rec.get('implies', rec.get('label'))
            if eq1_idx and eq2_idx and label is not None:
                problems.append((eq1_idx, eq2_idx, bool(label)))

    logger.info(f"Building features for {len(problems)} problems...")

    feature_dicts = []
    labels = []
    meta = []
    for i, (eq1_idx, eq2_idx, label) in enumerate(problems):
        eq1_str = equations[eq1_idx - 1]
        eq2_str = equations[eq2_idx - 1]
        feats = pair_features(eq1_str, eq2_str, config)
        feats["eq1_idx"] = eq1_idx
        feats["eq2_idx"] = eq2_idx
        feature_dicts.append(feats)
        labels.append(label)
        meta.append({"eq1_idx": eq1_idx, "eq2_idx": eq2_idx, "label": label})

        if (i + 1) % 100 == 0:
            logger.info(f"  Processed {i+1}/{len(problems)} pairs")

    # Convert to numpy
    feature_names = sorted(feature_dicts[0].keys())
    X = np.array([[float(d.get(k, 0)) for k in feature_names] for d in feature_dicts])
    y = np.array(labels, dtype=np.float32)

    logger.info(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    logger.info(f"Label balance: {y.sum():.0f} TRUE ({y.mean()*100:.1f}%), {len(y)-y.sum():.0f} FALSE")

    return X, y, feature_names, meta


def build_dataset_from_matrix(
    equations: list,
    matrix: dict,
    n_samples: int = 10000,
    config: MLConfig = None,
    seed: int = 42,
) -> tuple:
    """Build feature matrix by sampling from the full implication matrix.

    Balanced sampling: 50% TRUE, 50% FALSE.
    """
    import random
    if config is None:
        from config import DEFAULT_ML_CONFIG
        config = DEFAULT_ML_CONFIG

    true_pairs = [(k, True) for k, v in matrix.items() if v]
    false_pairs = [(k, False) for k, v in matrix.items() if not v]

    rng = random.Random(seed)
    rng.shuffle(true_pairs)
    rng.shuffle(false_pairs)

    half = n_samples // 2
    selected = true_pairs[:half] + false_pairs[:half]
    rng.shuffle(selected)

    logger.info(f"Building features for {len(selected)} sampled pairs...")

    feature_dicts = []
    labels = []
    meta = []
    for i, ((eq1_idx, eq2_idx), label) in enumerate(selected):
        eq1_str = equations[eq1_idx - 1]
        eq2_str = equations[eq2_idx - 1]
        feats = pair_features(eq1_str, eq2_str, config)
        feats["eq1_idx"] = eq1_idx
        feats["eq2_idx"] = eq2_idx
        feature_dicts.append(feats)
        labels.append(label)
        meta.append({"eq1_idx": eq1_idx, "eq2_idx": eq2_idx, "label": label})

        if (i + 1) % 500 == 0:
            logger.info(f"  Processed {i+1}/{len(selected)} pairs")

    feature_names = sorted(feature_dicts[0].keys())
    X = np.array([[float(d.get(k, 0)) for k in feature_names] for d in feature_dicts])
    y = np.array(labels, dtype=np.float32)

    logger.info(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    return X, y, feature_names, meta


def save_dataset(X, y, feature_names, meta, name: str = "default"):
    """Save precomputed feature dataset."""
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FEATURES_DIR / f"{name}.pkl"
    with open(path, 'wb') as f:
        pickle.dump({"X": X, "y": y, "feature_names": feature_names, "meta": meta}, f)
    logger.info(f"Saved dataset to {path} ({X.shape[0]} samples, {X.shape[1]} features)")


def load_dataset(name: str = "default") -> tuple:
    """Load precomputed feature dataset."""
    path = FEATURES_DIR / f"{name}.pkl"
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data["X"], data["y"], data["feature_names"], data["meta"]


# ── CLI ───────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract features for ML training")
    parser.add_argument("--data", help="JSONL training file (if omitted, samples from full matrix)")
    parser.add_argument("--n-samples", type=int, default=10000,
                        help="Number of pairs to sample from matrix")
    parser.add_argument("--name", default="default", help="Dataset name for saving")
    parser.add_argument("--no-algebraic", action="store_true", help="Skip algebraic proofs (faster)")
    parser.add_argument("--no-counterexample", action="store_true", help="Skip counterexample search (faster)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    from analyze_equations import load_equations
    equations = load_equations()

    config = MLConfig(
        seed=args.seed,
        use_algebraic=not args.no_algebraic,
        use_counterexample=not args.no_counterexample,
    )

    if args.data:
        X, y, feature_names, meta = build_dataset_from_jsonl(args.data, equations, config)
    else:
        matrix = load_raw_implication_matrix()
        X, y, feature_names, meta = build_dataset_from_matrix(
            equations, matrix, n_samples=args.n_samples, config=config, seed=args.seed,
        )

    save_dataset(X, y, feature_names, meta, name=args.name)

    # Print feature summary
    print(f"\nFeatures ({len(feature_names)}):")
    for name in feature_names:
        col = feature_names.index(name)
        print(f"  {name}: mean={X[:, col].mean():.3f}, std={X[:, col].std():.3f}")


if __name__ == "__main__":
    main()
