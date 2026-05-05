#!/usr/bin/env python3
"""Interactive CLI for running a submission against a local problem set.

Same underlying engine as ``pipeline/runner.py`` (``pipeline.proxy.run_solver``),
but with colorized per-problem rows, a per-problem debug log, and an ANSI
status line for humans driving the local-CLI model (no HTTP server, no
submission token, no per-submitter API key).

Usage:
  ./scripts/submit.py \\
      --submission examples/solo/demos/baseline \\
      --problems   examples/problems/sample_20.json \\
      [--problem-ids s1,s3] \\
      [--config pipeline/config.json] \\
      [--output pipeline/results/demo.json] \\
      [--verbose]

Exits 0 iff every selected problem is solved.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.proxy import load_config, load_problems, run_solver


def _style(s: str, code: str, stream: Any = None) -> str:
    """Wrap ``s`` in an ANSI sequence iff ``stream`` is an attached TTY.

    The decision is made against the target stream (stdout vs stderr),
    so stderr messages still get ANSI when stderr is a TTY but stdout is a
    pipe, and vice versa. Mixing the two with a single module-level flag
    produces the wrong output in mixed-redirect pipelines.
    """
    target = stream if stream is not None else sys.stdout
    isatty = getattr(target, "isatty", lambda: False)
    if not isatty():
        return s
    return f"\033[{code}m{s}\033[0m"


def GREEN(s: str, stream: Any = None) -> str:  return _style(s, "32", stream)
def RED(s: str, stream: Any = None) -> str:    return _style(s, "31", stream)
def YELLOW(s: str, stream: Any = None) -> str: return _style(s, "33", stream)
def CYAN(s: str, stream: Any = None) -> str:   return _style(s, "36", stream)
def DIM(s: str, stream: Any = None) -> str:    return _style(s, "2", stream)
def BOLD(s: str, stream: Any = None) -> str:   return _style(s, "1", stream)


def _atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically: tmp file in the same dir, fsync, rename.

    The same-directory constraint is required so ``os.replace`` stays on one
    filesystem (atomic). On Python + POSIX, ``os.replace`` is atomic across
    existing targets. On an error mid-write the partial tmp file is removed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def _fmt_bytes(n: int | None) -> str:
    if n is None:
        return "-"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1048576:.2f} MB"


def _truncate(text: str, cap: int = 80) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= cap else text[: cap - 1] + "…"


def _print_status_line(i: int, total: int, pid: str, eq1: str, eq2: str) -> None:
    if not sys.stdout.isatty():
        return
    line = f"{DIM(f'[{i}/{total}]')} {BOLD(pid)} {DIM(eq1 + ' -> ' + eq2)}  ..."
    sys.stdout.write("\r\033[K" + line)
    sys.stdout.flush()


def _clear_status_line() -> None:
    if sys.stdout.isatty():
        sys.stdout.write("\r\033[K")


def _print_problem_row(
    i: int,
    total: int,
    pid: str,
    eq1: str,
    eq2: str,
    result: dict[str, Any],
    elapsed: float,
    verbose: bool,
) -> None:
    _clear_status_line()
    solved = bool(result.get("solved"))
    verdict = result.get("verdict") or "?"
    jc = result.get("judge_calls", 0)
    lc = result.get("llm_calls", 0)

    if solved:
        mark = GREEN(BOLD("[OK  ]"))
    else:
        mark = RED(BOLD("[FAIL]"))

    details = [
        f"verdict={verdict}",
        f"t={elapsed:.2f}s",
        f"j={jc} l={lc}",
    ]
    print(
        f"  {mark}  {DIM(f'[{i}/{total}]')} "
        f"{BOLD(pid):<18} {DIM(eq1 + ' -> ' + eq2)}  "
        f"{DIM(' · '.join(details))}"
    )

    log = result.get("log") or []
    if verbose or not solved:
        _render_debug_log(log)


def _render_debug_log(log: list[dict[str, Any]]) -> None:
    """Render the per-problem debug log with kind-tagged rows.

    Consumes the raw ``log`` returned by ``run_solver``: entries of type
    ``judge``, ``llm``, ``error``, ``timeout``, ``unknown``.
    """
    for e in log:
        t = e.get("elapsed")
        tstr = f"{t:6.2f}s" if isinstance(t, (int, float)) else "   —  "
        kind = e.get("type")
        if kind == "judge":
            req = e.get("request") or {}
            resp = e.get("response") or {}
            v = req.get("verdict", "?")
            code_len = len(req.get("code", "") or "")
            st = resp.get("status", "?")
            ec = resp.get("error_code", "-")
            head = _truncate((req.get("code") or "").lstrip().split("\n", 1)[0], 60)
            print(f"    {DIM(tstr)} {BOLD('judge ')} v={v} code[{code_len}B] "
                  f"status={st} error={ec}")
            if head:
                print(f"    {DIM(' ' * len(tstr))} {DIM(head)}")
        elif kind == "llm":
            req = e.get("request") or {}
            resp = e.get("response") or {}
            ctx = req.get("solver_context")
            ctx_s = _truncate(str(ctx), 60) if ctx else "-"
            err = resp.get("error")
            content = resp.get("response")
            content_len = len(content) if isinstance(content, str) else 0
            if err:
                print(f"    {DIM(tstr)} {BOLD('llm   ')} ctx={ctx_s}  "
                      f"{RED('error=' + str(err))}")
            else:
                print(f"    {DIM(tstr)} {BOLD('llm   ')} ctx={ctx_s}  "
                      f"content={content_len}B")
        elif kind == "error":
            print(f"    {DIM(tstr)} {RED('error ')} {e.get('message','')}")
        elif kind == "timeout":
            print(f"    {DIM(tstr)} {YELLOW('timeout')} {e.get('message','')}")
        else:
            print(f"    {DIM(tstr)} {DIM('event ')} {kind}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--submission", required=True, help="Path to submission directory")
    ap.add_argument("--problems", required=True,
                    help="Path to problems file (JSON array or JSONL, auto-detected)")
    ap.add_argument("--problem-ids", help="Comma-separated subset of problem IDs")
    ap.add_argument("--config", default=None, help="Path to config.json (default: pipeline/config.json)")
    ap.add_argument("--output", default=None, help="Write results JSON to this path")
    ap.add_argument("--verbose", action="store_true",
                    help="Print debug log for every problem (not just failures)")
    args = ap.parse_args()

    config = load_config(args.config)
    try:
        problems = load_problems(args.problems)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(RED(f"FATAL: {exc}", sys.stderr), file=sys.stderr)
        return 2
    submission_name = Path(args.submission).name

    if not problems:
        print(
            RED(f"FATAL: problem set at {args.problems} is empty", sys.stderr),
            file=sys.stderr,
        )
        return 2

    if args.problem_ids:
        wanted = {x.strip() for x in args.problem_ids.split(",") if x.strip()}
        available = {p["id"] for p in problems}
        missing = sorted(wanted - available)
        if missing:
            print(
                RED(
                    "FATAL: --problem-ids contains IDs not present in problem set: "
                    + ", ".join(missing),
                    sys.stderr,
                ),
                file=sys.stderr,
            )
            return 2
        problems = [p for p in problems if p["id"] in wanted]
        if not problems:
            print(
                RED(
                    f"FATAL: no problems matched --problem-ids={args.problem_ids}",
                    sys.stderr,
                ),
                file=sys.stderr,
            )
            return 2

    solver_cfg = config["solver"]
    llm_cfg = config["llm"]

    print(BOLD(f"Submission:  {args.submission}"))
    print(f"Problems:    {len(problems)}")
    print(f"Config:      timeout={solver_cfg['timeout_seconds']}s, "
          f"max_output_tokens={llm_cfg['max_output_tokens']}")
    print(f"LLM:         {llm_cfg['model']} "
          f"(provider: {llm_cfg.get('provider', 'default')})")
    if args.output:
        print(f"Output:      {args.output}")
    print()

    results: list[dict[str, Any]] = []
    solved_count = 0
    total_time = 0.0

    for i, problem in enumerate(problems, 1):
        pid = problem["id"]
        eq1 = f"Equation{problem['eq1_id']}"
        eq2 = f"Equation{problem['eq2_id']}"

        _print_status_line(i, len(problems), pid, eq1, eq2)

        t0 = time.time()
        result = run_solver(args.submission, problem, config)
        elapsed = time.time() - t0
        total_time += elapsed

        entry = {
            "id": pid,
            "eq1_id": problem["eq1_id"],
            "eq2_id": problem["eq2_id"],
            "elapsed_seconds": round(elapsed, 2),
            **result,
        }
        results.append(entry)

        if result.get("solved"):
            solved_count += 1

        _print_problem_row(
            i, len(problems), pid, eq1, eq2, result, elapsed, args.verbose,
        )

        if args.output:
            _atomic_write_text(
                Path(args.output),
                json.dumps(results, indent=2, ensure_ascii=False),
            )

    _clear_status_line()
    total = len(problems)
    print()
    colour = GREEN if solved_count == total else (YELLOW if solved_count > 0 else RED)
    print(colour(BOLD(
        f"Final: {solved_count} / {total} solved  "
        f"({total_time:.1f}s, submission={submission_name})"
    )))
    if args.output:
        print(DIM(f"Results written to {args.output}"))

    return 0 if solved_count == total else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(RED(f"unexpected error: {exc}", sys.stderr), file=sys.stderr)
        raise SystemExit(2)
