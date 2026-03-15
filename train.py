"""Research-only ML training pipeline for implication prediction."""

import json
import logging
import pickle
import argparse
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import log_loss, accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

from config import MLConfig, DEFAULT_ML_CONFIG, MODELS_DIR, RESULTS_DIR
from features import (
    load_dataset,
    build_dataset_from_jsonl,
    build_dataset_from_matrix,
    load_raw_implication_matrix,
    save_dataset,
)
from benchmark_utils import annotate_records

logger = logging.getLogger(__name__)


# ── Model Builders ────────────────────────────────────────────────

def build_xgboost(config: MLConfig):
    import xgboost as xgb
    return xgb.XGBClassifier(
        n_estimators=config.n_estimators,
        learning_rate=config.learning_rate,
        max_depth=config.max_depth,
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=config.seed,
        n_jobs=-1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
    )


def build_lightgbm(config: MLConfig):
    import lightgbm as lgb
    return lgb.LGBMClassifier(
        n_estimators=config.n_estimators,
        learning_rate=config.learning_rate,
        max_depth=config.max_depth,
        objective="binary",
        metric="binary_logloss",
        random_state=config.seed,
        n_jobs=-1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        verbose=-1,
    )


def build_mlp(config: MLConfig):
    from sklearn.neural_network import MLPClassifier
    return MLPClassifier(
        hidden_layer_sizes=(256, 128, 64),
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        max_iter=500,
        early_stopping=True,
        validation_fraction=0.1,
        random_state=config.seed,
    )


MODEL_BUILDERS = {
    "xgboost": build_xgboost,
    "lightgbm": build_lightgbm,
    "mlp": build_mlp,
}


# ── Training Pipeline ─────────────────────────────────────────────

def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    config: MLConfig,
    calibrate: bool = True,
) -> object:
    """Train a classifier with optional probability calibration."""
    if config.model_type not in MODEL_BUILDERS:
        raise ValueError(f"Unknown model: {config.model_type}. Available: {list(MODEL_BUILDERS.keys())}")

    logger.info(f"Training {config.model_type} on {X_train.shape[0]} samples, {X_train.shape[1]} features")

    model = MODEL_BUILDERS[config.model_type](config)
    model.fit(X_train, y_train)

    if calibrate:
        logger.info("Calibrating probabilities (isotonic)...")
        calibrated = CalibratedClassifierCV(model, cv=3, method="isotonic")
        calibrated.fit(X_train, y_train)
        return calibrated

    return model


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list = None,
) -> dict:
    """Evaluate a trained model."""
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_prob > 0.5).astype(int)

    acc = accuracy_score(y_test, y_pred)
    ll = log_loss(y_test, y_pred_prob)

    # Per-class accuracy
    true_mask = y_test == 1
    false_mask = y_test == 0
    true_acc = accuracy_score(y_test[true_mask], y_pred[true_mask]) if true_mask.sum() > 0 else 0
    false_acc = accuracy_score(y_test[false_mask], y_pred[false_mask]) if false_mask.sum() > 0 else 0

    results = {
        "accuracy": float(acc),
        "log_loss": float(ll),
        "true_accuracy": float(true_acc),
        "false_accuracy": float(false_acc),
        "n_test": int(len(y_test)),
        "n_true": int(true_mask.sum()),
        "n_false": int(false_mask.sum()),
    }

    # Feature importance (if available)
    if feature_names and hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        results["top_features"] = [
            {"name": feature_names[i], "importance": float(importances[i])}
            for i in sorted_idx[:20]
        ]
    elif feature_names and hasattr(model, 'estimator') and hasattr(model.estimator, 'feature_importances_'):
        importances = model.estimator.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        results["top_features"] = [
            {"name": feature_names[i], "importance": float(importances[i])}
            for i in sorted_idx[:20]
        ]

    return results


def cross_validate(
    X: np.ndarray,
    y: np.ndarray,
    config: MLConfig,
    n_folds: int = 5,
) -> tuple[dict, np.ndarray]:
    """Run k-fold cross-validation."""
    logger.info(f"Running {n_folds}-fold CV with {config.model_type}...")

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=config.seed)

    fold_results = []
    all_probas = np.zeros(len(y))

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        model = train_model(X_tr, y_tr, config, calibrate=True)
        val_proba = model.predict_proba(X_val)[:, 1]
        all_probas[val_idx] = val_proba

        fold_acc = accuracy_score(y_val, (val_proba > 0.5).astype(int))
        fold_ll = log_loss(y_val, val_proba)
        fold_results.append({"fold": fold, "accuracy": fold_acc, "log_loss": fold_ll})
        logger.info(f"  Fold {fold}: acc={fold_acc:.4f}, logloss={fold_ll:.4f}")

    # Overall OOF metrics
    oof_acc = accuracy_score(y, (all_probas > 0.5).astype(int))
    oof_ll = log_loss(y, all_probas)

    results = {
        "n_folds": n_folds,
        "model_type": config.model_type,
        "oof_accuracy": float(oof_acc),
        "oof_log_loss": float(oof_ll),
        "fold_results": fold_results,
        "mean_accuracy": float(np.mean([f["accuracy"] for f in fold_results])),
        "std_accuracy": float(np.std([f["accuracy"] for f in fold_results])),
        "mean_log_loss": float(np.mean([f["log_loss"] for f in fold_results])),
        "std_log_loss": float(np.std([f["log_loss"] for f in fold_results])),
    }

    logger.info(f"OOF: acc={oof_acc:.4f}, logloss={oof_ll:.4f}")
    return results, all_probas


def mine_hardest_pairs(
    y: np.ndarray,
    oof_probas: np.ndarray,
    meta: list,
    equations: list[str],
    top_k: int = 250,
) -> list[dict]:
    """Rank the hardest pairs by out-of-fold loss and uncertainty."""
    eps = 1e-7
    scored = []
    for idx, (label, prob, pair_meta) in enumerate(zip(y, oof_probas, meta)):
        clipped = max(eps, min(1.0 - eps, float(prob)))
        loss = -np.log(clipped) if label else -np.log(1.0 - clipped)
        predicted = clipped > 0.5
        scored.append({
            "eq1_idx": int(pair_meta["eq1_idx"]),
            "eq2_idx": int(pair_meta["eq2_idx"]),
            "eq1": equations[int(pair_meta["eq1_idx"]) - 1],
            "eq2": equations[int(pair_meta["eq2_idx"]) - 1],
            "label": bool(label),
            "predicted_prob": clipped,
            "predicted": predicted,
            "correct": predicted == bool(label),
            "oof_log_loss": float(loss),
            "margin": float(abs(clipped - 0.5)),
        })

    hardest = sorted(
        scored,
        key=lambda record: (-record["oof_log_loss"], record["margin"]),
    )[:top_k]
    return annotate_records(hardest, equations)


def save_model(model, feature_names: list, config: MLConfig, name: str = None):
    """Save trained model and metadata."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    name = name or config.name
    path = MODELS_DIR / f"{name}.pkl"
    with open(path, 'wb') as f:
        pickle.dump({
            "model": model,
            "feature_names": feature_names,
            "config": config.__dict__,
        }, f)
    logger.info(f"Model saved to {path}")


def load_model(name: str = "default") -> tuple:
    """Load a saved model."""
    path = MODELS_DIR / f"{name}.pkl"
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data["model"], data["feature_names"], data.get("config", {})


# ── Prediction Interface ─────────────────────────────────────────

def predict_pair(
    eq1_str: str,
    eq2_str: str,
    model,
    feature_names: list,
    config: MLConfig = None,
) -> float:
    """Predict implication probability for a single pair."""
    from features import pair_features
    if config is None:
        config = DEFAULT_ML_CONFIG
    feats = pair_features(eq1_str, eq2_str, config)
    x = np.array([[float(feats.get(k, 0)) for k in feature_names]])
    prob = model.predict_proba(x)[0, 1]
    return float(prob)


def ensure_dataset_available(
    dataset_name: str,
    config: MLConfig,
    n_samples: int,
    excluded_eq_indices: set[int] | None = None,
) -> tuple[np.ndarray, np.ndarray, list, list]:
    """Load a precomputed dataset, auto-building it from matrix data if missing."""
    try:
        return load_dataset(dataset_name)
    except FileNotFoundError:
        from analyze_equations import load_equations

        logger.warning(
            "Dataset '%s' not found in features/. Auto-bootstrapping from matrix with n_samples=%d.",
            dataset_name,
            n_samples,
        )
        equations = load_equations()
        matrix = load_raw_implication_matrix()
        X, y, feature_names, meta = build_dataset_from_matrix(
            equations,
            matrix,
            n_samples=n_samples,
            config=config,
            seed=config.seed,
            excluded_eq_indices=excluded_eq_indices or set(),
        )
        save_dataset(X, y, feature_names, meta, name=dataset_name)
        logger.info(
            "Auto-bootstrap complete: features/%s.pkl created with %d rows.",
            dataset_name,
            X.shape[0],
        )
        return X, y, feature_names, meta


# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train ML model for implication prediction")
    parser.add_argument("--dataset", default="default", help="Precomputed dataset name (from features.py)")
    parser.add_argument("--data", default=None, help="JSONL file (alternative to --dataset)")
    parser.add_argument("--exclude-eq-file", default=None,
                        help="Optional JSON file listing equation indices to exclude when building from --data")
    parser.add_argument("--bootstrap-samples", type=int, default=10000,
                        help="Rows to sample when auto-bootstrapping a missing precomputed dataset")
    parser.add_argument("--no-auto-bootstrap", action="store_true",
                        help="Disable automatic dataset creation when --dataset is missing")
    parser.add_argument("--model-type", default="xgboost", choices=list(MODEL_BUILDERS.keys()))
    parser.add_argument("--n-estimators", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--cv", type=int, default=5, help="Number of CV folds (0 = no CV, just train)")
    parser.add_argument("--hardest-k", type=int, default=0,
                        help="Export the top-K hardest out-of-fold pairs after CV")
    parser.add_argument("--name", default="default", help="Experiment name")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = MLConfig(
        name=args.name,
        model_type=args.model_type,
        n_estimators=args.n_estimators,
        learning_rate=args.learning_rate,
        max_depth=args.max_depth,
        seed=args.seed,
    )

    # Load data
    from benchmark_utils import load_holdout_indices
    excluded_eq_indices = set(load_holdout_indices(args.exclude_eq_file)) if args.exclude_eq_file else set()

    if args.data:
        from analyze_equations import load_equations
        equations = load_equations()
        X, y, feature_names, meta = build_dataset_from_jsonl(
            args.data,
            equations,
            config,
            excluded_eq_indices=excluded_eq_indices,
        )
        save_dataset(X, y, feature_names, meta, name=args.name)
    else:
        if args.no_auto_bootstrap:
            X, y, feature_names, meta = load_dataset(args.dataset)
        else:
            X, y, feature_names, meta = ensure_dataset_available(
                dataset_name=args.dataset,
                config=config,
                n_samples=args.bootstrap_samples,
                excluded_eq_indices=excluded_eq_indices,
            )

    logger.info(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {y.mean()*100:.1f}% positive")

    # Cross-validation
    if args.cv > 0:
        cv_results, oof_probas = cross_validate(X, y, config, n_folds=args.cv)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_DIR / f"cv_{args.name}.json", 'w') as f:
            json.dump(cv_results, f, indent=2)
        print(f"\nCV Results ({args.cv}-fold):")
        print(f"  Accuracy: {cv_results['oof_accuracy']:.4f} (±{cv_results['std_accuracy']:.4f})")
        print(f"  Log-loss: {cv_results['oof_log_loss']:.4f} (±{cv_results['std_log_loss']:.4f})")

        if args.hardest_k > 0:
            from analyze_equations import load_equations
            equations = load_equations()
            hardest_pairs = mine_hardest_pairs(y, oof_probas, meta, equations, top_k=args.hardest_k)
            hardest_path = RESULTS_DIR / f"hardest_{args.name}.json"
            with open(hardest_path, 'w', encoding='utf-8') as f:
                json.dump(hardest_pairs, f, indent=2)
            print(f"  Hardest pairs: wrote top {len(hardest_pairs)} to {hardest_path}")

    # Train final model on full data
    logger.info("Training final model on full dataset...")
    model = train_model(X, y, config, calibrate=True)
    results = evaluate_model(model, X, y, feature_names)
    save_model(model, feature_names, config, name=args.name)

    print(f"\nFinal model (train set):")
    print(f"  Accuracy: {results['accuracy']:.4f}")
    print(f"  Log-loss: {results['log_loss']:.4f}")

    if "top_features" in results:
        print(f"\nTop features:")
        for feat in results["top_features"][:10]:
            print(f"  {feat['name']}: {feat['importance']:.4f}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / f"train_{args.name}.json", 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
