#!/usr/bin/env python3
"""Check document links, heading anchors, and review-dataset note paths.

Uses the Python standard library. Fenced/indented code and inline code are
excluded. External URLs are not fetched; links outside the repository are
counted separately and checked only with --check-external. A full repository
scan also checks CSV/XLSX analysis_file and analysis_note_path fields under
03_assets/literature/review_dataset. Explicit Markdown file selection checks
only those Markdown files. Dataset paths use each CSV/XLSX file's parent;
original PDF local_path, BibTeX attachments, and run metadata are provenance
and are excluded.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass, asdict
import html
import json
from pathlib import Path
import posixpath
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile


NOTE_FIELDS = frozenset({"analysis_file", "analysis_note_path"})
SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCUMENT_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True)
class Link:
    destination: str
    line: int
    kind: str


def escaped(text: str, index: int) -> bool:
    count = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        count += 1
        index -= 1
    return bool(count % 2)


def mask(text: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in text)


def without_code_blocks(text: str) -> str:
    output: list[str] = []
    fence = ""
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            output.append(mask(line))
            if re.fullmatch(rf"\s{{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*", line):
                fence = ""
        elif match:
            fence = match.group(1)
            output.append(mask(line))
        elif re.match(r"^(?: {4}|\t)\S", line):
            output.append(mask(line))
        else:
            output.append(line)
    return "".join(output)


def without_inline_code(text: str) -> str:
    output = list(text)
    index = 0
    while index < len(text):
        if text[index] != "`" or escaped(text, index):
            index += 1
            continue
        end = index
        while end < len(text) and text[end] == "`":
            end += 1
        marker = text[index:end]
        close = end
        while True:
            close = text.find(marker, close)
            if close == -1:
                break
            if (close == 0 or text[close - 1] != "`") and (close + len(marker) == len(text) or text[close + len(marker)] != "`"):
                output[index:close + len(marker)] = mask(text[index:close + len(marker)])
                index = close + len(marker)
                break
            close += len(marker)
        if close == -1:
            index = end
    return "".join(output)


def unescape_destination(destination: str) -> str:
    return html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", destination))


def normalize_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def bracket_end(text: str, start: int) -> int | None:
    depth = 0
    for index in range(start, len(text)):
        if escaped(text, index):
            continue
        if text[index] == "[":
            depth += 1
        elif text[index] == "]":
            depth -= 1
            if depth == 0:
                return index
    return None


def link_target(text: str, start: int, inline: bool) -> tuple[str, int] | None:
    """Read an angle/balanced bare destination, optionally followed by a title."""
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return None
    if text[index] == "<":
        begin = index + 1
        index = begin
        while index < len(text) and (text[index] != ">" or escaped(text, index)):
            if text[index] == "\n":
                return None
            index += 1
        if index == len(text):
            return None
        destination = text[begin:index]
        index += 1
    else:
        begin = index
        depth = 0
        while index < len(text):
            char = text[index]
            if escaped(text, index):
                index += 1
                continue
            if char == "\n":
                break
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace():
                rest = index
                while rest < len(text) and text[rest].isspace() and text[rest] != "\n":
                    rest += 1
                if rest == len(text) or text[rest] in "\"'(" or (inline and text[rest] == ")"):
                    break
                if not inline:
                    break
            index += 1
        if depth:
            return None
        destination = text[begin:index].strip()
    while index < len(text) and text[index].isspace():
        index += 1
    if index < len(text) and text[index] in "\"'(":
        quote = text[index]
        closing_quote = ")" if quote == "(" else quote
        index += 1
        while index < len(text) and (text[index] != closing_quote or escaped(text, index)):
            index += 1
        if index == len(text):
            return None
        index += 1
        while index < len(text) and text[index].isspace():
            index += 1
    if inline and (index >= len(text) or text[index] != ")"):
        return None
    return unescape_destination(destination), index + (1 if inline else 0)


def extract_links(text: str) -> list[Link]:
    source = without_code_blocks(text)
    visible = without_inline_code(source)
    definitions: dict[str, str] = {}
    definition_spans: list[tuple[int, int]] = []
    links: list[Link] = []
    for match in re.finditer(r"^ {0,3}\[([^\]\n]+)\]:[ \t]*", visible, re.M):
        target = link_target(visible, match.end(), inline=False)
        if target:
            destination, end = target
            definitions.setdefault(normalize_label(match.group(1)), destination)
            definition_spans.append((match.start(), end))
            links.append(Link(destination, visible[:match.start()].count("\n") + 1, "reference-definition"))
    for begin, end in definition_spans:
        visible = visible[:begin] + mask(visible[begin:end]) + visible[end:]
    reference_label_indices: set[int] = set()
    for index, char in enumerate(visible):
        if char != "[" or escaped(visible, index) or index in reference_label_indices:
            continue
        close = bracket_end(visible, index)
        if close is None:
            continue
        label = visible[index + 1:close]
        next_index = close + 1
        line = visible[:index].count("\n") + 1
        image = index > 0 and visible[index - 1] == "!" and not escaped(visible, index - 1)
        if next_index < len(visible) and visible[next_index] == "(":
            target = link_target(visible, next_index + 1, inline=True)
            if target:
                links.append(Link(target[0], line, "image" if image else "inline"))
        elif next_index < len(visible) and visible[next_index] == "[":
            ref_close = bracket_end(visible, next_index)
            if ref_close is not None:
                reference_label_indices.update(range(next_index, ref_close + 1))
                reference = visible[next_index + 1:ref_close] or label
                destination = definitions.get(normalize_label(reference))
                if destination is not None:
                    links.append(Link(destination, line, "reference-image" if image else "reference"))
        elif normalize_label(label) in definitions:
            links.append(Link(definitions[normalize_label(label)], line, "reference-image" if image else "reference"))
    for match in re.finditer(r"<(?:[A-Za-z][\w:-]*)(?:\s[^<>]*)?>", visible):
        tag = match.group()
        for attribute in re.finditer(r"\b(?:href|src)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", tag, re.I):
            destination = next(value for value in attribute.groups() if value is not None)
            links.append(Link(html.unescape(destination), visible[:match.start()].count("\n") + 1, "HTML"))
    return links


def heading_slug(heading: str) -> str:
    heading = re.sub(r"!?(\[[^\]]*\])\([^)]*\)", lambda match: match.group(1)[1:-1], heading)
    heading = html.unescape(re.sub(r"<[^>]+>", "", heading)).lower()
    # GitHub retains underscore and hyphen; formatting markers are removed.
    heading = heading.replace("`", "").replace("*", "")
    return "".join(char for char in heading if char in "_- " or unicodedata.category(char)[0] in "LNM").replace(" ", "-")


def anchors(text: str) -> set[str]:
    source = without_code_blocks(text)
    result: set[str] = set()
    used: set[str] = set()
    lines = source.splitlines()
    for index, line in enumerate(lines):
        heading = None
        match = re.match(r"^ {0,3}#{1,6}(?:\s+|$)(.*)$", line)
        if match:
            heading = re.sub(r"\s+#+\s*$", "", match.group(1)).strip()
        elif index + 1 < len(lines) and line.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", lines[index + 1]):
            heading = line.strip()
        if heading is not None:
            base = heading_slug(heading)
            slug = base
            suffix = 0
            while slug in used:
                suffix += 1
                slug = f"{base}-{suffix}"
            used.add(slug)
            result.add(slug)
    visible = without_inline_code(source)
    for tag in re.finditer(r"<[A-Za-z][^>]*>", visible):
        for match in re.finditer(r"\b(?:id|name)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", tag.group(), re.I):
            result.add(html.unescape(next(value for value in match.groups() if value is not None)))
    return result


def resolve_link(source: Path, destination: str, root: Path) -> tuple[Path, str] | None:
    if destination.startswith("//"):
        return None
    try:
        url = urlsplit(destination)
    except ValueError:
        return None
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    if path.startswith("/"):
        absolute = Path(path)
        target = absolute if absolute.is_relative_to(root) or absolute.exists() else root / path.lstrip("/")
    else:
        target = source.parent / path if path else source
    return target.resolve(), unquote(url.fragment)


def is_note_path(value: str) -> bool:
    """Select actual Markdown note references; status/provenance text is skipped."""
    value = value.strip()
    if not value or re.match(r"(?i)^(?:not applicable|not stated|duplicat(?:e|ed)|n/?a)(?:\b|$)", value):
        return False
    try:
        return urlsplit(value).path.lower().endswith(".md")
    except ValueError:
        return False


def csv_note_links(source: Path) -> list[Link]:
    links: list[Link] = []
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            for field in NOTE_FIELDS:
                value = (row.get(field) or "").strip()
                if is_note_path(value):
                    links.append(Link(value, reader.line_num, f"CSV:{field}"))
    return links


def xlsx_note_links(source: Path) -> list[Link]:
    """Read analysis columns by header, supporting shared and inline strings."""
    prefix = f"{{{SPREADSHEET_NS}}}"
    links: list[Link] = []
    with zipfile.ZipFile(source) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(item.text or "" for item in entry.iter(prefix + "t"))
                      for entry in strings.findall(prefix + "si")]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
            if relation.attrib.get("TargetMode") != "External"
        }

        def cell_text(cell: ET.Element) -> str:
            if cell.attrib.get("t") == "s":
                return shared[int(cell.findtext(prefix + "v", default="0"))]
            if cell.attrib.get("t") == "inlineStr":
                return "".join(item.text or "" for item in cell.iter(prefix + "t"))
            return cell.findtext(prefix + "v", default="")

        for sheet in workbook.findall(prefix + "sheets/" + prefix + "sheet"):
            relationship_id = sheet.attrib.get(f"{{{DOCUMENT_REL_NS}}}id")
            if relationship_id not in targets:
                continue
            target = targets[relationship_id]
            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            worksheet = ET.fromstring(archive.read(part))
            columns: dict[str, str] = {}
            for row in worksheet.findall(prefix + "sheetData/" + prefix + "row"):
                cells = []
                for cell in row.findall(prefix + "c"):
                    address = re.fullmatch(r"([A-Za-z]+)(\d+)", cell.attrib.get("r", ""))
                    if address:
                        cells.append((address.group(1), int(address.group(2)), cell.attrib["r"], cell_text(cell).strip()))
                if not columns:
                    columns = {column: value for column, _, _, value in cells if value in NOTE_FIELDS}
                    continue
                for column, line, address, value in cells:
                    if column in columns and is_note_path(value):
                        kind = f'XLSX:{sheet.attrib.get("name", part)}!{address}:{columns[column]}'
                        links.append(Link(value, line, kind))
    return links


def check_files(
    paths: list[Path],
    root: Path,
    check_external: bool = False,
    dataset_paths: list[Path] | None = None,
) -> dict:
    stats = Counter(markdown_files=len(paths))
    errors: list[dict] = []
    external: list[dict] = []
    cache: dict[Path, set[str]] = {}

    def check_link(source: Path, link: Link) -> None:
        resolved = resolve_link(source, link.destination, root)
        if resolved is None:
            stats["external_urls"] += 1
            return
        target, fragment = resolved
        outside = not target.is_relative_to(root)
        stats["external_links" if outside else "internal_links"] += 1
        record = {"source": str(source.relative_to(root)) if source.is_relative_to(root) else str(source), **asdict(link), "target": str(target)}
        if outside:
            external.append(record)
            if not check_external:
                return
        if not target.exists():
            errors.append({**record, "error": "missing-path", "external": outside})
        elif fragment and target.suffix.lower() == ".md":
            if target not in cache:
                cache[target] = anchors(target.read_text(encoding="utf-8-sig"))
            if fragment not in cache[target]:
                errors.append({**record, "error": "missing-anchor", "fragment": fragment, "external": outside})

    for source in paths:
        for link in extract_links(source.read_text(encoding="utf-8-sig")):
            check_link(source, link)
    for source in dataset_paths or []:
        format_name = source.suffix.lower().lstrip(".")
        stats[f"dataset_{format_name}_files"] += 1
        try:
            links = csv_note_links(source) if format_name == "csv" else xlsx_note_links(source)
        except (OSError, UnicodeError, csv.Error, zipfile.BadZipFile, ET.ParseError, KeyError, IndexError, ValueError) as error:
            errors.append({"source": str(source.relative_to(root)) if source.is_relative_to(root) else str(source),
                           "line": 1, "destination": "", "error": "dataset-read-error", "detail": str(error)})
            continue
        stats[f"dataset_{format_name}_links"] += len(links)
        for link in links:
            check_link(source, link)
    stats["errors"] = len(errors)
    return {"stats": dict(stats), "errors": errors, "external_links": external}


def repository_root() -> Path:
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path,
                        help="Markdown files/directories or dataset CSV/XLSX; full scan includes review-dataset note paths")
    parser.add_argument("--root", type=Path, default=repository_root())
    parser.add_argument("--check-external", action="store_true", help="Also check links into the surrounding workspace")
    parser.add_argument("--json-output", type=Path, help="Write the detailed report as JSON")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    paths: set[Path] = set()
    dataset_paths: set[Path] = set()
    dataset_root = root / "03_assets/literature/review_dataset"
    for path in args.paths or [root]:
        path = path.resolve()
        if path.is_dir():
            paths.update(p.resolve() for p in path.rglob("*.md") if ".git" not in p.parts)
            dataset_paths.update(p.resolve() for p in path.rglob("*")
                                 if p.is_file() and p.suffix.lower() in {".csv", ".xlsx"}
                                 and p.resolve().is_relative_to(dataset_root))
        elif path.is_file() and path.suffix.lower() == ".md":
            paths.add(path)
        elif path.is_file() and path.suffix.lower() in {".csv", ".xlsx"}:
            dataset_paths.add(path)
        else:
            parser.error(f"Markdown/dataset file or directory does not exist: {path}")
    report = check_files(sorted(paths), root, args.check_external, sorted(dataset_paths))
    for error in report["errors"]:
        print(f'{error["source"]}:{error["line"]}: {error["error"]}: {error["destination"]}')
    print(json.dumps(report["stats"], ensure_ascii=False, sort_keys=True))
    if args.json_output:
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bool(report["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
