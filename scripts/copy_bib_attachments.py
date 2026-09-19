#!/usr/bin/env python3
"""Copy attachments referenced by BibTeX ``file`` fields.

This script is intended for BibTeX/BibLaTeX exports from tools such as Zotero.
It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FILE_FIELD_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])file\s*=\s*")
MIME_SUFFIX_RE = re.compile(r":[a-z][a-z0-9.+-]*/[^:;]+$", re.IGNORECASE)
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass
class CopySummary:
    copied: int = 0
    skipped: int = 0
    missing: int = 0
    failed: int = 0


def _read_field_value(text: str, start: int) -> tuple[str, int]:
    """Return one BibTeX field value and the position following it."""
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text):
        return "", start

    opener = text[start]
    if opener == "{":
        depth = 1
        index = start + 1
        value_start = index
        while index < len(text):
            character = text[index]
            if character == "\\":
                index += 2
                continue
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return text[value_start:index], index + 1
            index += 1
        raise ValueError("닫히지 않은 중괄호가 file 필드에 있습니다.")

    if opener == '"':
        index = start + 1
        value_start = index
        while index < len(text):
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == '"':
                return text[value_start:index], index + 1
            index += 1
        raise ValueError("닫히지 않은 따옴표가 file 필드에 있습니다.")

    end = start
    while end < len(text) and text[end] not in ",\r\n":
        end += 1
    return text[start:end].strip(), end


def _split_unescaped_semicolons(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    index = 0
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value):
            current.extend(value[index : index + 2])
            index += 2
            continue
        if value[index] == ";":
            parts.append("".join(current))
            current = []
        else:
            current.append(value[index])
        index += 1
    parts.append("".join(current))
    return parts


def _decode_attachment_path(raw_value: str) -> str:
    value = raw_value.strip()
    value = MIME_SUFFIX_RE.sub("", value)

    # Some exporters use ``label:C:\\path\\file.pdf:mime/type``.
    drive_match = re.search(r"[A-Za-z]:[\\/]", value)
    if drive_match and drive_match.start() > 0:
        value = value[drive_match.start() :]

    # Better BibTeX can escape Windows drive colons and backslashes.
    value = value.replace(r"\;", ";")
    value = value.replace(r"\:", ":")
    value = value.replace(r"\\", "\\")
    return value.strip()


def attachment_paths(bib_path: Path) -> list[Path]:
    """Extract de-duplicated attachment paths from one BibTeX file."""
    text = bib_path.read_text(encoding="utf-8-sig")
    paths: list[Path] = []
    seen: set[str] = set()

    for match in FILE_FIELD_RE.finditer(text):
        value, _ = _read_field_value(text, match.end())
        for raw_path in _split_unescaped_semicolons(value):
            decoded = _decode_attachment_path(raw_path)
            if not decoded:
                continue
            path = Path(decoded)
            if not path.is_absolute() and not WINDOWS_DRIVE_RE.match(decoded):
                path = bib_path.parent / path
            key = str(path).casefold()
            if key not in seen:
                seen.add(key)
                paths.append(path)
    return paths


def _renamed_destination(destination: Path, reserved: set[str]) -> Path:
    candidate = destination
    number = 2
    while candidate.exists() or str(candidate).casefold() in reserved:
        candidate = destination.with_name(
            f"{destination.stem} ({number}){destination.suffix}"
        )
        number += 1
    return candidate


def copy_attachments(
    bib_files: Iterable[Path],
    destination_dir: Path,
    conflict: str,
    dry_run: bool,
) -> CopySummary:
    summary = CopySummary()
    reserved: set[str] = set()

    if not dry_run:
        destination_dir.mkdir(parents=True, exist_ok=True)

    for bib_file in bib_files:
        try:
            sources = attachment_paths(bib_file)
        except (OSError, UnicodeError, ValueError) as error:
            print(f"[오류] {bib_file}: {error}", file=sys.stderr)
            summary.failed += 1
            continue

        for source in sources:
            try:
                source_is_file = source.is_file()
            except OSError as error:
                print(f"[오류] 원본에 접근할 수 없습니다: {source} ({error})", file=sys.stderr)
                summary.failed += 1
                continue
            if not source_is_file:
                print(f"[누락] {source}", file=sys.stderr)
                summary.missing += 1
                continue

            destination = destination_dir / source.name
            destination_key = str(destination).casefold()
            has_conflict = destination.exists() or destination_key in reserved

            if has_conflict:
                if conflict == "skip":
                    print(f"[건너뜀] {source} -> {destination} (동일 이름 존재)")
                    summary.skipped += 1
                    continue
                if conflict == "error":
                    print(
                        f"[오류] 대상 파일이 이미 존재합니다: {destination}",
                        file=sys.stderr,
                    )
                    summary.failed += 1
                    continue
                if conflict == "rename":
                    destination = _renamed_destination(destination, reserved)

            action = "복사 예정" if dry_run else "복사"
            print(f"[{action}] {source} -> {destination}")
            reserved.add(str(destination).casefold())
            if dry_run:
                summary.copied += 1
                continue

            try:
                shutil.copy2(source, destination)
                summary.copied += 1
            except shutil.SameFileError:
                print(f"[건너뜀] 원본과 대상이 같습니다: {source}")
                summary.skipped += 1
            except OSError as error:
                print(f"[오류] {source}: {error}", file=sys.stderr)
                summary.failed += 1

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BibTeX file 필드가 가리키는 첨부파일을 지정 폴더로 복사합니다."
    )
    parser.add_argument("bib_files", nargs="+", type=Path, help="입력 .bib 파일")
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        type=Path,
        help="첨부파일을 복사할 폴더",
    )
    parser.add_argument(
        "--conflict",
        choices=("rename", "overwrite", "skip", "error"),
        default="rename",
        help="같은 이름이 있을 때의 처리 방식 (기본값: rename)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="실제 복사 없이 수행 내용을 출력"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = copy_attachments(
        bib_files=args.bib_files,
        destination_dir=args.destination,
        conflict=args.conflict,
        dry_run=args.dry_run,
    )
    print(
        "완료: "
        f"복사 {summary.copied}, 건너뜀 {summary.skipped}, "
        f"누락 {summary.missing}, 오류 {summary.failed}"
    )
    return 1 if summary.missing or summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
