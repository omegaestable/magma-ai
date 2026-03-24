#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import shutil
import subprocess
from pathlib import Path


def build_prompt(champion_path: str, failure_summary_path: str, mutation_focus: str,
                 distillation_brief_path: str = "", witness_brief_path: str = "",
                 max_bytes: int = 10240) -> str:
    distillation_section = ""
    if distillation_brief_path:
        try:
            brief = Path(distillation_brief_path).read_text(encoding="utf-8").strip()
            distillation_section = f"""

Distillation signal (ranked failure patterns from the last evaluation run):
{brief}
"""
        except OSError:
            pass  # Brief is optional; skip gracefully if file is missing

    witness_section = ""
    if witness_brief_path:
        try:
            witness_brief = Path(witness_brief_path).read_text(encoding="utf-8").strip()
            witness_section = f"""

Verified witness signal (small magmas that recently separated false positives):
{witness_brief}
"""
        except OSError:
            pass

    return f"""Return ONLY the full revised cheatsheet as plain text.
Do not use markdown fences.
Do not add commentary before or after the cheatsheet.

Use the current workspace files as inputs.

Task:
- Read {champion_path}
- Read {failure_summary_path}
- Produce one candidate revision focused on: {mutation_focus}{distillation_section}{witness_section}
Hard constraints:
- Keep {{{{ equation1 }}}} and {{{{ equation2 }}}} templating valid.
- Preserve strict verdict formatting and the four required headers.
- Keep the candidate under {max_bytes} bytes on disk.
- Byte budget is strict: if close to limit, compress wording and remove non-essential examples.
- Prefer a minimal targeted diff, not a rewrite.
- No unconditional TRUE or FALSE fallback.
- Do not invent counterexamples.
- Optimize for balanced normal gates, not skewed samples.

Output only the revised cheatsheet text.
"""


def resolve_command(command: str) -> str:
    if command == "copilot":
        cmd_variant = shutil.which("copilot.cmd")
        if cmd_variant:
            return cmd_variant
    resolved = shutil.which(command)
    return resolved or command


def strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a candidate cheatsheet via Copilot CLI.")
    parser.add_argument("--champion-path", required=True)
    parser.add_argument("--candidate-path", required=True)
    parser.add_argument("--failure-summary-path", required=True)
    parser.add_argument("--mutation-focus", required=True)
    parser.add_argument("--copilot-command", default="copilot")
    parser.add_argument("--copilot-model", default="")
    parser.add_argument("--max-bytes", type=int, default=10240)
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--distillation-brief-path", default="",
                        help="Optional path to a distillation brief .md file to inject into the prompt")
    parser.add_argument("--witness-brief-path", default="",
                        help="Optional path to a verified witness brief .md file to inject into the prompt")
    args = parser.parse_args()

    prompt = build_prompt(
        args.champion_path,
        args.failure_summary_path,
        args.mutation_focus,
        distillation_brief_path=args.distillation_brief_path,
        witness_brief_path=args.witness_brief_path,
        max_bytes=args.max_bytes,
    )

    command = [
        resolve_command(args.copilot_command),
        "--silent",
        "--no-ask-user",
        "--allow-all-tools",
        f"--prompt={prompt}",
    ]
    if args.copilot_model:
        command.extend(["--model", args.copilot_model])

    completed = None
    last_error = ""
    for attempt in range(args.max_retries + 1):
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=args.timeout_s,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            break
        last_error = completed.stderr.strip() or completed.stdout.strip() or "Copilot CLI failed"
        if attempt < args.max_retries:
            time.sleep(1.5 * (attempt + 1))

    if completed is None or completed.returncode != 0:
        raise RuntimeError(last_error or "Copilot CLI failed")

    candidate = strip_fences(completed.stdout)
    if not candidate:
        raise RuntimeError("Copilot CLI returned empty output.")

    candidate_path = Path(args.candidate_path)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(candidate.rstrip() + "\n", encoding="utf-8")
    size = candidate_path.stat().st_size
    if size > args.max_bytes:
        raise RuntimeError(f"Candidate exceeds byte limit: {size} > {args.max_bytes}")
    print(f"Wrote {candidate_path} ({size} bytes)")


if __name__ == "__main__":
    main()