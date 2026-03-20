---
name: seminary-lesson
description: Creates seminary Slidev lessons in the Seminary repo from churchofjesuschrist.org student-manual URLs. Scrapes the manual page, writes lessons/YYYY-MM-DD/slides.md plus materials/manual-content.md, and follows a 40-minute flow with QT Time. Use when the user asks to create or prep a seminary lesson, build Slidev for a class date, or provides a seminary manual link and QT leader name.
compatibility: Requires Python 3.10+ in a venv (see workflow; scripts/requirements.txt), network access to churchofjesuschrist.org, Node/npm for Slidev at the Seminary repo root, and a browser to review slides for overflow.
metadata:
  author: garthdb
  version: "1.0"
---

# Seminary lesson (Slidev)

Create or refresh a weekly seminary presentation in the **Seminary** git repo using the official **student manual** lesson URL.

## Context

- **Repo root:** directory that contains `lessons/` and `package.json` (this skill lives at `skills/seminary-lesson/` inside that repo).
- **Output:** `lessons/<YYYY-MM-DD>/slides.md`, `lessons/<YYYY-MM-DD>/materials/manual-content.md`, `lessons/<YYYY-MM-DD>/materials/README.md`.
- **Generator:** [scripts/create-lesson.py](scripts/create-lesson.py) — fetches and parses the manual HTML (server-rendered `<article>` content).
- **Structure & timing:** see [references/LESSON-STRUCTURE.md](references/LESSON-STRUCTURE.md).
- **Teaching guidance (Christlike teaching):** [references/TEACHING-PRINCIPLES.md](references/TEACHING-PRINCIPLES.md) — summary aligned with *Teaching in the Savior’s Way*; full markdown extract at `teaching-in-the-saviors-way/` (repo root).
- **Example prompts:** [assets/example-prompt.txt](assets/example-prompt.txt).

## When to use

Trigger when the user:

- Asks to **create**, **build**, or **prep** a seminary **Slidev** lesson for a **date**
- Pastes a **churchofjesuschrist.org** seminary **student manual** URL
- Mentions **QT Time** and who is leading it
- Asks to **review existing lessons** before creating a new one (scan recent `lessons/*/slides.md` for tone and layout)

## Workflow

1. **Gather inputs**
   - **Date:** normalize to `YYYY-MM-DD` (e.g. `1/30/2026` → `2026-01-30`).
   - **Manual URL:** full `https://www.churchofjesuschrist.org/study/manual/...` lesson link.
   - **QT leader:** first name (or full name if the user prefers); if missing, use `[Student Name]` and note it in the reply.
   - If any of these are missing, ask before writing files.

2. **Review recent lessons (recommended)**  
   Read 1–3 recent `lessons/*/slides.md` files to match voice, layout density, and use of presenter notes—see e.g. `lessons/2026-01-09/slides.md` for a rich example.

   Also read [references/TEACHING-PRINCIPLES.md](references/TEACHING-PRINCIPLES.md) to apply Christlike teaching principles from *Teaching in the Savior’s Way*—especially for discussion questions, presenter notes, and application sections. Open files under `teaching-in-the-saviors-way/` when you need the full chapter (e.g. youth settings, doctrine depth).

3. **Python environment**  
   On macOS/Homebrew Python (PEP 668), use a venv inside the skill (ignored by git):

   ```bash
   python3 -m venv skills/seminary-lesson/.venv
   source skills/seminary-lesson/.venv/bin/activate
   pip install -r skills/seminary-lesson/scripts/requirements.txt
   ```

4. **Run the generator** from the Seminary repo root (with the venv activated):

   ```bash
   python3 skills/seminary-lesson/scripts/create-lesson.py \
     --url "<MANUAL_URL>" \
     --date YYYY-MM-DD \
     --student "<QT_LEADER_NAME>" \
     --seminary-root .
   ```

   Optional: write to a different folder under `lessons/` (e.g. for a dry run):

   ```bash
   --lesson-folder _skill-verify-YYYY-MM-DD
   ```

5. **Fill in QT question**  
   The deck includes a visible placeholder for the student’s question. Replace it before class if the leader shared their question early.

6. **Open Slidev and check for cutoffs**  
   From repo root:

   ```bash
   npx slidev lessons/YYYY-MM-DD/slides.md
   ```

   Step through every slide; fix overflow (split slides, shorten text, move detail to presenter notes). See [references/LESSON-STRUCTURE.md](references/LESSON-STRUCTURE.md).

7. **Optional build check**

   ```bash
   npx slidev build "lessons/YYYY-MM-DD/slides.md" --base "/YYYY-MM-DD/" --out "/tmp/seminary-lesson-build-check"
   ```

   (Adjust `--base` if you use a GitHub Pages prefix—see `.github/scripts/build-all.js`.)

8. **Report back**  
   Tell the user the paths written, approximate slide count, and remind them to verify overflow in the browser and add the QT question.

## Manual page failures

If fetch fails, HTML has no `<article>`, or the site layout changes:

- Report the error.
- Suggest opening the URL in a browser to confirm it loads.
- Offer to create `slides.md` from `lessons/templates/lesson-template.md` manually.

## Validation (optional)

If [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) is installed:

```bash
skills-ref validate skills/seminary-lesson
```

## Progressive disclosure

Keep this file as the single entry point; load [references/LESSON-STRUCTURE.md](references/LESSON-STRUCTURE.md) when detailing timing, QT flow, or overflow checks. Load [references/TEACHING-PRINCIPLES.md](references/TEACHING-PRINCIPLES.md) when shaping discussion, testimony, and invitations to act; use `teaching-in-the-saviors-way/` for deeper quotes or setting-specific help.
