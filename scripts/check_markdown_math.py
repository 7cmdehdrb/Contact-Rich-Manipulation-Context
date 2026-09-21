#!/usr/bin/env python3
"""Validate Markdown math for GitHub rendering hazards.

Usage:
    python scripts/check_markdown_math.py path/to/file.md [more.md ...]

Pass only Markdown files created or modified by the current change.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


FENCE_OPEN = re.compile(r"^\s{0,3}((?:\x60){3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(\x60+)(.*?)\1")
INLINE_MATH = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$")
SAME_LINE_DISPLAY = re.compile(r"(?<!\\)\$\$.+?\$\$")
SETEXT_UNDERLINE = re.compile(r"^\s*(?:=+|-+)\s*$")
MARKDOWN_STRUCTURE = re.compile(
    r"^\s{0,3}(?:#{1,6}(?:\s|$)|>\s?|(?:[*+-]|\d+[.)])\s+)"
)

HTML_ENTITY = re.compile(r"&(?:lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);")
DISALLOWED_MACROS = ("operatorname",)
DISALLOWED_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(x) for x in DISALLOWED_MACROS) + r")\b"
)

STYLE_MACROS = ("mathbf", "mathrm", "text", "boldsymbol")
UNBRACED_STYLE_MACRO = re.compile(
    r"\\(" + "|".join(re.escape(x) for x in STYLE_MACROS) + r")(?!\s*\{)"
)

GFM_RISKY_ESCAPE = re.compile(
    r"""\\([!"#%&'()*+,\-./:;<=>?@\[\]\\^_\x60{|}~])"""
)

ACCIDENTAL_DOUBLE_BACKSLASH = re.compile(
    r"(?<!\\)\\\\(?=[A-Za-z]{2,}|[{},;!])"
)

MALFORMED_LEFT_BRACE = re.compile(r"\\left\s*\{")
MALFORMED_RIGHT_BRACE = re.compile(r"\\right\s*\}")
INDICATOR_TRAILING_SET = re.compile(r"\\mathbf\{1\}\\\{")
LEFT_RIGHT_COMMAND = re.compile(r"\\(left|right)\b")
VALID_LEFT_RIGHT = re.compile(
    r"\\(left|right)\s*(?:\\(?:[A-Za-z]+|[{}|])|[()[\]|.])"
)
ENV_TOKEN = re.compile(r"\\(begin|end)\{([^{}]+)\}")


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
    return bool(re.fullmatch(rf"\s{{0,3}}{marker}{{{len(fence)},}}\s*", line))


def strip_inline_code(line: str) -> str:
    previous = None
    while previous != line:
        previous = line
        line = INLINE_CODE.sub("", line)
    return line


def grouping_brace_errors(fragment: str, label: str) -> list[str]:
    errors: list[str] = []
    depth = 0
    i = 0
    while i < len(fragment):
        ch = fragment[i]
        if ch == "\\" and i + 1 < len(fragment) and fragment[i + 1] in "{}":
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                errors.append(f"unmatched closing grouping brace in {label}")
                depth = 0
        i += 1
    if depth:
        errors.append(f"{depth} unclosed grouping brace(s) in {label}")
    return errors


def environment_errors(fragment: str, label: str) -> list[str]:
    errors: list[str] = []
    stack: list[str] = []
    for match in ENV_TOKEN.finditer(fragment):
        kind, name = match.groups()
        if kind == "begin":
            stack.append(name)
        elif not stack or stack[-1] != name:
            errors.append(f"unmatched \\end{{{name}}} in {label}")
        else:
            stack.pop()
    for name in reversed(stack):
        errors.append(f"missing \\end{{{name}}} in {label}")
    return errors


def check_math(
    fragment: str,
    *,
    path: Path,
    lineno: int,
    label: str,
    gfm_preprocessed: bool,
) -> list[str]:
    errors: list[str] = []

    for match in DISALLOWED_MACRO.finditer(fragment):
        errors.append(
            f"{path}:{lineno}: GitHub-disallowed macro '\\{match.group(1)}' in {label}"
        )

    for match in UNBRACED_STYLE_MACRO.finditer(fragment):
        errors.append(
            f"{path}:{lineno}: style macro '\\{match.group(1)}' in {label} "
            "must use an explicit braced argument"
        )

    if HTML_ENTITY.search(fragment):
        errors.append(
            f"{path}:{lineno}: HTML entity inside {label}; keep raw math operators "
            "in Markdown source"
        )

    if ACCIDENTAL_DOUBLE_BACKSLASH.search(fragment):
        errors.append(
            f"{path}:{lineno}: accidental doubled backslash before a command or "
            f"escaped punctuation in {label}; use one backslash for commands"
        )

    if MALFORMED_LEFT_BRACE.search(fragment):
        errors.append(
            f"{path}:{lineno}: malformed '\\left{{' in {label}; literal brace "
            "delimiters require '\\left\\{' or a safer non-scaled notation"
        )

    if MALFORMED_RIGHT_BRACE.search(fragment):
        errors.append(
            f"{path}:{lineno}: malformed '\\right}}' in {label}; literal brace "
            "delimiters require '\\right\\}' or a safer non-scaled notation"
        )

    if INDICATOR_TRAILING_SET.search(fragment):
        errors.append(
            f"{path}:{lineno}: fragile indicator form '\\mathbf{{1}}\\{{...\\}}' "
            f"in {label}; put the condition in a subscript"
        )

    lr_commands = list(LEFT_RIGHT_COMMAND.finditer(fragment))
    lr_valid = list(VALID_LEFT_RIGHT.finditer(fragment))
    if len(lr_commands) != len(lr_valid):
        errors.append(
            f"{path}:{lineno}: one or more \\left/\\right commands have an "
            f"unrecognized delimiter in {label}"
        )

    left_count = sum(1 for m in lr_commands if m.group(1) == "left")
    right_count = sum(1 for m in lr_commands if m.group(1) == "right")
    if left_count != right_count:
        errors.append(
            f"{path}:{lineno}: unbalanced \\left/\\right in {label} "
            f"({left_count} left, {right_count} right)"
        )

    for msg in grouping_brace_errors(fragment, label):
        errors.append(f"{path}:{lineno}: {msg}")
    for msg in environment_errors(fragment, label):
        errors.append(f"{path}:{lineno}: {msg}")

    if gfm_preprocessed:
        for match in GFM_RISKY_ESCAPE.finditer(fragment):
            errors.append(
                f"{path}:{lineno}: GFM-sensitive escape '{match.group(0)}' in "
                f"{label}; use a fenced math block for complex display math"
            )

    return errors


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: cannot read file: {exc}"]

    code_fence: str | None = None
    math_fence = False
    math_start = 0
    math_lines: list[str] = []

    in_dollar_display = False
    dollar_start = 0
    dollar_lines: list[str] = []

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        if code_fence is not None:
            if is_fence_close(line, code_fence):
                if math_fence:
                    fragment = "\n".join(math_lines)
                    errors.extend(
                        check_math(
                            fragment,
                            path=path,
                            lineno=math_start,
                            label="fenced math",
                            gfm_preprocessed=False,
                        )
                    )
                code_fence = None
                math_fence = False
                math_lines = []
            elif math_fence:
                math_lines.append(line)
            continue

        fence_match = FENCE_OPEN.match(line)
        if fence_match:
            code_fence = fence_match.group(1)
            info = fence_match.group(2).strip().lower()
            math_fence = bool(info and info.split()[0] == "math")
            if math_fence:
                math_start = lineno
                math_lines = []
            continue

        if stripped == "$$":
            if not in_dollar_display:
                in_dollar_display = True
                dollar_start = lineno
                dollar_lines = []
            else:
                nonempty = [x for x in dollar_lines if x.strip()]
                if not nonempty:
                    errors.append(
                        f"{path}:{dollar_start}-{lineno}: empty $$ display block"
                    )
                if len(nonempty) > 1:
                    errors.append(
                        f"{path}:{dollar_start}-{lineno}: $$ display spans multiple "
                        "physical Markdown lines; use a fenced math block"
                    )
                fragment = "\n".join(dollar_lines)
                errors.extend(
                    check_math(
                        fragment,
                        path=path,
                        lineno=dollar_start,
                        label="$$ display math",
                        gfm_preprocessed=True,
                    )
                )
                for offset, content in enumerate(dollar_lines, start=1):
                    if SETEXT_UNDERLINE.fullmatch(content) or MARKDOWN_STRUCTURE.match(content):
                        errors.append(
                            f"{path}:{dollar_start + offset}: Markdown structural "
                            "syntax inside $$ display block"
                        )
                in_dollar_display = False
                dollar_lines = []
            continue

        if in_dollar_display:
            dollar_lines.append(line)
            continue

        cleaned = strip_inline_code(line)

        if SAME_LINE_DISPLAY.search(cleaned):
            errors.append(
                f"{path}:{lineno}: same-line $$...$$ display is not allowed; "
                "use a fenced math block"
            )
            continue

        for match in INLINE_MATH.finditer(cleaned):
            errors.extend(
                check_math(
                    match.group(1),
                    path=path,
                    lineno=lineno,
                    label="inline math",
                    gfm_preprocessed=True,
                )
            )

    if code_fence is not None:
        errors.append(f"{path}: unclosed fenced code block")
    if in_dollar_display:
        errors.append(f"{path}:{dollar_start}: unclosed $$ display block")

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
