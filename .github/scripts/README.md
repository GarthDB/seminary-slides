# Build Scripts

This folder contains scripts used by the GitHub Actions workflow to build and deploy seminary slides.

## Scripts

### `build-all.js`
Builds all lesson slideshows and creates the static site.

**Usage:**
```bash
npm run build-all
```

### `generate-index.js`
Generates the landing page with links to all lessons.

## 📅 Updating Archive Date for New Trimester

When starting a new trimester, update the archive date in `generate-index.js`:

```javascript
// ===============================================
// CONFIGURATION: Update this date for each new trimester
// ===============================================
const ARCHIVE_DATE = '2025-12-01'; // Lessons before this date go to archive
// ===============================================
```

**Steps:**
1. Open `.github/scripts/generate-index.js`
2. Find the `ARCHIVE_DATE` constant at the top of the file
3. Update to the first Monday of the new trimester (format: `YYYY-MM-DD`)
4. Commit and push to main

**Example:**
```javascript
// For a trimester starting March 3, 2025
const ARCHIVE_DATE = '2025-03-03';
```

Lessons dated before this date will appear in the "Archived Lessons" section.
Lessons on or after this date will appear in the "Current Trimester" section.

## How It Works

The landing page will automatically:
- Show current trimester lessons at the top
- Add a visual divider (horizontal rule)
- Show archived lessons below with slightly muted styling
- Display counts: "Current lessons: X, Archived: Y" in build logs




