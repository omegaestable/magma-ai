"""Centralized configuration for submission-support and research tooling.

Status:
- Distillation and prompt evaluation are offline support for the cheatsheet artifact.
- ML and solver settings are research-only and not submission-time behavior.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
GUIDES_DIR = DOCS_DIR / "guides"
PAPER_DIR = DOCS_DIR / "paper"
PAPER_SOURCE_DIR = PAPER_DIR / "source"
DATA_DIR = ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"
RESULTS_DIR = ROOT / "results"
CHEATSHEETS_DIR = ROOT / "cheatsheets"
LOGS_DIR = ROOT / "logs"

CHEATSHEET_FILE = ROOT / "cheatsheet.txt"
EQUATIONS_FILE = ROOT / "equations.txt"
EXPLORER_CSV = EXPORTS_DIR / "export_explorer_14_3_2026.csv"
RAW_IMPL_CSV = EXPORTS_DIR / "export_raw_implications_14_3_2026.csv"

# ── Model Configs ──────────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Configuration for an LLM provider/model."""
    provider: str          # "openai", "anthropic", "google", "local"
    model: str             # e.g. "gpt-4.1", "gemini-2.0-flash", "llama-3"
    api_key_env: str = ""  # env var name for API key
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    cost_per_1k_input: float = 0.0   # USD per 1K input tokens
    cost_per_1k_output: float = 0.0  # USD per 1K output tokens

    @property
    def api_key(self) -> str:
        if self.api_key_env:
            return os.environ.get(self.api_key_env, "")
        return ""


# Pre-configured LLM models (for distillation / eval, add keys via env vars)
MODELS = {
    "gpt-4.1": ModelConfig(
        provider="openai", model="gpt-4.1",
        api_key_env="OPENAI_API_KEY",
        cost_per_1k_input=0.002, cost_per_1k_output=0.008,
    ),
    "gpt-4o-mini": ModelConfig(
        provider="openai", model="gpt-4o-mini",
        api_key_env="OPENAI_API_KEY",
        cost_per_1k_input=0.00015, cost_per_1k_output=0.0006,
    ),
    "claude-sonnet": ModelConfig(
        provider="anthropic", model="claude-sonnet-4-20250514",
        api_key_env="ANTHROPIC_API_KEY",
        cost_per_1k_input=0.003, cost_per_1k_output=0.015,
    ),
}

# ── ML Paths ───────────────────────────────────────────────────────
MODELS_DIR = ROOT / "models"        # saved ML model checkpoints
FEATURES_DIR = ROOT / "features"    # precomputed feature matrices
EMBEDDINGS_DIR = ROOT / "embeddings"  # equation embeddings


# ── Experiment Config ──────────────────────────────────────────────

@dataclass
class ExperimentConfig:
    """Full experiment configuration."""
    name: str = "default"
    # Distillation
    distill_model: str = "gpt-4.1"       # model to create the cheatsheet
    n_shots: int = 150                    # demos for many-shot/distillation
    # Evaluation
    eval_model: str = "gpt-4o-mini"      # model for inference (cheap)
    n_eval: int = 100                     # number of eval problems
    n_format_examples: int = 0            # safe default: no eval-set label leakage
    seed: int = 42
    dual_swap_check: bool = False         # evaluate (E1*, E2*) alongside (E1, E2)
    # Cheatsheet
    cheatsheet_max_bytes: int = 10240     # 10KB limit
    cheatsheet_path: str = str(CHEATSHEET_FILE)
    # Ablations
    use_rationale_augmentation: bool = True
    use_self_consistency: bool = False
    sc_samples: int = 5                   # self-consistency samples


DEFAULT_CONFIG = ExperimentConfig()


# ── ML Training Config ─────────────────────────────────────────────

@dataclass
class MLConfig:
    """Configuration for ML-based implication prediction."""
    name: str = "default"
    seed: int = 42
    # Data
    train_split: float = 0.8
    val_split: float = 0.1
    # Features
    use_structural: bool = True       # equation structure features
    use_algebraic: bool = True        # rewriting/specialization proofs
    use_counterexample: bool = True   # counterexample search features
    use_embeddings: bool = False      # learned equation embeddings
    counterexample_sizes: tuple = (2, 3)
    rewrite_max_steps: int = 200
    # Model
    model_type: str = "xgboost"       # xgboost, lightgbm, mlp, gnn
    n_estimators: int = 1000
    learning_rate: float = 0.05
    max_depth: int = 8
    # Embedding model (if use_embeddings)
    embed_dim: int = 64
    embed_epochs: int = 50
    embed_batch_size: int = 256


DEFAULT_ML_CONFIG = MLConfig()


# ── Environment Validation ─────────────────────────────────────────

def check_environment(eval_model: str = "gpt-4o-mini") -> list[str]:
    """Check readiness of the evaluation environment.

    Returns a list of status lines (info/warnings).
    """
    lines: list[str] = []

    # Check model config
    if eval_model in MODELS:
        cfg = MODELS[eval_model]
        lines.append(f"Model: {cfg.model} ({cfg.provider})")
        key = cfg.api_key
        if key:
            masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
            lines.append(f"API key ({cfg.api_key_env}): set ({masked})")
        else:
            lines.append(f"WARNING: API key {cfg.api_key_env} is NOT set — live eval will fail")
            lines.append(f"  Set it via: $env:{cfg.api_key_env}='sk-...'  or in .env")
    else:
        lines.append(f"WARNING: Unknown model '{eval_model}' — not in MODELS registry")

    # Check data folder
    data_files = []
    if DATA_DIR.is_dir():
        data_files = [f.name for f in DATA_DIR.iterdir() if f.suffix == '.jsonl']
    if data_files:
        lines.append(f"Data folder: {len(data_files)} JSONL file(s) found ({', '.join(data_files)})")
    else:
        lines.append("WARNING: No JSONL files in data/ — run: python download_data.py --generate-local")

    # Check cheatsheet
    cs = CHEATSHEET_FILE
    if cs.is_file():
        size = cs.stat().st_size
        lines.append(f"Cheatsheet: {size} bytes ({size*100/10240:.1f}% of 10KB limit)")
    else:
        lines.append("WARNING: cheatsheet.txt not found")

    # Check equations
    if EQUATIONS_FILE.is_file():
        with open(EQUATIONS_FILE, 'r', encoding='utf-8') as f:
            n_eq = sum(1 for line in f if line.strip())
        lines.append(f"Equations: {n_eq} loaded")
    else:
        lines.append("WARNING: equations.txt not found")

    # Python packages
    pkg_status = []
    for pkg in ['openai', 'anthropic']:
        try:
            __import__(pkg)
            pkg_status.append(f"{pkg} ✓")
        except ImportError:
            pkg_status.append(f"{pkg} ✗")
    lines.append(f"Packages: {', '.join(pkg_status)}")

    return lines
