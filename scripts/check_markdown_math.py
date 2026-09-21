#!/usr/bin/env python3
"""Check Markdown math for GitHub rendering hazards.

Usage:
    python scripts/check_markdown_math.py path/to/file.md [more.md ...]

The checker distinguishes GitHub's two block-math syntaxes:

- fenced ```math blocks: preferred for non-trivial display equations because
  their contents are not first interpreted as ordinary Markdown text.
- $$ blocks: allowed only for simple, single-physical-line equations that do
  not contain backslash-escaped ASCII punctuation vulnerable to GFM unescaping.

Inline $...$ math is also checked for the same GFM escape hazards.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


SETEXT_UNDERLINE = re.compile(r"^\s*(?:=+|-+)\s*$")
MARKDOWN_STRUCTURE = re.compile(
    r"^\s{0,3}(?:#{1,6}(?:\s|$)|>\s?|(?:[*+-]|\d+[.)])\s+)"
)
FENCE_OPEN = re.compile(r"^\s{0,3}((?:\x60){3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(\x60+)(.*?)\1")
INLINE_MATH = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$")
SAME_LINE_DISPLAY = re.compile(r"(?<!\\)\$\$.+?\$\$")
HTML_ENTITY_IN_MATH = re.compile(
    r"&(?:lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);"
)

# GitHub may reject macros that ordinary MathJax supports.
# Keep synchronized with .agents/rules/document-formatting.md.
DISALLOWED_MATH_MACROS = ("operatorname",)
DISALLOWED_MATH_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(name) for name in DISALLOWED_MATH_MACROS) + r")\b"
)

# TeX accepts some unbraced single-token arguments, but explicit braces make
# repository math less ambiguous and easier to lint.
BRACED_STYLE_MACROS = ("mathbf", "mathrm", "text", "boldsymbol")
UNBRACED_STYLE_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(name) for name in BRACED_STYLE_MACROS) + r")(?!\s*\{)"
)

# In ordinary GFM text, a backslash before ASCII punctuation can be consumed by
# Markdown before MathJax sees it.  This is the root cause of patterns such as
# \left\{ becoming \left{ and of \\ row separators being damaged inside $$.
# GitHub explicitly documents \$ inside math, so '$' is intentionally excluded.
GFM_RISKY_ESCAPE = re.compile(
    r"""\\([!"#%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])"""
)

ENV_TOKEN = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LEFT_TOKEN = re.compile(r"\\left\b")
RIGHT_TOKEN = re.compile(r"\\right\b")


def iter_markdown_paths(args: list[str]) -> list[Path]:
    paths: list[Path] = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() == ".md":
            paths.append(path)
    return paths


def is_fence_close(line: str, fence: str) -> bool:
    marker = re.escape(fence[0])
    min_len = len(fence)
    return bool(re.fullmatch(rf"\s{{0,3}}{marker}{{{min_len},}}\s*", line))


def strip_inline_code(line: str) -> str:
    previous = None
    while previous != line:
        previous = line
        line = INLINE_CODE.sub("", line)
    return line


def check_common_math(
    fragment: str,
    path: Path,
    lineno: int,
    context: str,
    *,
    gfm_preprocessed: bool,
) -> list[str]:
    errors: list[str] = []

    for match in DISALLOWED_MATH_MACRO.finditer(fragment):
        macro = match.group(1)
        errors.append(
            f"{path}:{lineno}: GitHub-disallowed math macro '\\{macro}' in "
            f"{context}; use a GitHub-safe basic form such as \\mathrm{{...}}"
        )

    for match in UNBRACED_STYLE_MACRO.finditer(fragment):
        macro = match.group(1)
        errors.append(
            f"{path}:{lineno}: style macro '\\{macro}' in {context} must use "
            "an explicit braced argument, e.g. \\mathbf{1}"
        )

    if HTML_ENTITY_IN_MATH.search(fragment):
        errors.append(
            f"{path}:{lineno}: HTML entity found inside {context}; use the "
            "actual mathematical character/operator rather than &lt;/&gt;/etc."
        )

    if gfm_preprocessed:
        for match in GFM_RISKY_ESCAPE.finditer(fragment):
            token = match.group(0)
            errors.append(
                f"{path}:{lineno}: GFM-sensitive escape '{token}' inside "
                f"{context}. Markdown can consume this escape before MathJax. "
                "For display math, use a fenced ```math block; for inline "
                "math, use named macros such as \\lbrace/\\rbrace or "
                "\\lVert/\\rVert and avoid escaped spacing punctuation."
            )

    return errors


def check_math_structure(
    fragment: str, path: Path, lineno: int, context: str
) -> list[str]:
    errors: list[str] = []

    # Count grouping braces that are not escaped literal braces.
    depth = 0
    for match in re.finditer(r"(?<!\\)[{}]", fragment):
        if match.group(0) == "{":
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                errors.append(
                    f"{path}:{lineno}: unmatched closing brace in {context}"
                )
                depth = 0
    if depth:
        errors.append(
            f"{path}:{lineno}: unbalanced grouping braces in {context}"
        )

    left_count = len(LEFT_TOKEN.findall(fragment))
    right_count = len(RIGHT_TOKEN.findall(fragment))
    if left_count != right_count:
        errors.append(
            f"{path}:{lineno}: unbalanced \\left/\\right delimiters in {context} "
            f"({left_count} left vs {right_count} right)"
        )

    env_stack: list[str] = []
    for match in ENV_TOKEN.finditer(fragment):
        kind, name = match.groups()
        if kind == "begin":
            env_stack.append(name)
        elif not env_stack or env_stack[-1] != name:
            errors.append(
                f"{path}:{lineno}: unmatched \\end{{{name}}} in {context}"
            )
        else:
            env_stack.pop()
    for name in reversed(env_stack):
        errors.append(
            f"{path}:{lineno}: missing \\end{{{name}}} in {context}"
        )

    return errors


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: cannot read file: {exc}"]

    in_display_math = False
    display_start = 0
    display_lines: list[str] = []

    code_fence: str | None = None
    math_fence = False
    math_fence_start = 0
    math_fence_lines: list[str] = []

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        if code_fence is not None:
            if is_fence_close(line, code_fence):
                if math_fence:
                    fragment = "\n".join(math_fence_lines)
                    errors.extend(
                        check_common_math(
                            fragment,
                            path,
                            math_fence_start,
                            "fenced math",
                            gfm_preprocessed=False,
                        )
                    )
                    errors.extend(
                        check_math_structure(
                            fragment, path, math_fence_start, "fenced math"
                        )
                    )
                code_fence = None
                math_fence = False
                math_fence_lines = []
            elif math_fence:
                math_fence_lines.append(line)
            continue

        fence_match = FENCE_OPEN.match(line)
        if fence_match:
            code_fence = fence_match.group(1)
            info = fence_match.group(2).strip().lower()
            math_fence = bool(info and info.split()[0] == "math")
            if math_fence:
                math_fence_start = lineno
                math_fence_lines = []
            continue

        if stripped == "$$":
            if not in_display_math:
                in_display_math = True
                display_start = lineno
                display_lines = []
            else:
                nonempty = [x for x in display_lines if x.strip()]
                if not nonempty:
                    errors.append(
                        f"{path}:{display_start}-{lineno}: empty $$ display block"
                    )
                if len(nonempty) > 1:
                    errors.append(
                        f"{path}:{display_start}-{lineno}: $$ equation spans "
                        f"{len(nonempty)} non-empty Markdown lines. Prefer a "
                        "fenced ```math block for non-trivial display math."
                    )
                fragment = "\n".join(display_lines)
                errors.extend(
                    check_common_math(
                        fragment,
                        path,
                        display_start,
                        "$$ display math",
                        gfm_preprocessed=True,
                    )
                )
                errors.extend(
                    check_math_structure(
                        fragment, path, display_start, "$$ display math"
                    )
                )
                in_display_math = False
                display_lines = []
            continue

        if in_display_math:
            display_lines.append(line)
            if SETEXT_UNDERLINE.fullmatch(line):
                errors.append(
                    f"{path}:{lineno}: standalone '{stripped}' inside $$ block can "
                    "be parsed as a Markdown Setext heading underline"
                )
            if MARKDOWN_STRUCTURE.match(line):
                errors.append(
                    f"{path}:{lineno}: Markdown structural syntax inside $$ block "
                    f"('{stripped}')"
                )
            continue

        cleaned = strip_inline_code(line)

        if SAME_LINE_DISPLAY.search(cleaned):
            errors.append(
                f"{path}:{lineno}: same-line $$...$$ display math is not allowed; "
                "use a fenced ```math block or repository-style block delimiters"
            )
            continue

        for match in INLINE_MATH.finditer(cleaned):
            fragment = match.group(1)
            errors.extend(
                check_common_math(
                    fragment,
                    path,
                    lineno,
                    "inline math",
                    gfm_preprocessed=True,
                )
            )
            errors.extend(
                check_math_structure(
                    fragment, path, lineno, "inline math"
                )
            )

    if in_display_math:
        errors.append(
            f"{path}:{display_start}: unclosed $$ display-math block"
        )
    if code_fence is not None:
        kind = "math fence" if math_fence else "code fence"
        errors.append(f"{path}:{math_fence_start or 1}: unclosed {kind}")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: python scripts/check_markdown_math.py "
            "<changed-file.md> [more.md ...]",
            file=sys.stderr,
        )
        return 2

    paths = iter_markdown_paths(sys.argv[1:])
    if not paths:
        print("no Markdown files to check", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in paths:
        errors.extend(check_file(path))

    if errors:
        print("Markdown math check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Markdown math check passed: {len(paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
