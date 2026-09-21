#!/usr/bin/env python3
"""Check Markdown math for GitHub rendering hazards.

Usage:
    python scripts/check_markdown_math.py path/to/file.md [more.md ...]

Pass only Markdown files that are being created or modified. The checker is
intentionally path-scoped so legacy documents do not have to be reformatted
as part of unrelated work.
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

# GitHub Markdown may reject macros that ordinary MathJax supports.
# Keep this list synchronized with .agents/rules/document-formatting.md.
DISALLOWED_MATH_MACROS = ("operatorname",)
DISALLOWED_MATH_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(name) for name in DISALLOWED_MATH_MACROS) + r")\b"
)

# TeX often accepts unbraced single-token arguments (for example, \\mathbf x),
# but this repository requires explicit braces to avoid brittle GitHub rendering.
BRACED_STYLE_MACROS = ("mathbf", "mathrm", "text", "boldsymbol")
UNBRACED_STYLE_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(name) for name in BRACED_STYLE_MACROS) + r")(?!\s*\{)"
)



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
    """Remove inline-code spans before inspecting inline math."""
    previous = None
    while previous != line:
        previous = line
        line = INLINE_CODE.sub("", line)
    return line


def check_disallowed_macros(
    fragment: str, path: Path, lineno: int, context: str
) -> list[str]:
    errors: list[str] = []
    for match in DISALLOWED_MATH_MACRO.finditer(fragment):
        macro = match.group(1)
        errors.append(
            f"{path}:{lineno}: GitHub-disallowed math macro '\\{macro}' in "
            f"{context}; replace it with a GitHub-safe basic form "
            "(for example, use \\mathrm{...} for a custom operator label)"
        )
    return errors


def check_unbraced_style_macros(
    fragment: str, path: Path, lineno: int, context: str
) -> list[str]:
    errors: list[str] = []
    for match in UNBRACED_STYLE_MACRO.finditer(fragment):
        macro = match.group(1)
        errors.append(
            f"{path}:{lineno}: style macro '\\{macro}' in {context} must use "
            "an explicit braced argument (for example, \\mathbf{1} or "
            "\\boldsymbol{\\tau})"
        )
    return errors


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: cannot read file: {exc}"]

    in_display_math = False
    block_start = 0
    nonempty_content = 0
    code_fence: str | None = None

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        if code_fence is not None:
            if is_fence_close(line, code_fence):
                code_fence = None
            continue

        fence_match = FENCE_OPEN.match(line)
        if fence_match:
            code_fence = fence_match.group(1)
            info = fence_match.group(2).strip().lower()
            if info and info.split()[0] == "math":
                errors.append(
                    f"{path}:{lineno}: fenced code block with language 'math' is "
                    "not allowed by repository formatting rules; use $$ delimiters"
                )
            continue

        if stripped == "$$":
            if not in_display_math:
                in_display_math = True
                block_start = lineno
                nonempty_content = 0
            else:
                if nonempty_content == 0:
                    errors.append(
                        f"{path}:{block_start}-{lineno}: empty $$ display-math block"
                    )
                elif nonempty_content > 1:
                    errors.append(
                        f"{path}:{block_start}-{lineno}: display equation spans "
                        f"{nonempty_content} non-empty Markdown lines; keep one "
                        "display equation on one physical line and use LaTeX "
                        "alignment commands inside that line when needed"
                    )
                in_display_math = False
            continue

        if in_display_math:
            if stripped:
                nonempty_content += 1

            errors.extend(
                check_disallowed_macros(line, path, lineno, "display math")
            )
            errors.extend(
                check_unbraced_style_macros(line, path, lineno, "display math")
            )

            if SETEXT_UNDERLINE.fullmatch(line):
                errors.append(
                    f"{path}:{lineno}: standalone '{stripped}' inside $$ block can be "
                    "parsed as a Markdown Setext heading underline; keep the operator "
                    "on the same physical line as the LaTeX expression"
                )
                continue

            if MARKDOWN_STRUCTURE.match(line):
                errors.append(
                    f"{path}:{lineno}: Markdown structural syntax inside $$ block "
                    f"('{stripped}'); rewrite the display equation so this token is "
                    "not at the beginning of a physical Markdown line"
                )
            continue

        cleaned = strip_inline_code(line)

        if SAME_LINE_DISPLAY.search(cleaned):
            errors.append(
                f"{path}:{lineno}: same-line $$...$$ display math is not allowed by "
                "repository rules; put opening and closing $$ on separate lines"
            )
            continue

        for match in INLINE_MATH.finditer(cleaned):
            errors.extend(
                check_disallowed_macros(
                    match.group(1), path, lineno, "inline math"
                )
            )
            errors.extend(
                check_unbraced_style_macros(
                    match.group(1), path, lineno, "inline math"
                )
            )

    if in_display_math:
        errors.append(f"{path}:{block_start}: unclosed $$ display-math block")

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
