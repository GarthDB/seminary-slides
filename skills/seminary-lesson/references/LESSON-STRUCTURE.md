# Seminary lesson structure (Slidev)

This reference supports [SKILL.md](../SKILL.md). For Christlike teaching (discussion tone, testimony, invitations to act), see [TEACHING-PRINCIPLES.md](TEACHING-PRINCIPLES.md). Keep slides concise so content does not overflow the default 16:9 Slidev viewport (see “Overflow” below).

## Timing (40 minutes)

Schedules vary; this is a balanced default that matches a single class period:

| Block | Minutes | Notes |
|------|---------|--------|
| Opening prayer | ~2 | |
| QT Time | ~10 | Student-led question, breakout groups, reconvene, brief reports |
| Scripture / manual focus | ~15 | Read, mark, teach, short activities |
| Discussion & application | ~10 | Pick 1–2 questions if time is short |
| Closing | ~3 | Testimony as prompted; closing prayer |

**QT Time flow**

1. QT leader shares the question (from virtual seminary or their own).
2. Split into small groups (or pairs) for discussion.
3. Bring the class back together.
4. Invite **one** person per group to share a short highlight (1–2 sentences each).

## Slide deck rhythm

Aligned with lessons in `lessons/*/slides.md`:

1. **Title** — date, scripture range, manual subtitle.
2. **Welcome** — today’s focus + **Class Structure (40 min)**.
3. **Opening Activities** — opening prayer + QT (leader name + placeholder for their question + flow reminder).
4. **Section slides** — `layout: section` for major beats; body slides use `layout: default` or `layout: two-cols`.
5. **Discussion** — short list; presenter notes say to trim if needed.
6. **Application** — challenge + reflection.
7. **Closing** — `layout: end`, closing prayer.

## Styling conventions

- Callouts: `<div class="p-4 bg-blue-50 rounded-lg">` (or `purple-50`, `green-50`, `yellow-50`).
- Section titles: `#` on a `layout: section` slide.
- Presenter-only timing: HTML comment blocks `<!-- Presenter Notes: ... -->` after slides.
- Optional: gradients `bg-gradient-to-r from-blue-50 to-purple-50` for emphasis (use sparingly—adds vertical space).

## Overflow (slides “cut off”)

Slidev will clip content that exceeds the slide canvas.

**After generating slides:**

1. From the **Seminary repo root** (where `package.json` lives), run:
   ```bash
   npx slidev lessons/YYYY-MM-DD/slides.md
   ```
2. Step through **every** slide in the browser; fix any slide where text or boxes are clipped.
3. Fixes that usually work: shorten bullet text, split one slide into two, reduce `text-lg` / `text-3xl`, remove a row from grids, or move detail to presenter notes.

The skill’s script does not auto-detect overflow; manual pass is required.

## Repo paths

- Lessons: `lessons/YYYY-MM-DD/slides.md`
- Template reference: `lessons/templates/lesson-template.md`
- Generator script: `skills/seminary-lesson/scripts/create-lesson.py`
