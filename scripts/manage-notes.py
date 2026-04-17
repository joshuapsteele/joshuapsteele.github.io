#!/usr/bin/env python3
"""
List or remove Hugo notes by frontmatter date, tag, draft status, and syndication flag.

Examples:
    python3 scripts/manage-notes.py list --before 2026-05-01
    python3 scripts/manage-notes.py list --syndicate false

    # Destructive commands are dry-run by default.
    python3 scripts/manage-notes.py delete --from 2026-04-17T10:00:00-04:00 --to 2026-04-17T11:00:00-04:00
    python3 scripts/manage-notes.py delete --tag test --before 2026-05-01 --yes

By default, delete moves matched notes to attic/deleted-notes/ so Hugo no longer
publishes them but Git still keeps the content. Use --permanent with --yes to
unlink files instead.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
LOCAL_TZ = datetime.now().astimezone().tzinfo


@dataclass(frozen=True)
class Note:
    path: Path
    rel_path: Path
    date: datetime
    title: str
    tags: list[str]
    draft: bool
    syndicate: bool
    frontmatter: dict[str, Any]


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected true or false, got {value!r}")


def frontmatter_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return parse_bool(value)
    return bool(value)


def parse_datetime(value: str) -> datetime:
    """Parse a date/datetime filter and return an aware UTC datetime."""
    raw = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        dt = datetime.combine(datetime.fromisoformat(raw).date(), time.min, tzinfo=LOCAL_TZ)
    else:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid date/datetime: {value}") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(timezone.utc)


def normalize_tag(tag: Any) -> str:
    return str(tag).strip().lower().replace("#", "").replace(" ", "-")


def normalize_tags(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        values = [part.strip() for part in raw.split(",")]
    elif isinstance(raw, Iterable):
        values = list(raw)
    else:
        values = [raw]
    seen: set[str] = set()
    tags: list[str] = []
    for value in values:
        tag = normalize_tag(value)
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_inline_array(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    return [strip_quotes(part.strip()) for part in next(csv.reader([inner], skipinitialspace=True))]


def parse_frontmatter_value(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return parse_inline_array(value)
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    return strip_quotes(value)


def parse_frontmatter_block(block: str) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            frontmatter[match.group(1)] = parse_frontmatter_value(match.group(2))
    return frontmatter


def read_note(path: Path, notes_dir: Path) -> Note | None:
    if path.name == "_index.md":
        return None
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        print(f"! skipped {path}: missing frontmatter", file=sys.stderr)
        return None

    frontmatter = parse_frontmatter_block(match.group(1))
    raw_date = frontmatter.get("date")
    if raw_date is None:
        print(f"! skipped {path}: missing date", file=sys.stderr)
        return None
    if isinstance(raw_date, datetime):
        date = raw_date
        if date.tzinfo is None:
            date = date.replace(tzinfo=LOCAL_TZ)
        date = date.astimezone(timezone.utc)
    else:
        date = parse_datetime(str(raw_date))

    return Note(
        path=path,
        rel_path=path.relative_to(notes_dir),
        date=date,
        title=str(frontmatter.get("title") or ""),
        tags=normalize_tags(frontmatter.get("tags")),
        draft=frontmatter_bool(frontmatter.get("draft"), False),
        syndicate=frontmatter_bool(frontmatter.get("syndicate"), True),
        frontmatter=frontmatter,
    )


def iter_notes(notes_dir: Path) -> Iterable[Note]:
    for path in sorted(notes_dir.glob("*.md")):
        note = read_note(path, notes_dir)
        if note:
            yield note


def matches_filters(note: Note, args: argparse.Namespace) -> bool:
    after = args.after or args.from_date
    before = args.before or args.to_date
    if after and note.date < after:
        return False
    if before and note.date >= before:
        return False
    if args.tag:
        wanted = {normalize_tag(tag) for tag in args.tag}
        if not wanted.issubset(set(note.tags)):
            return False
    if args.draft is not None and note.draft != args.draft:
        return False
    if args.syndicate is not None and note.syndicate != args.syndicate:
        return False
    return True


def collect_notes(args: argparse.Namespace) -> list[Note]:
    notes_dir = args.hugo_repo / args.notes_dir
    if not notes_dir.is_dir():
        sys.exit(f"notes directory not found: {notes_dir}")
    return [note for note in iter_notes(notes_dir) if matches_filters(note, args)]


def print_notes(notes: list[Note], as_json: bool) -> None:
    if as_json:
        print(json.dumps([
            {
                "path": str(note.path),
                "date": note.date.isoformat(),
                "title": note.title,
                "tags": note.tags,
                "draft": note.draft,
                "syndicate": note.syndicate,
            }
            for note in notes
        ], indent=2))
        return

    if not notes:
        print("No matching notes.")
        return

    for note in notes:
        flags = []
        if note.draft:
            flags.append("draft")
        if not note.syndicate:
            flags.append("syndicate:false")
        flag_text = f" [{' '.join(flags)}]" if flags else ""
        tag_text = f" tags={','.join(note.tags)}" if note.tags else ""
        title_text = f" {note.title}" if note.title else ""
        print(f"{note.date.isoformat()} {note.rel_path}{flag_text}{tag_text}{title_text}")
    print(f"\nMatched {len(notes)} note(s).")


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def command_list(args: argparse.Namespace) -> int:
    notes = collect_notes(args)
    print_notes(notes, as_json=args.json)
    return 0


def command_delete(args: argparse.Namespace) -> int:
    notes = collect_notes(args)
    if not notes:
        print("No matching notes.")
        return 0

    print_notes(notes, as_json=False)
    active = args.yes and not args.dry_run
    action = "delete permanently" if args.permanent else f"move to {args.trash_dir}"

    if not active:
        print(f"\nDry run only. Re-run with --yes to {action}.")
        return 0

    if args.permanent:
        for note in notes:
            note.path.unlink()
            print(f"- deleted {note.rel_path}")
    else:
        trash_root = args.hugo_repo / args.trash_dir
        for note in notes:
            dest = unique_destination(trash_root / note.rel_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(note.path), str(dest))
            print(f"- moved {note.rel_path} -> {dest.relative_to(args.hugo_repo)}")
    return 0


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--hugo-repo", type=Path, default=Path.cwd(), help="Hugo repo root. Defaults to current directory.")
    parser.add_argument("--notes-dir", type=Path, default=Path("content/notes"), help="Notes directory relative to --hugo-repo.")
    parser.add_argument("--after", type=parse_datetime, help="Include notes at or after this date/time.")
    parser.add_argument("--before", type=parse_datetime, help="Include notes before this date/time.")
    parser.add_argument("--from", dest="from_date", type=parse_datetime, help="Alias for --after.")
    parser.add_argument("--to", dest="to_date", type=parse_datetime, help="Alias for --before.")
    parser.add_argument("--tag", action="append", help="Require tag. Repeat to require multiple tags.")
    parser.add_argument("--draft", type=parse_bool, help="Filter by draft true/false.")
    parser.add_argument("--syndicate", type=parse_bool, help="Filter by syndicate true/false. Missing syndicate counts as true.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List notes matching filters.")
    add_common_filters(list_parser)
    list_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    list_parser.set_defaults(func=command_list)

    delete_parser = subparsers.add_parser("delete", help="Move or permanently delete notes matching filters.")
    add_common_filters(delete_parser)
    delete_parser.add_argument("--trash-dir", type=Path, default=Path("attic/deleted-notes"), help="Move destination relative to --hugo-repo.")
    delete_parser.add_argument("--permanent", action="store_true", help="Unlink files instead of moving to --trash-dir.")
    delete_parser.add_argument("--dry-run", action="store_true", help="Force preview mode even if --yes is provided.")
    delete_parser.add_argument("--yes", action="store_true", help="Actually perform the delete/move operation.")
    delete_parser.set_defaults(func=command_delete)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.hugo_repo = args.hugo_repo.expanduser().resolve()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
