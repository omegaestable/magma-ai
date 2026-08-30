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

Since 2026-08-28 the four big data tables (`PACKED_TABLES`) are additionally
packed: each literal is serialised to JSON, zlib-compressed and base85-encoded,
and the artifact rebuilds it at import time through a 6-line helper. The
certificate library alone goes from ~100 KB to ~15 KB with every judge-pinned
byte intact. The source keeps the readable literals; only the artifact carries
the blobs, which the submission note discloses (rules/evaluation.md,
"Submission Note": compressed data must be described, and it is). The packed
value is decoded again here and compared to the source literal with `==`
before anything is written, so a blob that does not round-trip exactly —
tuple-vs-list included — aborts the packaging run.

    python minify_submission.py <source> <destination>
"""

from __future__ import annotations

import ast
import base64
import io
import json
import lzma
import sys
import tokenize
from pathlib import Path

DOCSTRING_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# Top-level literals packed in the artifact, with the shape each one is
# rebuilt to. "certs": dict[(str, str)] -> (str, str, str); "tables":
# tuple[(str, list[list[int]]), ...]. Anything else raises rather than packs.
PACKED_TABLES = {
    "DISTILLED_CERTS": "certs",
    "FP_WITNESS_TABLES": "tables",
    "O5_WITNESS_TABLES": "tables",
    "WITNESS_TABLES": "tables",
    # "lit": any top-level literal, carried as its `repr` and rebuilt with
    # `ast.literal_eval`, so tuple/list/str types survive exactly. Added
    # 2026-08-29: these twelve were the largest data literals the packer was
    # still shipping verbatim (30,516 B of source between them).
    "_ANCHORED_RIGHT_PROJECTION_BLOCKS": "lit",
    "_ANCHORED_LEFT_PROJECTION_BLOCKS": "lit",
    "_PRODUCT_CONSTANT_BLOCKS_3565": "lit",
    "_PRODUCT_CONSTANT_BLOCKS_3967": "lit",
    "PROTOCOL_FALSE_FIRST": "lit",
    "_PRODUCT_CONSTANT_BLOCKS_3983": "lit",
    "_PRODUCT_CONSTANT_BLOCKS_3577": "lit",
    "_RIGHT_SPINE_CROSSED_BLOCKS": "lit",
    "MINED_LEMMA_LIBRARY_TEXT": "lit",
    "PROTOCOL_DERIVATION_EXCLUSION": "lit",
    "PROTOCOL_TERMS": "lit",
}
# `PROMPT` is deliberately NOT here, though it is 3,338 B and would pack to 2,210.
# `pipeline/proxy.py:_extract_prompt_from_solver` reads it out of the artifact by
# AST and accepts ONLY a top-level `PROMPT = <str constant>`; packing it makes the
# extractor return "" and the Solo LLM lane runs on an empty prompt with no error
# anywhere. `test_artifact.py` pins both halves of that.
UNPACK_HELPER = "_unpack_all"
PACKED_DICT = "_PACKED"
# The helper shipped in the artifact. Local imports keep the solver's own import
# block untouched; `lzma`, `base64` and `json` are all stdlib in
# python:3.11-slim.
# lzma rather than zlib since 2026-08-29: the certificate table is ~600 KB of Lean
# whose entries share a long common preamble, and zlib's 32 KB window cannot see
# across two 19 KB certificates. Measured on the 46-entry table: zlib level 9 +
# base85 = 112,379 B; lzma preset 9|EXTREME + base85 = 50,155 B.
UNPACK_SOURCE = """\
def _unpack_all(blob):
    import ast, base64, json, lzma
    out = {}
    for name, kind, data in json.loads(lzma.decompress(base64.b85decode(blob)).decode("utf-8")):
        if kind == "certs":
            out[name] = {(a, b): (c, d, e) for a, b, c, d, e in data}
        elif kind == "tables":
            out[name] = tuple((n, t) for n, t in data)
        else:
            out[name] = ast.literal_eval(data)
    return out
"""


def _comment_spans(source: str) -> dict[int, list[tuple[int, int]]]:
    spans: dict[int, list[tuple[int, int]]] = {}
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type == tokenize.COMMENT:
            spans.setdefault(token.start[0], []).append((token.start[1], token.end[1]))
    return spans


def _string_interior_lines(source: str) -> set[int]:
    """Lines whose content belongs to a multi-line string literal.

    Both line transforms in `minify` edit string *content* when a literal spans
    lines: collapsing a run of blank lines rewrites the text, and `rstrip`
    deletes significant trailing spaces. `DISTILLED_CERTS` stores every
    judge-accepted certificate as triple-quoted Lean and is the highest-churn
    data in the solver, so a certificate carrying a trailing space or a
    three-blank-line gap would fail `check()` and abort the packaging run.

    The first line is excluded: it holds the assignment and the opening quotes,
    so a comment can never follow the literal there but code can precede it.
    """
    lines: set[int] = set()
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type != tokenize.STRING or token.end[0] == token.start[0]:
            continue
        lines.update(range(token.start[0] + 1, token.end[0] + 1))
    return lines


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
    literal = _string_interior_lines(source)
    out: list[str] = []
    blank_run = 0
    for number, line in enumerate(source.splitlines(), start=1):
        if number in drop:
            continue
        if number in literal:
            # Inside a multi-line literal: emit verbatim. No comment can start
            # here, blank lines are content, and trailing spaces are content.
            blank_run = 0
            out.append(line)
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


def _assigned_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    if (isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)):
        return node.targets[0].id
    return None


def _flatten_table(name: str, value: object) -> object:
    """The JSON-safe form of one table, per its `PACKED_TABLES` kind."""
    kind = PACKED_TABLES[name]
    if kind == "certs":
        if not (isinstance(value, dict) and all(
                isinstance(k, tuple) and len(k) == 2 and isinstance(v, tuple)
                and len(v) == 3 for k, v in value.items())):
            raise SystemExit(f"{name}: expected dict[(str, str)] -> (str, str, str)")
        return [[*k, *v] for k, v in value.items()]
    if kind == "tables":
        if not (isinstance(value, tuple) and all(
                isinstance(entry, tuple) and len(entry) == 2
                and isinstance(entry[1], list) for entry in value)):
            raise SystemExit(f"{name}: expected tuple[(str, list), ...]")
        return [[entry_name, table] for entry_name, table in value]
    # "lit": carry the repr, which `ast.literal_eval` rebuilds with exact types.
    text = repr(value)
    rebuilt = ast.literal_eval(text)
    if rebuilt != value or type(rebuilt) is not type(value):
        raise SystemExit(f"{name}: literal does not round-trip through repr")
    return text


def _encode_all(values: dict[str, object], order: list[str]) -> str:
    """One blob for every packed table.

    A separate lzma stream per table restarts the dictionary each time, which
    costs real bytes when the tables share vocabulary (Lean preambles, block
    text, prompt prose). Measured 2026-08-29 over the sixteen tables: 77,635 B
    as separate blobs against 72,920 B shared, and 97,166 B for the state this
    replaced (four blobs plus twelve verbatim literals) -- 24,246 B saved.
    """
    flat = [[name, PACKED_TABLES[name], _flatten_table(name, values[name])] for name in order]
    payload = json.dumps(flat, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    blob = base64.b85encode(lzma.compress(payload, preset=9 | lzma.PRESET_EXTREME)).decode("ascii")
    return f'{PACKED_DICT} = {UNPACK_HELPER}("{blob}")'


def pack_tables(minified: str) -> tuple[str, dict[str, object]]:
    """Replace each `PACKED_TABLES` literal with a lookup into one packed blob.

    Runs on the minified text (its line numbers are the ones edited) and
    returns the packed text plus the literal values, which `check` compares
    against what the packed lines decode to.
    """
    tree = ast.parse(minified)
    lines = minified.splitlines()
    targets: list[tuple[int, int, str, object]] = []
    for node in tree.body:
        name = _assigned_name(node)
        if name in PACKED_TABLES:
            value = node.value
            if value is None:
                raise SystemExit(f"{name} has no value to pack")
            targets.append((node.lineno, node.end_lineno, name, ast.literal_eval(value)))
    missing = set(PACKED_TABLES) - {name for _, _, name, _ in targets}
    if missing:
        raise SystemExit(f"packed tables not found at top level: {sorted(missing)}")
    seen = [name for _, _, name, _ in targets]
    if len(set(seen)) != len(seen):
        raise SystemExit(f"packed table assigned more than once: {sorted(set(seen))}")
    values = {name: value for _, _, name, value in targets}
    order = [name for _, _, name, _ in sorted(targets)]
    # Bottom-up so earlier line numbers stay valid; the helper and the shared
    # blob go in front of the first packed assignment, which is the earliest use.
    for lineno, end_lineno, name, _ in sorted(targets, reverse=True):
        lines[lineno - 1:end_lineno] = [f'{name} = {PACKED_DICT}["{name}"]']
    first = min(lineno for lineno, _, _, _ in targets)
    lines[first - 1:first - 1] = (
        UNPACK_SOURCE.splitlines() + ["", _encode_all(values, order), ""])
    return "\n".join(lines) + "\n", values


def _decode_packed(packed: str) -> dict[str, object]:
    """Run only the helper and the packed assignments, in a bare namespace."""
    tree = ast.parse(packed)
    namespace: dict[str, object] = {}
    for node in tree.body:
        is_helper = isinstance(node, ast.FunctionDef) and node.name == UNPACK_HELPER
        name = _assigned_name(node)
        if is_helper or name == PACKED_DICT or name in PACKED_TABLES:
            exec(compile(ast.Module(body=[node], type_ignores=[]), "<packed>", "exec"),
                 namespace)
    return {name: namespace[name] for name in PACKED_TABLES}


def _drop_packed(tree: ast.Module) -> ast.Module:
    tree.body = [
        node for node in tree.body
        if _assigned_name(node) not in PACKED_TABLES
        and _assigned_name(node) != PACKED_DICT
        and not (isinstance(node, ast.FunctionDef) and node.name == UNPACK_HELPER)]
    return tree


def check(source: str, minified: str, packed_values: dict[str, object] | None = None) -> None:
    """Fail unless the two files parse to the same tree modulo docstrings —
    and, when tables were packed, unless every packed value decodes to exactly
    the source literal."""
    want_tree = _without_docstrings(ast.parse(source))
    got_tree = _without_docstrings(ast.parse(minified))
    if packed_values is not None:
        decoded = _decode_packed(minified)
        for name, want in packed_values.items():
            if decoded[name] != want or type(decoded[name]) is not type(want):
                raise SystemExit(f"packed table {name} does not round-trip to the source literal")
        _drop_packed(want_tree)
        _drop_packed(got_tree)
    if ast.dump(want_tree) == ast.dump(got_tree):
        return
    # Name the first statement that differs. A bare "does not match" costs a
    # debugging session on a deadline day, and this runs inside the packager,
    # where the operator sees only the exception text.
    for index, (a, b) in enumerate(zip(want_tree.body, got_tree.body)):
        if ast.dump(a) != ast.dump(b):
            raise SystemExit(
                "minified submission does not match the source parse tree; first "
                f"difference at top-level statement {index + 1}, source line {a.lineno}")
    raise SystemExit(
        "minified submission does not match the source parse tree; top-level "
        f"statement count differs ({len(want_tree.body)} vs {len(got_tree.body)})")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit(f"usage: {argv[0]} <source> <destination>")
    source_path, destination = Path(argv[1]), Path(argv[2])
    source = source_path.read_text(encoding="utf-8")
    minified = minify(source)
    check(source, minified)
    stripped = len(minified.encode("utf-8"))
    minified, packed_values = pack_tables(minified)
    check(source, minified, packed_values)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(minified.encode("utf-8"))
    before, after = len(source.replace("\r\n", "\n").encode("utf-8")), len(minified.encode("utf-8"))
    print(f"{destination}: {before} -> {stripped} bytes stripped -> {after} bytes packed "
          f"({before - after} saved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
