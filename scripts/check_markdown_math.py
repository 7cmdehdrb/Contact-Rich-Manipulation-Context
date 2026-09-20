#!/usr/bin/env python3
"""Check Markdown display-math blocks for GitHub rendering hazards.

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


def iter_markdown_paths(args: list[str]) -> list[Path]:
    paths: list[Path] = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() == ".md":
            paths.append(path)
    return paths


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: cannot read file: {exc}"]

    in_display_math = False
    block_start = 0
    nonempty_content = 0

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

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
                in_display_math = False
            continue

        if not in_display_math:
            continue

        if stripped:
            nonempty_content += 1

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

    if in_display_math:
        errors.append(
            f"{path}:{block_start}: unclosed $$ display-math block"
        )

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
