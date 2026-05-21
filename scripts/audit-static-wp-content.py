#!/usr/bin/env python3
"""
Audit legacy WordPress media under static/wp-content without deleting files.

The cleanup script in this repo is intentionally destructive. This companion
audit builds a reviewable inventory first, so legacy media can be pruned only
after checking which files are still referenced by site sources.
"""

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
WP_DIR = STATIC_DIR / "wp-content"
JSON_OUTPUT = ROOT / "scripts" / "data" / "audit-static-wp-content.json"
MD_OUTPUT = ROOT / "docs" / "AUDIT-static-wp-content.md"

SOURCE_PATHS = [
    "content",
    "layouts",
    "assets",
    "data",
    "archetypes",
    "templates",
    "hugo.yaml",
    "config.yaml",
    "config.toml",
    "netlify.toml",
]

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def human_size(num_bytes):
    units = ["B", "KiB", "MiB", "GiB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024


def iter_source_files():
    for source in SOURCE_PATHS:
        path = ROOT / source
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in TEXT_SUFFIXES:
                yield path
            continue
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in TEXT_SUFFIXES:
                yield file_path


def load_sources():
    sources = []
    for file_path in iter_source_files():
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        sources.append(
            {
                "path": file_path.relative_to(ROOT).as_posix(),
                "text": text,
            }
        )
    return sources


def reference_variants(served_path):
    encoded_path = quote(served_path, safe="/-._~:%")
    variants = {
        served_path,
        served_path.lstrip("/"),
        encoded_path,
        encoded_path.lstrip("/"),
    }

    for path in {served_path, encoded_path}:
        for origin in (
            "https://joshuapsteele.com",
            "http://joshuapsteele.com",
            "https://www.joshuapsteele.com",
            "http://www.joshuapsteele.com",
            "https://joshuapsteele.github.io",
        ):
            variants.add(origin + path)

    return sorted(variants, key=len, reverse=True)


def find_references(served_path, sources):
    variants = reference_variants(served_path)
    matches = []

    for source in sources:
        text = source["text"]
        line_starts = None
        for variant in variants:
            start = text.find(variant)
            if start == -1:
                continue
            if line_starts is None:
                line_starts = [0]
                for index, char in enumerate(text):
                    if char == "\n":
                        line_starts.append(index + 1)
            line_no = 1
            for index, line_start in enumerate(line_starts):
                if line_start > start:
                    line_no = index
                    break
            else:
                line_no = len(line_starts)
            matches.append(
                {
                    "source": source["path"],
                    "line": line_no,
                    "matched": variant,
                }
            )
            break

    return matches


def audit():
    if not WP_DIR.exists():
        raise SystemExit(f"Missing directory: {WP_DIR}")

    sources = load_sources()
    files = sorted(path for path in WP_DIR.rglob("*") if path.is_file())
    records = []

    for file_path in files:
        rel_static = file_path.relative_to(STATIC_DIR).as_posix()
        served_path = "/" + rel_static
        size = file_path.stat().st_size
        references = find_references(served_path, sources)
        records.append(
            {
                "path": file_path.relative_to(ROOT).as_posix(),
                "served_path": served_path,
                "extension": file_path.suffix.lower().lstrip(".") or "[none]",
                "size_bytes": size,
                "size": human_size(size),
                "referenced": bool(references),
                "references": references,
            }
        )

    total_size = sum(record["size_bytes"] for record in records)
    referenced = [record for record in records if record["referenced"]]
    orphan_candidates = [record for record in records if not record["referenced"]]

    return {
        "generated_on": date.today().isoformat(),
        "source_scope": SOURCE_PATHS,
        "source_files_scanned": len(sources),
        "totals": {
            "files": len(records),
            "size_bytes": total_size,
            "size": human_size(total_size),
            "referenced_files": len(referenced),
            "orphan_candidates": len(orphan_candidates),
        },
        "files": records,
    }


def extension_summary(records):
    summary = defaultdict(lambda: {"files": 0, "referenced": 0, "orphan_candidates": 0, "size_bytes": 0})
    for record in records:
        ext = record["extension"]
        summary[ext]["files"] += 1
        summary[ext]["size_bytes"] += record["size_bytes"]
        if record["referenced"]:
            summary[ext]["referenced"] += 1
        else:
            summary[ext]["orphan_candidates"] += 1

    rows = []
    for ext, values in sorted(summary.items()):
        rows.append(
            {
                "extension": ext,
                "files": values["files"],
                "referenced": values["referenced"],
                "orphan_candidates": values["orphan_candidates"],
                "size": human_size(values["size_bytes"]),
            }
        )
    return rows


def write_json(report):
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def write_markdown(report):
    records = report["files"]
    orphan_candidates = sorted(
        [record for record in records if not record["referenced"]],
        key=lambda record: record["size_bytes"],
        reverse=True,
    )
    referenced_records = [record for record in records if record["referenced"]]
    references_per_source = Counter()
    for record in referenced_records:
        for ref in record["references"]:
            references_per_source[ref["source"]] += 1

    lines = [
        "# Static wp-content Audit",
        "",
        f"**Updated:** {report['generated_on']}",
        "",
        "This is a non-destructive audit of legacy WordPress media under `static/wp-content/`. It does not run `scripts/cleanup_images.sh` and does not delete files.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Files in `static/wp-content/` | {report['totals']['files']} |",
        f"| Total size | {report['totals']['size']} |",
        f"| Referenced by site sources | {report['totals']['referenced_files']} |",
        f"| Orphan candidates | {report['totals']['orphan_candidates']} |",
        f"| Source files scanned | {report['source_files_scanned']} |",
        "",
        "Site sources scanned: `content/`, `layouts/`, `assets/`, `data/`, `archetypes/`, `templates/`, and Hugo/config files when present. Generated audit files and docs are intentionally excluded so they do not count as live site references.",
        "",
        "## By Extension",
        "",
        "| Extension | Files | Referenced | Orphan candidates | Size |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for row in extension_summary(records):
        lines.append(
            f"| `{row['extension']}` | {row['files']} | {row['referenced']} | {row['orphan_candidates']} | {row['size']} |"
        )

    lines.extend(
        [
            "",
            "## Referenced Sources",
            "",
        ]
    )

    if references_per_source:
        lines.extend(
            f"- `{source}` ({count} media reference{'s' if count != 1 else ''})"
            for source, count in sorted(references_per_source.items())
        )
    else:
        lines.append("_No references found in site sources._")

    lines.extend(
        [
            "",
            "## Largest Orphan Candidates",
            "",
            "| Size | Served path |",
            "| ---: | --- |",
        ]
    )

    if orphan_candidates:
        for record in orphan_candidates[:25]:
            lines.append(f"| {record['size']} | `{record['served_path']}` |")
    else:
        lines.append("| n/a | _No orphan candidates found._ |")

    lines.extend(
        [
            "",
            "## All Orphan Candidates",
            "",
        ]
    )

    if orphan_candidates:
        for record in orphan_candidates:
            lines.append(f"- `{record['served_path']}` ({record['size']})")
    else:
        lines.append("_No orphan candidates found._")

    lines.extend(
        [
            "",
            "## Cleanup Recommendation",
            "",
            "Do not run `scripts/cleanup_images.sh` as-is. It removes the entire `static/wp-content/` directory, but this audit found live references there. Review the orphan candidates above first, then delete only confirmed-unused files in a separate, explicit cleanup pass.",
            "",
            f"Machine-readable details are in `scripts/data/{JSON_OUTPUT.name}`.",
            "",
        ]
    )

    MD_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    report = audit()
    write_json(report)
    write_markdown(report)

    totals = report["totals"]
    print(f"Scanned {totals['files']} static/wp-content files ({totals['size']}).")
    print(f"Referenced: {totals['referenced_files']}")
    print(f"Orphan candidates: {totals['orphan_candidates']}")
    print(f"Wrote {JSON_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
