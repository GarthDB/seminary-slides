#!/usr/bin/env python3
"""
Sync all remaining Wed/Fri seminary lessons from a Canvas "Live Class Attendance"
assignment group: for each assignment not yet built under lessons/, extract its
Gospel Library manual URL and date, then call create-lesson.py to generate the deck.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:
    print(f"Missing dependency 'requests': {e}", file=sys.stderr)
    sys.exit(1)

NAME_RE = re.compile(
    r"^W(\d+)D([35])\s+(WEDNESDAY|FRIDAY)\s+(\d{1,2})/(\d{1,2}):\s*(.+?)\s+LIVE ZOOM",
    re.IGNORECASE,
)
MANUAL_URL_RE = re.compile(
    r'https://www\.churchofjesuschrist\.org/study/manual/[^"\s]+'
)


def load_canvas_env(env_path: Path) -> tuple[str, str]:
    # The .env file is the live source of truth (canvas-mcp keeps it current); a
    # shell profile can export a stale CANVAS_API_TOKEN that would otherwise shadow it.
    token, url = "", ""
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key == "CANVAS_API_TOKEN":
                token = val
            elif key == "CANVAS_API_URL":
                url = val
    token = token or os.environ.get("CANVAS_API_TOKEN", "")
    url = url or os.environ.get("CANVAS_API_URL", "")
    if not token or not url:
        print(
            f"CANVAS_API_TOKEN/CANVAS_API_URL not found in env or {env_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    return token, url


def fetch_assignments(base_url: str, token: str, course_id: str, group_id: str) -> list[dict]:
    assignments: list[dict] = []
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/api/v1"):
        base_url += "/api/v1"
    url = f"{base_url}/courses/{course_id}/assignment_groups/{group_id}/assignments"
    params = {"include[]": "description", "per_page": 100}
    headers = {"Authorization": f"Bearer {token}"}
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=45)
        resp.raise_for_status()
        assignments.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
        params = None
    return assignments


def parse_assignment(assignment: dict, year: int) -> tuple[str, str, str] | None:
    """Returns (iso_date, title, manual_url) or None if unparsed."""
    m = NAME_RE.match(assignment.get("name", "").strip())
    if not m:
        return None
    _week, _day_code, _dow, month, day, title = m.groups()
    iso_date = f"{year:04d}-{int(month):02d}-{int(day):02d}"

    desc = assignment.get("description") or ""
    url_m = MANUAL_URL_RE.search(desc)
    if not url_m:
        return None
    return iso_date, title.strip(), url_m.group(0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate remaining seminary lesson decks from a Canvas assignment group."
    )
    parser.add_argument("--course-id", default="116313")
    parser.add_argument("--group-id", default="347676")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument(
        "--seminary-root", type=Path, default=Path(__file__).resolve().parents[3]
    )
    parser.add_argument(
        "--canvas-env",
        type=Path,
        default=Path.home() / "Projects" / "canvas-mcp" / ".env",
        help="Path to a .env file with CANVAS_API_TOKEN and CANVAS_API_URL",
    )
    parser.add_argument("--student", default="[Student Name]")
    parser.add_argument(
        "--force", action="store_true", help="Regenerate decks even if slides.md already exists"
    )
    args = parser.parse_args()

    token, canvas_url = load_canvas_env(args.canvas_env)
    assignments = fetch_assignments(canvas_url, token, args.course_id, args.group_id)

    generator = Path(__file__).resolve().with_name("create-lesson.py")
    rows: list[tuple[str, str, str]] = []

    for a in sorted(assignments, key=lambda a: a.get("name", "")):
        name = a.get("name", "").strip()
        parsed = parse_assignment(a, args.year)
        if parsed is None:
            rows.append(("-", name, "skipped-unparsed"))
            continue
        iso_date, title, manual_url = parsed

        slides_path = args.seminary_root / "lessons" / iso_date / "slides.md"
        if slides_path.exists() and not args.force:
            rows.append((iso_date, title, "skipped-exists"))
            continue

        result = subprocess.run(
            [
                sys.executable,
                str(generator),
                "--url",
                manual_url,
                "--date",
                iso_date,
                "--student",
                args.student,
                "--seminary-root",
                str(args.seminary_root),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip().splitlines()[-1:]
            rows.append((iso_date, title, f"error: {err[0] if err else 'unknown'}"))
        else:
            rows.append((iso_date, title, "created"))

    print(f"{'DATE':<12} {'STATUS':<18} TITLE")
    for iso_date, title, status in rows:
        print(f"{iso_date:<12} {status:<18} {title}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
