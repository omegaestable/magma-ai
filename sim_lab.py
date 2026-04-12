#!/usr/bin/env python3
"""
sim_lab — SAIR Equational Theories Stage 1 evaluator.

Aligned with the official SAIRcompetition/equational-theories-stage1-judge:
  - Prompt: cheatsheet IS the complete prompt (raw mode, default)
  - Models: GPT-OSS-120B, Llama 3.3 70B, Gemma 4 31B IT (all 3 official)
  - Parsing: 3-tier verdict extraction (boxed > labeled > line)
  - Scoring: strict F1 (unparsed TRUE → FN, unparsed FALSE → FP)

Usage:
    python sim_lab.py --data file.jsonl --cheatsheet cheatsheets/v24j.txt
    python sim_lab.py --subset normal --n 60 --cheatsheet cheatsheets/v24j.txt
    python sim_lab.py --subset hard3 --cheatsheet cheatsheets/v24j.txt --repeats 3
    python sim_lab.py --data file.jsonl --cheatsheet cheatsheets/v24j.txt --model gpt-oss-120b
    python sim_lab.py --data file.jsonl --cheatsheet cheatsheets/v24j.txt --all-models
"""

import argparse
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import requests
from filelock import FileLock

# ── Constants ─────────────────────────────────────────────────────────────

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct"
DEFAULT_REPEATS = 1
DEFAULT_TIMEOUT_S = 600
DEFAULT_RETRY_BUDGET_S = 120
CHEATSHEET_MAX_BYTES = 10_240

# Cross-process API lock: prevents parallel sim_lab.py processes from
# causing a 429 retry death spiral on the same OpenRouter API key.
_API_LOCK_PATH = Path(__file__).parent / "data" / ".sim_lab_api.lock"
_API_LOCK = FileLock(_API_LOCK_PATH, timeout=600)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HF_DATASET = "SAIRfoundation/equational-theories-selected-problems"
HF_SUBSETS = ("normal", "hard", "hard1", "hard2", "hard3")
HF_CACHE_DIR = Path(__file__).parent / "data" / "hf_cache"

EVAL_TEMPLATE_URL = (
    "https://huggingface.co/datasets/"
    "SAIRfoundation/equational-theories-benchmark"
    "/raw/main/prompts/evaluation.jinja2"
)
EVAL_TEMPLATE_CACHE = HF_CACHE_DIR / "evaluation.jinja2"

# ── Official evaluation model configs ─────────────────────────────────────
# Source: https://github.com/SAIRcompetition/equational-theories-stage1-judge
#         evaluation_models.json (commit 5086db8, 2026-04-10)

# Provider name map: config slug  →  OpenRouter title-case name
_PROVIDER_DISPLAY = {
    "deepinfra": "DeepInfra",
    "novita": "Novita",
}

OFFICIAL_MODELS = {
    "gpt-oss-120b": {
        "model": "openai/gpt-oss-120b",
        "provider": "deepinfra/bf16",
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "seed": 0,
        "reasoning_mode": "low",
    },
    "llama-3-3-70b-instruct": {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "provider": "deepinfra/fp8",
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "seed": 0,
        "reasoning_mode": "disabled",
    },
    "gemma-4-31b-it": {
        "model": "google/gemma-4-31b-it",
        "provider": "novita/bf16",
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "seed": 0,
        "reasoning_mode": "disabled",
    },
}

ALL_OFFICIAL_MODEL_ALIASES = list(OFFICIAL_MODELS.keys())


# ── Data structures ───────────────────────────────────────────────────────

@dataclass
class Problem:
    id: str
    index: int
    difficulty: str
    equation1: str
    equation2: str
    answer: bool


@dataclass
class Result:
    problem: Problem
    repeat_id: int
    verdict: Optional[bool]
    raw_response: str
    elapsed_s: float
    usage: Optional[dict] = None


@dataclass
class RunStats:
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    unparsed: int = 0
    true_total: int = 0
    true_correct: int = 0
    false_total: int = 0
    false_correct: int = 0
    elapsed_total: float = 0.0
    results: list = field(default_factory=list)
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def true_accuracy(self) -> float:
        return self.true_correct / self.true_total if self.true_total else 0.0

    @property
    def false_accuracy(self) -> float:
        return self.false_correct / self.false_total if self.false_total else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def parse_rate(self) -> float:
        return (self.total - self.unparsed) / self.total if self.total else 0.0

    @property
    def avg_time(self) -> float:
        return self.elapsed_total / self.total if self.total else 0.0


# ── Data loading ──────────────────────────────────────────────────────────

def _normalize_eq(eq: str) -> str:
    return eq.replace("\u25c7", "*").strip()


def download_hf_subset(subset: str) -> Path:
    if subset not in HF_SUBSETS:
        raise ValueError(f"Unknown subset '{subset}'. Choose from: {HF_SUBSETS}")
    cache_path = HF_CACHE_DIR / f"{subset}.jsonl"
    if cache_path.exists():
        return cache_path
    url = (
        f"https://huggingface.co/datasets/{HF_DATASET}"
        f"/resolve/main/data/{subset}.jsonl"
    )
    print(f"Downloading {subset} from HuggingFace ...")
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    print(f"  Cached → {cache_path}  ({len(r.content):,} bytes)")
    return cache_path


def download_eval_template() -> str:
    if EVAL_TEMPLATE_CACHE.exists():
        return EVAL_TEMPLATE_CACHE.read_text(encoding="utf-8")
    print("Downloading evaluation template from HuggingFace ...")
    EVAL_TEMPLATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(EVAL_TEMPLATE_URL, timeout=60)
    r.raise_for_status()
    EVAL_TEMPLATE_CACHE.write_bytes(r.content)
    print(f"  Cached → {EVAL_TEMPLATE_CACHE}")
    return r.content.decode("utf-8")


def load_problems(
    path: Optional[str] = None,
    subset: Optional[str] = None,
    n: Optional[int] = None,
    shuffle: bool = False,
) -> list[Problem]:
    if subset:
        resolved = download_hf_subset(subset)
    elif path:
        resolved = Path(path)
    else:
        raise ValueError("Provide --data or --subset")

    problems = []
    with open(resolved, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            problems.append(Problem(
                id=obj["id"],
                index=obj.get("index", 0),
                difficulty=obj.get("difficulty", "unknown"),
                equation1=_normalize_eq(obj["equation1"]),
                equation2=_normalize_eq(obj["equation2"]),
                answer=bool(obj["answer"]),
            ))

    if shuffle:
        import random
        random.shuffle(problems)

    if n is not None:
        problems = problems[:n]

    return problems


def load_cheatsheet(path: str) -> str:
    p = Path(path)
    raw = p.read_bytes()
    size = len(raw)
    if size > CHEATSHEET_MAX_BYTES:
        print(f"WARNING: cheatsheet {size:,} bytes — exceeds 10 KB cap!")
    else:
        print(f"Cheatsheet: {size:,} / {CHEATSHEET_MAX_BYTES:,} bytes "
              f"({100 * size / CHEATSHEET_MAX_BYTES:.1f}%)")
    return raw.decode("utf-8")


# ── Prompt rendering ──────────────────────────────────────────────────────

def render_prompt(
    problem: Problem, cheatsheet: str, prompt_mode: str = "raw",
) -> str:
    """Render the prompt sent to the model.

    prompt_mode:
      'raw'     — cheatsheet IS the complete prompt (official judge behaviour).
                   Only {{equation1}} / {{equation2}} substitution.  No Jinja2.
      'wrapped' — legacy: evaluation.jinja2 wraps the cheatsheet (pre-April-2026).
    """
    eq1 = problem.equation1
    eq2 = problem.equation2

    # Substitute equation placeholders (both spaced and no-space variants)
    rendered = cheatsheet
    rendered = rendered.replace("{{equation1}}", eq1)
    rendered = rendered.replace("{{ equation1 }}", eq1)
    rendered = rendered.replace("{{equation2}}", eq2)
    rendered = rendered.replace("{{ equation2 }}", eq2)

    if prompt_mode == "wrapped":
        import jinja2
        template_src = download_eval_template()
        return jinja2.Template(template_src).render(
            equation1=eq1,
            equation2=eq2,
            cheatsheet=rendered,
        )

    # raw mode: the rendered cheatsheet is the complete prompt
    return rendered


# ── Verdict parsing (3-tier, ported from official judge.py) ──────────────
# Source: SAIRcompetition/equational-theories-stage1-judge/judge.py
# Priority: boxed (3) > labeled (2) > line (1)
# Within same tier: last occurrence wins.

_BOXED_START_RE = re.compile(r"(?i)\\+boxed\s*\{")
_VERDICT_RE = re.compile(r"(?i)\bVERDICT\s*[:：]\s*(TRUE|FALSE)\b")
_ANSWER_RE = re.compile(
    r"(?i)\b(?:FINAL\s+ANSWER|ANSWER|OUTPUT_RESULT|RESULT)\s*[:：=\-]\s*(TRUE|FALSE)\b"
)
_LATEX_TEXT_RE = re.compile(r"(?i)\\text\s*\{\s*(TRUE|FALSE)\s*\}")
_LINE_RE = re.compile(
    r"(?i)^\s*(?:FINAL\s+ANSWER\s*[:：=\-]\s*)?(TRUE|FALSE)\s*[.!?]*\s*$"
)
_LATEX_WRAPPER_RE = re.compile(
    r"(?is)^\\(?:text|mathrm|mathbf|operatorname)\s*\{(.+)\}$"
)


class _VerdictSource(Enum):
    """Verdict source, with numeric priority (higher wins)."""
    LINE = 1
    LABELED = 2
    BOXED = 3


@dataclass
class _VerdictCandidate:
    value: bool
    source: _VerdictSource
    index: int  # byte offset for tie-breaking


def _strip_markdown(s: str) -> str:
    return s.replace("***", "").replace("**", "").replace("__", "").replace("`", "")


def _parse_bool(label: str) -> Optional[bool]:
    u = label.upper()
    if u == "TRUE":
        return True
    if u == "FALSE":
        return False
    return None


def _is_or_clause(response: str, match_end: int) -> bool:
    after = response[match_end:].split("\n", 1)[0].lstrip()
    if after[:2].upper() == "OR":
        rest = after[2:]
        return not rest or rest[0].isspace()
    if after.startswith("/"):
        return bool(re.match(r"(?i)(TRUE|FALSE)\b", after[1:].lstrip()))
    return False


def _parse_boxed_content(token: str) -> Optional[bool]:
    STRIP = " \t\r\n.,;:!?$()[]"
    current = token.strip()
    for _ in range(4):
        current = current.strip(STRIP)
        if current.upper() == "ANSWER":
            return None
        verdict = _parse_bool(current)
        if verdict is not None:
            return verdict
        m = _LATEX_WRAPPER_RE.match(current)
        if m:
            current = m.group(1)
            continue
        break
    return None


def _extract_boxed(response: str, out: list) -> None:
    for m in _BOXED_START_RE.finditer(response):
        depth = 1
        cs = m.end()
        ce = None
        for i, ch in enumerate(response[cs:]):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    ce = cs + i
                    break
        if ce is None:
            continue
        value = _parse_boxed_content(response[cs:ce])
        if value is not None:
            out.append(_VerdictCandidate(value=value, source=_VerdictSource.BOXED, index=m.start()))


def _extract_labeled(response: str, out: list) -> None:
    for pattern in (_VERDICT_RE, _ANSWER_RE, _LATEX_TEXT_RE):
        for m in pattern.finditer(response):
            if _is_or_clause(response, m.end()):
                continue
            value = _parse_bool(m.group(1))
            if value is not None:
                out.append(_VerdictCandidate(value=value, source=_VerdictSource.LABELED, index=m.start()))


def _extract_leading_line(response: str, out: list) -> None:
    first = next((line for line in response.splitlines() if line.strip()), None)
    if first is None:
        return
    m = _LINE_RE.match(first)
    if not m:
        return
    value = _parse_bool(m.group(1))
    if value is not None:
        out.append(_VerdictCandidate(value=value, source=_VerdictSource.LINE, index=0))


def _extract_trailing_line(response: str, out: list) -> None:
    last = next((line for line in reversed(response.splitlines()) if line.strip()), None)
    if last is None:
        return
    m = _LINE_RE.match(last)
    if not m:
        return
    value = _parse_bool(m.group(1))
    if value is not None:
        out.append(_VerdictCandidate(value=value, source=_VerdictSource.LINE, index=len(response)))


def parse_verdict(response: str) -> Optional[bool]:
    """Extract TRUE/FALSE verdict using official 3-tier priority system.

    Priority: \\boxed{} (3) > VERDICT:/ANSWER:/\\text{} (2) > first/last line (1).
    Within same tier, last occurrence wins.
    """
    cleaned = _strip_markdown(response)
    candidates: list[_VerdictCandidate] = []
    _extract_boxed(cleaned, candidates)
    _extract_labeled(cleaned, candidates)
    _extract_leading_line(cleaned, candidates)
    _extract_trailing_line(cleaned, candidates)
    if not candidates:
        return None
    top_priority = max(c.source.value for c in candidates)
    top = [c for c in candidates if c.source.value == top_priority]
    chosen = max(top, key=lambda c: c.index)
    return chosen.value


# ── OpenRouter API ────────────────────────────────────────────────────────

def resolve_model(model_arg: str) -> dict:
    """Resolve a model argument to full OpenRouter config.

    Accepts official aliases (gpt-oss-120b, llama-3-3-70b-instruct, gemma-4-31b-it)
    or raw OpenRouter model IDs.
    """
    if model_arg in OFFICIAL_MODELS:
        cfg = OFFICIAL_MODELS[model_arg].copy()
        cfg["alias"] = model_arg
        return cfg
    # Raw model ID fallback (e.g. "meta-llama/llama-3.3-70b-instruct")
    # Check if it matches any official model's full ID
    for alias, cfg in OFFICIAL_MODELS.items():
        if cfg["model"] == model_arg:
            out = cfg.copy()
            out["alias"] = alias
            return out
    # Unknown model: use basic config
    return {
        "model": model_arg,
        "provider": None,
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "seed": 0,
        "reasoning_mode": "disabled",
        "alias": model_arg,
    }


def query_openrouter(
    prompt: str,
    model_cfg: dict,
    api_key: str,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    max_retries: int = 5,
    retry_budget_s: int = DEFAULT_RETRY_BUDGET_S,
) -> tuple[str, float, Optional[dict]]:
    """Call OpenRouter with official evaluation config and retry on 429/5xx.

    Retry uses Retry-After header when available, otherwise jittered exponential
    backoff (initial 1s, multiplier 2×, max 30s).  A cross-process file lock
    serializes API calls to prevent parallel 429 death spirals.
    """
    t0 = time.time()
    payload: dict = {
        "model": model_cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": model_cfg.get("temperature", 0.0),
        "max_tokens": model_cfg.get("max_output_tokens", 8192),
        "seed": model_cfg.get("seed", 0),
    }
    # Provider routing (pinned, no fallbacks — matches official eval)
    provider = model_cfg.get("provider")
    if provider:
        # Split "deepinfra/bf16" → order=["DeepInfra"], quantizations=["bf16"]
        parts = provider.split("/", 1)
        provider_slug = parts[0]
        provider_name = _PROVIDER_DISPLAY.get(provider_slug, provider_slug)
        quant = parts[1] if len(parts) > 1 else None
        prov_cfg: dict = {
            "order": [provider_name],
            "allow_fallbacks": model_cfg.get("allow_fallbacks", False),
        }
        if quant:
            prov_cfg["quantizations"] = [quant]
        payload["provider"] = prov_cfg
    # Reasoning mode — official judge always sends this explicitly
    reasoning = model_cfg.get("reasoning_mode", "disabled")
    if reasoning and reasoning != "disabled":
        payload["reasoning"] = {"effort": reasoning}
    else:
        payload["reasoning"] = {"effort": "none"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    def _call_with_backoff(active_payload: dict, phase_label: str = "") -> tuple[str, float, Optional[dict]]:
        """Retry one payload with Retry-After-aware backoff and file lock."""
        last_exc = None
        last_status = None
        interval = 1.0
        max_interval = 30.0
        deadline = time.monotonic() + retry_budget_s
        attempt = 0
        while True:
            try:
                with _API_LOCK:
                    r = requests.post(
                        OPENROUTER_URL, headers=headers, json=active_payload, timeout=timeout_s,
                    )
                last_status = r.status_code
                if r.status_code == 429 or r.status_code >= 500:
                    # Log response body for diagnosis (rate_limit vs credits vs provider)
                    body_preview = ""
                    try:
                        body_preview = r.text[:200]
                    except Exception:
                        pass
                    # Respect Retry-After header if present
                    retry_after = None
                    ra_header = r.headers.get("Retry-After") or r.headers.get("retry-after")
                    if ra_header:
                        try:
                            retry_after = float(ra_header)
                        except (ValueError, TypeError):
                            pass
                    backoff = min(interval, max_interval) * random.uniform(0.5, 1.5)
                    wait = max(backoff, retry_after) if retry_after else backoff
                    remaining = deadline - time.monotonic()
                    # Extend budget if Retry-After exceeds it (cap at 300s total)
                    if retry_after and wait > remaining and (time.monotonic() - (deadline - retry_budget_s) + wait) <= 300:
                        deadline = time.monotonic() + wait + 5.0
                        remaining = deadline - time.monotonic()
                    if remaining <= 0 or remaining < wait:
                        label = f" ({phase_label})" if phase_label else ""
                        print(f"    ⚠ {r.status_code} — retry budget exhausted{label} after {time.time() - t0:.0f}s")
                        if body_preview:
                            print(f"    ⚠ body: {body_preview}")
                        break
                    attempt += 1
                    ra_note = f" [Retry-After: {retry_after:.0f}s]" if retry_after else ""
                    print(f"    ⚠ {r.status_code} — retrying in {wait:.1f}s (attempt {attempt}, {remaining:.0f}s left){ra_note}")
                    if attempt == 1 and body_preview:
                        print(f"    ⚠ body: {body_preview}")
                    time.sleep(wait)
                    interval = min(interval * 2, max_interval)
                    continue
                r.raise_for_status()
                data = r.json()
                elapsed = time.time() - t0
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage")
                norm_usage = None
                if usage:
                    norm_usage = {
                        "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                        "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
                    }
                return text, elapsed, norm_usage
            except requests.exceptions.RequestException as e:
                last_exc = e
                remaining = deadline - time.monotonic()
                wait = min(interval, max_interval) * random.uniform(0.5, 1.5)
                if remaining <= 0 or remaining < wait:
                    break
                attempt += 1
                print(f"    ⚠ {e} — retrying in {wait:.1f}s (attempt {attempt}, {remaining:.0f}s left)")
                time.sleep(wait)
                interval = min(interval * 2, max_interval)
        raise last_exc or RuntimeError(f"query_openrouter: retry budget exhausted ({retry_budget_s}s)")

    # Phase 1: official strict route (always first)
    try:
        text, elapsed, norm_usage = _call_with_backoff(payload, phase_label="strict")
        return text, elapsed, norm_usage
    except Exception as strict_err:
        # For llama+deepinfra/fp8, retry with progressively looser routing if strict fp8 is saturated.
        if model_cfg.get("alias") != "llama-3-3-70b-instruct" or model_cfg.get("provider") != "deepinfra/fp8":
            raise strict_err

    # Phase 2 (llama only): keep DeepInfra pin, drop fp8 quantization filter.
    payload_no_quant = dict(payload)
    if "provider" in payload_no_quant and isinstance(payload_no_quant["provider"], dict):
        payload_no_quant["provider"] = dict(payload_no_quant["provider"])
        payload_no_quant["provider"].pop("quantizations", None)
    print("    ⚠ llama fallback: retrying without fp8 quantization filter")
    try:
        text, elapsed, norm_usage = _call_with_backoff(payload_no_quant, phase_label="llama-no-quant")
        return text, elapsed, norm_usage
    except Exception:
        pass

    # Phase 3 (llama only): allow OpenRouter fallbacks as last resort.
    payload_allow_fallbacks = dict(payload_no_quant)
    if "provider" in payload_allow_fallbacks and isinstance(payload_allow_fallbacks["provider"], dict):
        payload_allow_fallbacks["provider"] = dict(payload_allow_fallbacks["provider"])
        payload_allow_fallbacks["provider"]["allow_fallbacks"] = True
    print("    ⚠ llama fallback: enabling provider fallbacks")
    text, elapsed, norm_usage = _call_with_backoff(payload_allow_fallbacks, phase_label="llama-fallbacks")
    return text, elapsed, norm_usage


# ── Evaluation engine ─────────────────────────────────────────────────────

def evaluate_one(
    problem: Problem,
    cheatsheet: str,
    model_cfg: dict,
    api_key: str,
    repeat_id: int = 1,
    prompt_mode: str = "raw",
    retry_budget_s: int = DEFAULT_RETRY_BUDGET_S,
) -> Result:
    prompt = render_prompt(problem, cheatsheet, prompt_mode=prompt_mode)
    try:
        response, elapsed, usage = query_openrouter(prompt, model_cfg, api_key, retry_budget_s=retry_budget_s)
    except Exception as e:
        return Result(
            problem=problem,
            repeat_id=repeat_id,
            verdict=None,
            raw_response=f"ERROR: {e}",
            elapsed_s=0.0,
            usage=None,
        )
    verdict = parse_verdict(response)
    return Result(
        problem=problem,
        repeat_id=repeat_id,
        verdict=verdict,
        raw_response=response,
        elapsed_s=elapsed,
        usage=usage,
    )


def _update_stats(stats: RunStats, result: Result) -> str:
    p = result.problem
    stats.total += 1
    stats.elapsed_total += result.elapsed_s
    stats.results.append(result)
    if result.usage:
        stats.prompt_tokens += result.usage.get("prompt_tokens", 0)
        stats.completion_tokens += result.usage.get("completion_tokens", 0)

    if p.answer:
        stats.true_total += 1
    else:
        stats.false_total += 1

    if result.verdict is None:
        stats.unparsed += 1
        if p.answer:
            stats.fn += 1
        else:
            stats.fp += 1
        return "?"

    correct = result.verdict == p.answer
    if correct:
        stats.correct += 1
        if p.answer:
            stats.true_correct += 1
        else:
            stats.false_correct += 1
    else:
        stats.incorrect += 1

    if result.verdict and p.answer:
        stats.tp += 1
    elif result.verdict and not p.answer:
        stats.fp += 1
    elif not result.verdict and p.answer:
        stats.fn += 1
    else:
        stats.tn += 1

    return "✓" if correct else "✗"


def run_evaluation(
    problems: list[Problem],
    cheatsheet: str,
    model_cfg: dict,
    api_key: str,
    repeats: int = DEFAULT_REPEATS,
    verbose: bool = True,
    checkpoint_path: Optional[str] = None,
    prompt_mode: str = "raw",
    retry_budget_s: int = DEFAULT_RETRY_BUDGET_S,
) -> RunStats:
    stats = RunStats()
    total_runs = len(problems) * repeats

    # Resume from checkpoint
    done: set[tuple[str, int]] = set()
    if checkpoint_path and Path(checkpoint_path).exists():
        try:
            ckpt = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
            for r in ckpt.get("results", []):
                done.add((r["id"], r["repeat_id"]))
            print(f"  Resuming: {len(done)} runs cached")
        except Exception:
            pass

    run_idx = 0
    for problem in problems:
        for rep in range(1, repeats + 1):
            run_idx += 1
            if (problem.id, rep) in done:
                if verbose:
                    print(f"  [{run_idx:4d}/{total_runs}] {problem.id:15s} r{rep}  (cached)")
                continue

            result = evaluate_one(
                problem, cheatsheet, model_cfg, api_key, rep,
                prompt_mode=prompt_mode,
                retry_budget_s=retry_budget_s,
            )
            mark = _update_stats(stats, result)

            if verbose:
                gt = "T" if problem.answer else "F"
                pred = "T" if result.verdict is True else ("F" if result.verdict is False else "?")
                print(
                    f"  [{run_idx:4d}/{total_runs}] {problem.id:15s} "
                    f"gt={gt} pred={pred} {mark}  "
                    f"{result.elapsed_s:5.1f}s  "
                    f"acc={stats.accuracy:.1%}  f1={stats.f1:.1%}"
                )

            # Incremental checkpoint
            if checkpoint_path:
                _save_checkpoint(stats, checkpoint_path, model_cfg["model"])

    return stats


def _save_checkpoint(stats: RunStats, path: str, model: str):
    data = {
        "model": model,
        "checkpoint": True,
        "results": [_result_to_dict(r) for r in stats.results],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _result_to_dict(r: Result) -> dict:
    return {
        "id": r.problem.id,
        "repeat_id": r.repeat_id,
        "equation1": r.problem.equation1,
        "equation2": r.problem.equation2,
        "ground_truth": r.problem.answer,
        "predicted": r.verdict,
        "correct": r.verdict == r.problem.answer if r.verdict is not None else False,
        "parsed_ok": r.verdict is not None,
        "elapsed_s": round(r.elapsed_s, 2),
        "raw_response": r.raw_response,
        "usage": r.usage,
    }


# ── Reporting ─────────────────────────────────────────────────────────────

def print_report(stats: RunStats, label: str = ""):
    hdr = f"═══ Results{': ' + label if label else ''} ═══"
    print(f"\n{'═' * len(hdr)}")
    print(hdr)
    print(f"{'═' * len(hdr)}")
    print(f"  Total:        {stats.total}")
    print(f"  Correct:      {stats.correct}")
    print(f"  Incorrect:    {stats.incorrect}")
    print(f"  Unparsed:     {stats.unparsed}")
    print(f"  ─────────────────────────")
    print(f"  Accuracy:     {stats.accuracy:.1%}")
    print(f"  F1 (strict):  {stats.f1:.1%}")
    print(f"  Precision:    {stats.precision:.1%}")
    print(f"  Recall:       {stats.recall:.1%}")
    print(f"  Parse rate:   {stats.parse_rate:.1%}")
    print(f"  ─────────────────────────")
    print(f"  TRUE acc:     {stats.true_accuracy:.1%}  ({stats.true_correct}/{stats.true_total})")
    print(f"  FALSE acc:    {stats.false_accuracy:.1%}  ({stats.false_correct}/{stats.false_total})")
    print(f"  TP/FP/FN/TN:  {stats.tp}/{stats.fp}/{stats.fn}/{stats.tn}")
    print(f"  ─────────────────────────")
    print(f"  Avg time:     {stats.avg_time:.1f}s")
    print(f"  Total time:   {stats.elapsed_total:.1f}s")
    print()


def print_errors(stats: RunStats, top_n: int = 10):
    errors = [r for r in stats.results if r.verdict is not None and r.verdict != r.problem.answer]
    unparsed = [r for r in stats.results if r.verdict is None]
    fn = [r for r in errors if r.problem.answer and not r.verdict]
    fp = [r for r in errors if not r.problem.answer and r.verdict]

    print(f"\n  ERROR ANALYSIS")
    print(f"  Total errors: {len(errors)}  |  FN: {len(fn)}  |  FP: {len(fp)}  |  Unparsed: {len(unparsed)}")

    if fn:
        print(f"\n  False negatives (should be TRUE):")
        for r in fn[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")
    if fp:
        print(f"\n  False positives (should be FALSE):")
        for r in fp[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")
    if unparsed:
        print(f"\n  Unparsed:")
        for r in unparsed[:top_n]:
            print(f"    {r.problem.id}: {r.raw_response[:100]}...")
    print()


def save_results(stats: RunStats, output_path: str, model: str,
                 cheatsheet_path: Optional[str], subset: Optional[str] = None,
                 repeats: int = 1):
    data = {
        "model": model,
        "cheatsheet": cheatsheet_path or "(none)",
        "subset": subset or "(local)",
        "repeats": repeats,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": stats.total,
            "correct": stats.correct,
            "incorrect": stats.incorrect,
            "unparsed": stats.unparsed,
            "accuracy": round(stats.accuracy, 4),
            "f1_score": round(stats.f1, 4),
            "precision": round(stats.precision, 4),
            "recall": round(stats.recall, 4),
            "parse_rate": round(stats.parse_rate, 4),
            "true_accuracy": round(stats.true_accuracy, 4),
            "false_accuracy": round(stats.false_accuracy, 4),
            "tp": stats.tp, "fp": stats.fp, "fn": stats.fn, "tn": stats.tn,
            "avg_time_s": round(stats.avg_time, 2),
            "total_time_s": round(stats.elapsed_total, 2),
            "prompt_tokens": stats.prompt_tokens,
            "completion_tokens": stats.completion_tokens,
        },
        "results": [_result_to_dict(r) for r in stats.results],
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved → {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────

def _run_single_model(
    args, model_cfg: dict, problems: list, cheatsheet: str, api_key: str,
) -> None:
    """Run evaluation for a single model and save results."""
    alias = model_cfg.get("alias", model_cfg["model"])
    model_id = model_cfg["model"]

    true_count = sum(1 for p in problems if p.answer)
    false_count = len(problems) - true_count
    source = args.subset or args.data
    total_runs = len(problems) * args.repeats

    print(f"\n{'═' * 60}")
    print(f"  SAIR Stage 1 Simulation Lab")
    print(f"{'═' * 60}")
    print(f"  Model:       {alias} ({model_id})")
    print(f"  Provider:    {model_cfg.get('provider', 'auto')}")
    print(f"  Prompt mode: {args.prompt_mode}")
    print(f"  Source:      {source}")
    print(f"  Problems:    {len(problems)} (T:{true_count} F:{false_count})")
    print(f"  Repeats:     {args.repeats}")
    print(f"  Total:       {total_runs} runs")
    print(f"  Cheatsheet:  {args.cheatsheet}")
    print(f"{'═' * 60}\n")

    # Checkpoint path
    ckpt = None
    if args.resume:
        cs_label = Path(args.cheatsheet).stem
        sub_label = args.subset or Path(args.data).stem
        safe_alias = alias.replace("/", "_")
        ckpt = f"results/sim_{sub_label}_{cs_label}_{safe_alias}_latest.json.checkpoint"

    stats = run_evaluation(
        problems, cheatsheet, model_cfg, api_key,
        repeats=args.repeats, verbose=not args.quiet,
        checkpoint_path=ckpt,
        prompt_mode=args.prompt_mode,
        retry_budget_s=args.retry_budget,
    )

    print_report(stats, f"{Path(args.cheatsheet).stem} / {alias}")

    if args.errors:
        print_errors(stats)

    # Save results
    if args.output and not args.all_models:
        out = args.output
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        cs_label = Path(args.cheatsheet).stem
        sub_label = args.subset or Path(args.data).stem
        safe_alias = alias.replace("/", "_").replace(".", "_")
        out = f"results/sim_{sub_label}_{cs_label}_{safe_alias}_{ts}.json"

    save_results(stats, out, model_id, args.cheatsheet,
                 subset=args.subset, repeats=args.repeats)

    # Clean checkpoint
    if ckpt and Path(ckpt).exists():
        Path(ckpt).unlink()


def main():
    ap = argparse.ArgumentParser(
        description="SAIR Stage 1 Simulation Lab (aligned with official judge)",
    )
    ap.add_argument("--subset", choices=list(HF_SUBSETS))
    ap.add_argument("--data", help="Local JSONL benchmark file")
    ap.add_argument("--cheatsheet", required=True, help="Cheatsheet path")
    ap.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="Model alias (gpt-oss-120b, llama-3-3-70b-instruct, gemma-4-31b-it) "
             "or full OpenRouter model ID",
    )
    ap.add_argument(
        "--all-models", action="store_true",
        help="Run on all 3 official evaluation models sequentially",
    )
    ap.add_argument("--n", type=int, help="Limit number of problems")
    ap.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--output", help="Output JSON path (ignored with --all-models)")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--errors", action="store_true", help="Print error analysis")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--api-key", default=None)
    ap.add_argument(
        "--prompt-mode", default="raw", choices=["raw", "wrapped"],
        help="raw = cheatsheet IS the prompt (official). "
             "wrapped = legacy eval template wrapping.",
    )
    ap.add_argument(
        "--allow-fallbacks", action="store_true",
        help="Allow OpenRouter to fall back to alternate providers (lab use only). "
             "Official eval uses strict pinning.",
    )
    ap.add_argument(
        "--retry-budget", type=int, default=DEFAULT_RETRY_BUDGET_S,
        help=f"Per-phase retry budget in seconds (default {DEFAULT_RETRY_BUDGET_S}). "
             "Retry-After headers can extend this up to 300s.",
    )
    # Retained for CLI compatibility with old scripts
    ap.add_argument("--openrouter", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--parser", default="strict", help=argparse.SUPPRESS)

    args = ap.parse_args()

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: set OPENROUTER_API_KEY or pass --api-key")
        sys.exit(1)

    if not args.subset and not args.data:
        print("ERROR: provide --subset or --data")
        sys.exit(1)
    if args.data and not Path(args.data).exists():
        print(f"ERROR: file not found: {args.data}")
        sys.exit(1)

    # Pre-download evaluation template (only needed for wrapped mode)
    if args.prompt_mode == "wrapped":
        download_eval_template()

    problems = load_problems(
        path=args.data, subset=args.subset,
        n=args.n, shuffle=args.shuffle,
    )

    cheatsheet = load_cheatsheet(args.cheatsheet)

    # Resolve model(s) to run
    if args.all_models:
        model_cfgs = [resolve_model(alias) for alias in ALL_OFFICIAL_MODEL_ALIASES]
    else:
        model_cfgs = [resolve_model(args.model)]

    # Lab override: allow provider fallbacks to work around rate limits
    if args.allow_fallbacks:
        for cfg in model_cfgs:
            cfg["allow_fallbacks"] = True

    for model_cfg in model_cfgs:
        _run_single_model(args, model_cfg, problems, cheatsheet, api_key)


if __name__ == "__main__":
    main()
