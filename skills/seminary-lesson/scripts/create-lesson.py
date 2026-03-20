#!/usr/bin/env python3
"""
Scrape a Church seminary student-manual lesson page and generate Slidev slides.md
plus materials/manual-content.md under lessons/<date>/.
"""

from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError as e:
    print(
        "Missing dependencies. Install with:\n"
        "  pip install -r scripts/requirements.txt\n"
        f"({e})",
        file=sys.stderr,
    )
    sys.exit(1)

USER_AGENT = (
    "Mozilla/5.0 (compatible; SeminaryLessonSkill/1.0; +https://agentskills.io)"
)


@dataclass
class LessonOutline:
    source_url: str
    page_title: str
    meta_description: str
    lesson_label: str  # e.g. "Genesis 5; Moses 6: Lesson 14"
    scripture_ref: str  # e.g. "Moses 6:47–68"
    subtitle: str
    sections: list[dict] = field(default_factory=list)
    question_candidates: list[str] = field(default_factory=list)
    plain_text_outline: str = ""


def _text(el: Tag | None) -> str:
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def _strip_tags_keep_links(tag: Tag) -> str:
    """Flatten to plain text; keep link targets as (url) after label."""
    parts: list[str] = []

    def walk(node: Tag | NavigableString) -> None:
        if isinstance(node, NavigableString):
            t = str(node).strip()
            if t:
                parts.append(t)
            return
        if node.name == "a" and node.get("href"):
            label = _text(node)
            href = node["href"]
            if href.startswith("/"):
                href = f"https://www.churchofjesuschrist.org{href}"
            if label:
                parts.append(f"{label} ({href})")
            return
        for child in node.children:
            walk(child)

    walk(tag)
    return " ".join(" ".join(parts).split())


def fetch_html(url: str, timeout: int = 45) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding or "utf-8"
    return resp.text


def meta_description(soup: BeautifulSoup) -> str:
    m = soup.find("meta", attrs={"name": "description"})
    if m and m.get("content"):
        return m["content"].strip()
    m = soup.find("meta", attrs={"property": "og:description"})
    if m and m.get("content"):
        return m["content"].strip()
    return ""


def page_title(soup: BeautifulSoup) -> str:
    t = soup.find("title")
    return _text(t) if t else ""


def _section_heading(sec: Tag) -> str:
    h = sec.find("header")
    if h:
        h2 = h.find("h2")
        if h2:
            t = _text(h2)
            if t:
                return t
        pt = h.find("p", class_="title")
        if pt:
            t = _text(pt)
            if t:
                return t
        tn = h.find("p", class_="title-number")
        if tn:
            t = _text(tn)
            if t:
                return t
    h2 = sec.find("h2", recursive=False)
    if h2:
        t = _text(h2)
        if t:
            return t
    return "Lesson content"


def _direct_list_items(lst: Tag) -> list[str]:
    out: list[str] = []
    for li in lst.find_all("li", recursive=False):
        t = _strip_tags_keep_links(li)
        if t:
            out.append(t)
    return out


def _consume_section(sec: Tag, questions: list[str]) -> Iterable[dict]:
    """Yield one or more section dicts from a <section> tree (handles nesting)."""
    title = _section_heading(sec)

    def record_question(text: str) -> None:
        t = " ".join(text.split())
        if len(t) < 8 or "?" not in t:
            return
        if t not in questions:
            questions.append(t)

    paras: list[str] = []
    bullets: list[str] = []

    for child in sec.children:
        if not isinstance(child, Tag):
            continue
        if child.name == "header":
            continue
        if child.name == "section":
            # Nested section: flush current, then recurse
            if paras or bullets:
                yield {
                    "title": title,
                    "paragraphs": paras[:16],
                    "bullets": bullets[:24],
                }
                paras, bullets = [], []
            yield from _consume_section(child, questions)
            continue
        if child.name == "p":
            t = _strip_tags_keep_links(child)
            if t:
                record_question(t)
                paras.append(t)
            continue
        if child.name in ("ol", "ul"):
            for item in _direct_list_items(child):
                record_question(item)
                bullets.append(item)
            continue
        if child.name == "figure":
            continue
        if child.name == "div":
            # Pull meaningful text blocks (e.g. captions); skip tiny/icon-only divs
            t = _strip_tags_keep_links(child)
            if len(t) > 60:
                record_question(t)
                paras.append(t)
            continue

    if paras or bullets:
        yield {
            "title": title,
            "paragraphs": paras[:16],
            "bullets": bullets[:24],
        }


def parse_lesson(html_doc: str, source_url: str) -> LessonOutline:
    soup = BeautifulSoup(html_doc, "html.parser")
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()

    article = soup.select_one("main article") or soup.find("article")
    if not article:
        raise ValueError("Could not find <article> in page (layout may have changed).")

    # Plain-text outline before stripping teacher-only blocks
    article_clone = BeautifulSoup(str(article), "html.parser")
    bb_clone = article_clone.find("div", class_="body-block")
    outline_text = bb_clone.get_text("\n", strip=True) if bb_clone else ""

    # Drop teacher-only blocks and printable teaching-method figures (often long / alternate tracks).
    for sel in article.select("figure.for-teacher, figure.no-print"):
        sel.decompose()

    header = article.find("header")
    lesson_label = ""
    scripture_ref = ""
    subtitle = ""
    if header:
        tn = header.find("p", class_="title-number")
        lesson_label = _text(tn)
        h1 = header.find("h1")
        scripture_ref = _text(h1)
        st = header.find("p", class_="subtitle")
        subtitle = _text(st)

    body = article.find("div", class_="body-block")
    sections: list[dict] = []
    questions: list[str] = []

    if body:
        for child in body.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "p":
                t = _strip_tags_keep_links(child)
                if t and "?" in t and len(t) > 8 and t not in questions:
                    questions.append(t)
                if t:
                    sections.append(
                        {
                            "title": "Overview",
                            "paragraphs": [t],
                            "bullets": [],
                        }
                    )
            elif child.name == "section":
                sections.extend(list(_consume_section(child, questions)))

    # Merge adjacent sections with same title (paragraph-only)
    merged_sections: list[dict] = []
    for sec in sections:
        if (
            merged_sections
            and merged_sections[-1]["title"] == sec["title"]
            and not merged_sections[-1]["bullets"]
            and not sec["bullets"]
        ):
            merged_sections[-1]["paragraphs"].extend(sec["paragraphs"])
        else:
            merged_sections.append(
                {
                    "title": sec["title"],
                    "paragraphs": list(sec["paragraphs"]),
                    "bullets": list(sec["bullets"]),
                }
            )

    return LessonOutline(
        source_url=source_url,
        page_title=page_title(soup),
        meta_description=meta_description(soup),
        lesson_label=lesson_label,
        scripture_ref=scripture_ref,
        subtitle=subtitle,
        sections=merged_sections,
        question_candidates=questions[:24],
        plain_text_outline=outline_text[:20000],
    )


def md_escape(text: str) -> str:
    t = html.unescape(text)
    t = t.replace("<", "&lt;").replace(">", "&gt;")
    return t


def chunk_paragraphs(paragraphs: list[str], max_chars: int = 450) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    n = 0
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if n + len(p) > max_chars and buf:
            chunks.append(" ".join(buf))
            buf = [p]
            n = len(p)
        else:
            buf.append(p)
            n += len(p) + 1
    if buf:
        chunks.append(" ".join(buf))
    return chunks[:6]


def format_date_long(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def build_slides(outline: LessonOutline, iso_date: str, student: str) -> str:
    date_long = format_date_long(iso_date)
    title_line = f'Seminary Lesson - {date_long}'
    scripture = md_escape(outline.scripture_ref or "Scripture study")
    subtitle = md_escape(outline.subtitle or "")
    meta = md_escape(outline.meta_description or "")
    student_esc = md_escape(student.strip() or "[Student Name]")

    principle = meta or (
        outline.sections[0]["paragraphs"][0]
        if outline.sections and outline.sections[0]["paragraphs"]
        else "Apply the principles from today’s manual lesson."
    )
    principle = md_escape(principle[:280])

    slides: list[str] = []

    def add_slide(body: str) -> None:
        slides.append("---\nlayout: default\n---\n\n" + body.strip() + "\n")

    def add_section(title: str) -> None:
        slides.append(
            "---\nlayout: section\n---\n\n"
            f"# {md_escape(title)}\n\n"
            "<!-- Presenter Notes: Transition -->\n"
        )

    header = f"""---
theme: default
background: https://source.unsplash.com/1920x1080/?scripture,faith
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## {title_line}
  Weekly lesson for Seminary class
  {scripture}: {subtitle}
  Source materials available in ./materials/
drawings:
  persist: false
transition: slide-left
title: {title_line}
mdc: true
---

# Seminary Lesson
## {date_long}

### {scripture}
**{subtitle}**

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space for next page <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
</div>

<!--
Presenter Notes:
- Class runs about 40 minutes total (adjust to your schedule).
- Source: Church seminary student manual (scraped for outline).
-->

---
layout: default
---

# Welcome to Seminary

<div class="grid grid-cols-2 gap-4 text-sm">

<div>

## Today's Focus
- **Scripture Study**: {scripture}
- **Key idea**: {principle[:200]}{'…' if len(principle) > 200 else ''}
- **Application**: Look for one way to turn to Christ this week

</div>

<div>

## Class Structure (40 min)
1. **Opening Prayer** (2 min)
2. **QT Time** (10 min) — {student_esc}
3. **Scripture / lesson focus** (15 min)
4. **Discussion & application** (10 min)
5. **Closing** (3 min)

</div>

</div>

<!--
Presenter Notes:
- QT: student-led question, breakout groups, return and have one reporter per group share briefly.
-->

---
layout: default
---

# Opening Activities

<div class="space-y-6">

## 🙏 Opening Prayer

<div class="bg-blue-50 p-4 rounded-lg">
Ask someone to offer the opening prayer.
</div>

## 💬 QT Time

<div class="bg-purple-50 p-4 rounded-lg">

**{student_esc} is leading QT Time this week.**

**Question:** *[Add the student’s discussion question before class]*

**Flow:** Small groups → discuss → return together → one person per group shares a highlight.

</div>

</div>

<!--
Presenter Notes:
- QT (~10 min): opening question, breakouts, gather and report.
- If time is tight, shorten breakouts or limit group reporters to 1–2 sentences each.
-->
"""

    slides.append(header.strip() + "\n")

    add_section("From the manual")
    intro_chunks = []
    if outline.sections:
        for sec in outline.sections[:2]:
            intro_chunks.extend(sec["paragraphs"][:2])
    for chunk in chunk_paragraphs(intro_chunks, max_chars=500)[:2]:
        add_slide(
            f"# Lesson focus\n\n<div class=\"p-6 bg-blue-50 rounded-lg text-lg leading-relaxed\">\n\n{md_escape(chunk)}\n\n</div>\n\n<!--\nPresenter Notes:\n- Keep this tight; invite students to open scriptures / manual on their devices if helpful.\n-->"
        )

    # Main sections (skip redundant "Overview"-only noise)
    seen_titles: set[str] = set()
    for sec in outline.sections:
        title = sec["title"].strip()
        if title in ("Overview",) and not sec["bullets"] and len(sec["paragraphs"]) == 1:
            continue
        if title in seen_titles and not sec["bullets"]:
            continue
        seen_titles.add(title)

        add_section(title)

        if sec["bullets"]:
            items = "\n".join(
                f"- {md_escape(b[:220])}" for b in sec["bullets"][:8]
            )
            add_slide(
                f"# {md_escape(title)}\n\n<div class=\"space-y-3 text-base max-w-4xl mx-auto\">\n\n{items}\n\n</div>\n\n<!--\nPresenter Notes:\n- Let students mark scriptures or share what stands out.\n-->"
            )

        for chunk in chunk_paragraphs(sec["paragraphs"], max_chars=480)[:3]:
            add_slide(
                f"# {md_escape(title)}\n\n<div class=\"p-5 bg-green-50 rounded-lg text-base leading-relaxed\">\n\n{md_escape(chunk)}\n\n</div>\n\n<!--\nPresenter Notes:\n- Pause for questions; read verses together where appropriate.\n-->"
            )

    add_section("Discussion")
    qs = outline.question_candidates[:6]
    if len(qs) < 4:
        qs = qs + [
            "What from today’s reading helps you understand why you need the Savior?",
            "What is one way you can ‘come unto Christ’ this week?",
            "How does this lesson change the way you see God’s plan?",
        ]
    qs = qs[:6]
    q_body = "\n\n".join(f"{i + 1}. **{md_escape(q)}**" for i, q in enumerate(qs))
    add_slide(
        f"# Discussion questions\n\n<div class=\"p-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl text-left text-lg space-y-4 max-w-4xl mx-auto\">\n\n{q_body}\n\n</div>\n\n<!--\nPresenter Notes:\n- Pick 1–2 questions if time is short.\n-->"
    )

    add_section("Application & closing")
    add_slide(
        """# This week

<div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">

<div class="p-5 bg-yellow-50 rounded-lg">

## Challenge
- Complete **one** study option from the manual that fits your class time.
- Write **one** sentence about what you felt during the lesson.

</div>

<div class="p-5 bg-pink-50 rounded-lg">

## Personal reflection
- What will you **do** differently because of Christ?

</div>

</div>

<!--
Presenter Notes:
- Bear brief testimony as prompted by the Spirit.
-->
"""
    )

    slides.append(
        """---
layout: end
---

# Closing

<div class="text-center space-y-6">

## 🙏 Closing Prayer

Ask someone to offer the closing prayer.

</div>

<div class="abs-br m-6 text-xs text-gray-400">
"""
        + md_escape(title_line)
        + """
</div>

<!--
Presenter Notes:
- Thank students; remind them of reading for next time if applicable.
-->
"""
    )

    return "\n".join(slides)


def write_manual_markdown(
    dest: Path,
    outline: LessonOutline,
    iso_date: str,
    student: str,
) -> None:
    lines = [
        "---",
        f"date: {iso_date}",
        f"qt_leader: {student}",
        f"source_url: {outline.source_url}",
        "---",
        "",
        f"# Manual content outline ({iso_date})",
        "",
        f"- **Page title:** {outline.page_title}",
        f"- **Lesson label:** {outline.lesson_label}",
        f"- **Scripture block:** {outline.scripture_ref}",
        f"- **Subtitle:** {outline.subtitle}",
        "",
        "## Meta description",
        "",
        outline.meta_description or "_None_",
        "",
        "## Plain text outline (from manual body)",
        "",
        "```text",
        outline.plain_text_outline or "",
        "```",
        "",
        "## Structured sections (post-cleanup)",
        "",
    ]
    for sec in outline.sections:
        lines.append(f"### {sec['title']}")
        for p in sec["paragraphs"][:8]:
            lines.append(f"- {p}")
        if sec["bullets"]:
            lines.append("")
            lines.append("_List items:_")
            for b in sec["bullets"][:12]:
                lines.append(f"- {b}")
        lines.append("")

    dest.write_text("\n".join(lines), encoding="utf-8")


def write_materials_readme(dest: Path, outline: LessonOutline, iso_date: str) -> None:
    u = outline.source_url
    parsed = urlparse(u)
    lines = [
        f"# Materials — {iso_date}",
        "",
        "- Student manual lesson: "
        f"[Open on ChurchofJesusChrist.org]({u})",
        f"- Host: `{parsed.netloc}`",
        "",
        "Supporting files for this week (images, QT prep, etc.) can live in subfolders under `materials/`.",
        "",
    ]
    dest.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create seminary Slidev lesson from manual URL.")
    parser.add_argument("--url", required=True, help="Full churchofjesuschrist.org manual lesson URL")
    parser.add_argument("--date", required=True, help="Lesson date as YYYY-MM-DD")
    parser.add_argument("--student", default="[Student Name]", help="QT Time student first name")
    parser.add_argument(
        "--seminary-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to Seminary repo root (contains lessons/)",
    )
    parser.add_argument(
        "--lesson-folder",
        default=None,
        help="Folder name under lessons/ (defaults to --date)",
    )
    args = parser.parse_args()

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("Invalid --date; use YYYY-MM-DD", file=sys.stderr)
        return 2

    folder = args.lesson_folder or args.date
    lesson_dir = (args.seminary_root / "lessons" / folder).resolve()
    materials = lesson_dir / "materials"
    materials.mkdir(parents=True, exist_ok=True)

    try:
        doc = fetch_html(args.url)
        outline = parse_lesson(doc, args.url.strip())
    except Exception as e:
        print(f"Failed to fetch or parse manual: {e}", file=sys.stderr)
        return 1

    slides_md = build_slides(outline, args.date, args.student)
    (lesson_dir / "slides.md").write_text(slides_md, encoding="utf-8")
    write_manual_markdown(materials / "manual-content.md", outline, args.date, args.student)
    write_materials_readme(materials / "README.md", outline, args.date)

    print(f"Wrote: {lesson_dir / 'slides.md'}")
    print(f"Wrote: {materials / 'manual-content.md'}")
    print(f"Wrote: {materials / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
