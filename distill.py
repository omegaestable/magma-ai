"""Offline cheatsheet distillation pipeline.

Status:
- Submission-support only as an offline authoring tool.
- Never part of the final submission-time inference path.
"""

import json
import random
import argparse
import logging
from pathlib import Path
from typing import Optional

from config import ExperimentConfig, DEFAULT_CONFIG, CHEATSHEETS_DIR, DATA_DIR, RESULTS_DIR
from llm_client import LLMClient

logger = logging.getLogger(__name__)

# ── Prompt Templates (adapted from Honda et al. 2025, Appendix A) ─────────

RATIONALE_META_PROMPT = """\
You are an expert in abstract algebra and equational theories over magmas.
A magma (M, ◇) is a set M with a binary operation ◇ (no axioms assumed).
"Equation A implies Equation B" means every magma satisfying A also satisfies B.

Below are examples of equational implication problems with correct answers and explanations.
Use these as a reference to generate a detailed explanation for the final problem.

{seed_examples}

Now generate a detailed step-by-step explanation for the following problem:

Equation 1: {eq1}
Equation 2: {eq2}
Answer: {label}

Explanation:"""


CHEATSHEET_CREATION_PROMPT = """\
Create a cheat sheet based on the examples below.
You will be asked to determine whether one equational law over magmas implies another.
A magma (M, ◇) is a set M with a binary operation ◇ (no axioms assumed).
"Equation 1 implies Equation 2" means: every magma satisfying Eq1 also satisfies Eq2.

Your task here is to make a cheat sheet that will help you answer such problems correctly.
First, carefully read the examples below and identify which ones you find most difficult.

{demonstrations}

Now, create a cheat sheet to help you solve the difficult examples.
Exclude any content that is easy for you, and only include specific, detailed points
to address the challenging ones.

The cheat sheet MUST be at most {max_bytes} bytes in UTF-8.
Focus on:
- Decision procedures and algorithms for checking implication
- Common patterns that lead to TRUE or FALSE
- Useful counterexample magma tables
- Key structural properties (variable count, operation depth, duality)
- Landmark equations and their relationships"""

CHEATSHEET_PROMPT_VARIANTS = {
    "default": CHEATSHEET_CREATION_PROMPT,

    "textbook": """\
Based on the examples below, write a textbook chapter that teaches how to determine
whether one equational law over magmas implies another.
A magma (M, ◇) is a set M with a binary operation ◇ (no axioms assumed).

{demonstrations}

Write a comprehensive textbook chapter (at most {max_bytes} bytes UTF-8) covering:
- Core concepts and definitions
- Decision methods (substitution, rewriting, counterexamples)
- Common patterns and pitfalls
- Worked examples""",

    "concise": """\
Read the examples below carefully. Then produce a concise instruction manual
for determining equational implication over magmas.

{demonstrations}

Write a concise, actionable instruction manual (at most {max_bytes} bytes UTF-8).
Focus only on decision-critical rules and patterns. Be terse.""",

    "summary": """\
Analyze the examples below and produce a textual summary of the key patterns,
strategies, and rules needed to correctly determine equational implication over magmas.

{demonstrations}

Summary (at most {max_bytes} bytes UTF-8):""",
}


# ── Seed rationale examples for X-ICL meta-prompting ──────────────

SEED_RATIONALES = [
    {
        "eq1": "x ◇ y = y ◇ x",
        "eq2": "(x ◇ y) ◇ z = (x ◇ z) ◇ y",
        "label": "TRUE",
        "rationale": (
            "Eq1 says ◇ is commutative. We need to show (x◇y)◇z = (x◇z)◇y. "
            "Using commutativity: (x◇y)◇z = z◇(x◇y) — wait, that doesn't help directly. "
            "Instead: (x◇z)◇y. Using commutativity on the inner x◇z = z◇x, so (z◇x)◇y. "
            "And (x◇y)◇z. Using commutativity on x◇y = y◇x, so (y◇x)◇z. "
            "This approach needs more care. Direct approach: in (x◇y)◇z, apply commutativity "
            "to x◇y to get (y◇x)◇z. In (x◇z)◇y, apply commutativity to x◇z to get (z◇x)◇y. "
            "These aren't obviously equal. But we can use commutativity on the outer operation: "
            "(y◇x)◇z = z◇(y◇x) and (z◇x)◇y = y◇(z◇x). Still not matching. "
            "Actually, look more carefully at the target: (x◇y)◇z = (x◇z)◇y. "
            "Apply commutativity inside right side: (x◇z)◇y = (z◇x)◇y. "
            "Apply commutativity to outer operation on both sides: "
            "(x◇y)◇z = z◇(x◇y) and (z◇x)◇y = y◇(z◇x). "
            "Notice commutativity lets us swap arguments freely. So (x◇y)◇z = z◇(x◇y) = z◇(y◇x). "
            "And (x◇z)◇y = y◇(x◇z) = y◇(z◇x). "
            "We need z◇(y◇x) = y◇(z◇x). By commutativity this equals (y◇x)◇z = (z◇x)◇y. "
            "Substitute a=y, b=x, c=z in target: (a◇b)◇c = (a◇c)◇b — this is exactly the target "
            "with different variables. So this is circular. "
            "Let's try a counterexample on size 2. If ◇ is commutative, we have limited options. "
            "After checking: all commutative magmas on 2 elements satisfy this. TRUE."
        ),
    },
    {
        "eq1": "x ◇ (y ◇ z) = (x ◇ y) ◇ z",
        "eq2": "x ◇ x = x",
        "label": "FALSE",
        "rationale": (
            "Eq1 is associativity. Eq2 is idempotency. "
            "Counterexample: (Z, +) under addition. Addition is associative but not idempotent "
            "(1+1=2≠1). More simply, the magma ({0,1}, +mod2) is associative: "
            "0+(0+1)=0+1=1 and (0+0)+1=0+1=1 ✓, etc. But 1+1=0≠1, violating idempotency. FALSE."
        ),
    },
    {
        "eq1": "x ◇ y = x",
        "eq2": "x ◇ (y ◇ z) = x",
        "label": "TRUE",
        "rationale": (
            "Eq1: x◇y = x (left projection). For Eq2: x◇(y◇z). "
            "By Eq1 applied to the inner term: y◇z = y. So x◇(y◇z) = x◇y. "
            "By Eq1 again: x◇y = x. Hence x◇(y◇z) = x. TRUE."
        ),
    },
]


def format_demonstration(eq1: str, eq2: str, label: str, rationale: str = "") -> str:
    """Format a single demo for the many-shot prompt."""
    parts = [f"Equation 1: {eq1}", f"Equation 2: {eq2}"]
    if rationale:
        parts.append(f"Reasoning: {rationale}")
    parts.append(f"Answer: {label}")
    return "\n".join(parts)


def load_training_demos(filepath: str, equations: list) -> list:
    """Load training data and pair with equation strings."""
    demos = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            eq1_idx = rec.get('equation1_index', rec.get('eq1'))
            eq2_idx = rec.get('equation2_index', rec.get('eq2'))
            label = rec.get('implies', rec.get('label'))
            if eq1_idx is None or eq2_idx is None or label is None:
                continue
            eq1_str = equations[int(eq1_idx) - 1]
            eq2_str = equations[int(eq2_idx) - 1]
            demos.append({
                "eq1": eq1_str,
                "eq2": eq2_str,
                "eq1_idx": int(eq1_idx),
                "eq2_idx": int(eq2_idx),
                "label": "TRUE" if label else "FALSE",
            })
    return demos


def load_equations(filepath: str = "equations.txt") -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def augment_with_rationales(
    demos: list,
    client: LLMClient,
    n_demos: int = 0,
) -> list:
    """Add rationale explanations to demos using X-ICL meta-prompting.

    Uses SEED_RATIONALES as few-shot examples for the meta-prompt,
    then generates rationales for each training demo.
    """
    seed_text = "\n\n".join(
        format_demonstration(s["eq1"], s["eq2"], s["label"], s["rationale"])
        for s in SEED_RATIONALES
    )

    target = demos if n_demos == 0 else demos[:n_demos]
    augmented = []

    for i, demo in enumerate(target):
        prompt = RATIONALE_META_PROMPT.format(
            seed_examples=seed_text,
            eq1=demo["eq1"],
            eq2=demo["eq2"],
            label=demo["label"],
        )
        resp = client.call(prompt, max_tokens=512, temperature=0.0)
        demo_copy = dict(demo)
        demo_copy["rationale"] = resp.text.strip()
        augmented.append(demo_copy)
        logger.info(f"  Rationale {i+1}/{len(target)}: {len(resp.text)} chars, cost=${resp.cost_usd:.4f}")

    return augmented


def build_demonstrations_text(demos: list, include_rationale: bool = True) -> str:
    """Build the full demonstrations block for the cheatsheet creation prompt."""
    parts = []
    for i, d in enumerate(demos):
        rat = d.get("rationale", "") if include_rationale else ""
        parts.append(f"Example {i+1}:\n" + format_demonstration(d["eq1"], d["eq2"], d["label"], rat))
    return "\n\n".join(parts)


def distill_cheatsheet(
    demos: list,
    client: LLMClient,
    config: ExperimentConfig,
    prompt_variant: str = "default",
) -> str:
    """Create a cheatsheet by distilling many-shot demos through an LLM.

    This is the core Honda et al. method: feed demonstrations to a strong
    model and ask it to produce a compact cheat sheet.
    """
    demo_text = build_demonstrations_text(demos, include_rationale=config.use_rationale_augmentation)
    template = CHEATSHEET_PROMPT_VARIANTS.get(prompt_variant, CHEATSHEET_CREATION_PROMPT)

    prompt = template.format(
        demonstrations=demo_text,
        max_bytes=config.cheatsheet_max_bytes,
    )

    logger.info(f"Distillation prompt length: {len(prompt)} chars")
    resp = client.call(prompt, max_tokens=config.cheatsheet_max_bytes // 2, temperature=0.3)
    cheatsheet = resp.text.strip()

    # Enforce byte limit
    encoded = cheatsheet.encode('utf-8')
    if len(encoded) > config.cheatsheet_max_bytes:
        logger.warning(
            f"Cheatsheet {len(encoded)} bytes exceeds {config.cheatsheet_max_bytes}. Truncating."
        )
        cheatsheet = encoded[:config.cheatsheet_max_bytes].decode('utf-8', errors='ignore')

    return cheatsheet


def run_pipeline(
    training_data: str,
    config: ExperimentConfig,
    prompt_variant: str = "default",
    output_path: Optional[str] = None,
):
    """Run the full distillation pipeline.

    Steps:
      1. Load equations and training demonstrations
      2. Sample n_shots demos (balanced TRUE/FALSE)
      3. Optionally augment with rationales
      4. Distill into cheatsheet
      5. Save result
    """
    # Setup
    equations = load_equations()
    CHEATSHEETS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load and sample demos
    all_demos = load_training_demos(training_data, equations)
    logger.info(f"Loaded {len(all_demos)} training demos")

    # Balanced sampling
    true_demos = [d for d in all_demos if d["label"] == "TRUE"]
    false_demos = [d for d in all_demos if d["label"] == "FALSE"]
    rng = random.Random(config.seed)
    rng.shuffle(true_demos)
    rng.shuffle(false_demos)
    half = config.n_shots // 2
    demos = true_demos[:half] + false_demos[:half]
    rng.shuffle(demos)
    logger.info(f"Sampled {len(demos)} demos ({half} TRUE, {half} FALSE)")

    # Initialize distillation model
    distill_client = LLMClient(config.distill_model)

    # Rationale augmentation
    if config.use_rationale_augmentation:
        logger.info("Augmenting demos with rationales (X-ICL)...")
        rationale_client = LLMClient(config.distill_model)
        demos = augment_with_rationales(demos, rationale_client)
        logger.info(f"Rationale augmentation complete. {rationale_client.cost_report()}")

    # Distill
    logger.info(f"Distilling cheatsheet (variant: {prompt_variant})...")
    cheatsheet = distill_cheatsheet(demos, distill_client, config, prompt_variant)

    # Save
    if output_path is None:
        output_path = str(CHEATSHEETS_DIR / f"cheatsheet_{config.name}_{prompt_variant}.txt")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cheatsheet)

    size = len(cheatsheet.encode('utf-8'))
    logger.info(f"Cheatsheet saved to {output_path} ({size} bytes)")
    logger.info(distill_client.cost_report())

    # Save metadata
    meta = {
        "config": config.__dict__,
        "prompt_variant": prompt_variant,
        "cheatsheet_bytes": size,
        "n_demos_used": len(demos),
        "distill_cost": distill_client.total_cost,
        "distill_calls": distill_client.total_calls,
    }
    meta_path = output_path.replace('.txt', '_meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, default=str)

    return cheatsheet


def main():
    parser = argparse.ArgumentParser(description="Distill a cheat sheet from training data")
    parser.add_argument("--data", required=True, help="JSONL training data file")
    parser.add_argument("--config-name", default="default", help="Experiment config name")
    parser.add_argument("--distill-model", default="gpt-4.1", help="Model for distillation")
    parser.add_argument("--n-shots", type=int, default=150, help="Number of demos to use")
    parser.add_argument("--variant", default="default",
                        choices=list(CHEATSHEET_PROMPT_VARIANTS.keys()),
                        help="Prompt variant")
    parser.add_argument("--no-rationale", action="store_true", help="Skip rationale augmentation")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = ExperimentConfig(
        name=args.config_name,
        distill_model=args.distill_model,
        n_shots=args.n_shots,
        use_rationale_augmentation=not args.no_rationale,
        seed=args.seed,
    )

    run_pipeline(
        training_data=args.data,
        config=config,
        prompt_variant=args.variant,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
