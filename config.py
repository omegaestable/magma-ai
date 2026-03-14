"""
config.py — Centralized configuration for the research pipeline.

Supports both ML-based classification and Honda et al. (2025)
cheat-sheet ICL distillation for the TAO Challenge.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
CHEATSHEETS_DIR = ROOT / "cheatsheets"
LOGS_DIR = ROOT / "logs"

EQUATIONS_FILE = ROOT / "equations.txt"
EXPLORER_CSV = ROOT / "export_explorer_14_3_2026.csv"
RAW_IMPL_CSV = ROOT / "export_raw_implications_14_3_2026.csv"

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
    n_format_examples: int = 2            # format demos appended (Eq.2 in paper)
    seed: int = 42
    # Cheatsheet
    cheatsheet_max_bytes: int = 10240     # 10KB limit
    cheatsheet_path: str = "cheatsheet.txt"
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
