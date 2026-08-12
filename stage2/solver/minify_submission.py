"""Write the submission artifact with comments and docstrings stripped.

The 500 KB cap is on file bytes, and comments plus docstrings are ~17% of the
solver. They are worth keeping in the working tree — most of them record a
measurement that cost a session to obtain — and worth nothing to the judge, so
they are removed here rather than at the source.

The strip is line-based and never reformats code: comment spans are located with
`tokenize` (so a `#` inside a Lean string is safe), docstring statements are
located with `ast`. Before writing, the result is proved equivalent to the source
by comparing parse trees with docstrings dropped from both — a stronger check
than eyeballing the diff, and the reason this is safe to run unattended.

    python minify_submission.py <source> <destination>
"""

from __future__ import annotations

import ast
import io
import sys
import tokenize
from pathlib import Path

DOCSTRING_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _comment_spans(source: str) -> dict[int, list[tuple[int, int]]]:
    spans: dict[int, list[tuple[int, int]]] = {}
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type == tokenize.COMMENT:
            spans.setdefault(token.start[0], []).append((token.start[1], token.end[1]))
    return spans


def _docstring_lines(tree: ast.AST) -> set[int]:
    """Lines holding a docstring that can go without emptying its block."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, DOCSTRING_OWNERS) or not node.body:
            continue
        first = node.body[0]
        if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            continue
        if len(node.body) == 1 and not isinstance(node, ast.Module):
            continue  # removing it would leave an empty block
        lines.update(range(first.lineno, first.end_lineno + 1))
    return lines


def minify(source: str) -> str:
    comments = _comment_spans(source)
    drop = _docstring_lines(ast.parse(source))
    out: list[str] = []
    blank_run = 0
    for number, line in enumerate(source.splitlines(), start=1):
        if number in drop:
            continue
        for start, end in reversed(comments.get(number, [])):
            line = line[:start] + line[end:]
        if not line.strip():
            if comments.get(number) or number - 1 in drop:
                continue  # the line existed only for the comment/docstring
            blank_run += 1
            if blank_run > 2:
                continue
        else:
            blank_run = 0
        out.append(line.rstrip())
    return "\n".join(out) + "\n"


def _without_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if not isinstance(node, DOCSTRING_OWNERS) or not node.body:
            continue
        first = node.body[0]
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
                and (len(node.body) > 1 or isinstance(node, ast.Module))):
            node.body = node.body[1:]
    return tree


def check(source: str, minified: str) -> None:
    """Fail unless the two files parse to the same tree modulo docstrings."""
    want = ast.dump(_without_docstrings(ast.parse(source)))
    got = ast.dump(_without_docstrings(ast.parse(minified)))
    if want != got:
        raise SystemExit("minified submission does not match the source parse tree")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit(f"usage: {argv[0]} <source> <destination>")
    source_path, destination = Path(argv[1]), Path(argv[2])
    source = source_path.read_text(encoding="utf-8")
    minified = minify(source)
    check(source, minified)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(minified.encode("utf-8"))
    before, after = len(source.replace("\r\n", "\n").encode("utf-8")), len(minified.encode("utf-8"))
    print(f"{destination}: {before} -> {after} bytes ({before - after} stripped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
