const fs = require('fs');
const path = require('path');

// ===============================================
// CONFIGURATION: Update this date for each new trimester
// ===============================================
const ARCHIVE_DATE = '2025-12-01'; // Lessons before this date go to archive
// ===============================================

// Read all lesson directories
const lessonsDir = path.join(__dirname, '../../lessons');
const distDir = path.join(__dirname, '../../dist');

const lessons = [];

// Get all lesson directories (exclude templates)
const dirs = fs.readdirSync(lessonsDir, { withFileTypes: true })
  .filter(dirent => dirent.isDirectory() && dirent.name !== 'templates')
  .map(dirent => dirent.name)
  .sort()
  .reverse(); // Most recent first

// Extract lesson info from each directory
for (const dir of dirs) {
  const slidesPath = path.join(lessonsDir, dir, 'slides.md');
  
  if (fs.existsSync(slidesPath)) {
    const slidesContent = fs.readFileSync(slidesPath, 'utf-8');
    
    // Extract title from frontmatter or first heading
    let title = dir;
    let subtitle = '';
    
    // Try to extract from frontmatter
    const titleMatch = slidesContent.match(/title:\s*(.+)/);
    if (titleMatch) {
      title = titleMatch[1].replace(/Seminary Lesson - /g, '').trim();
    }
    
    // Try to extract subtitle from the markdown (e.g., "### Doctrine and Covenants 137")
    const subtitleMatch = slidesContent.match(/###\s*(.+)/);
    if (subtitleMatch) {
      subtitle = subtitleMatch[1].trim();
    }
    
    // Try to extract description
    const descMatch = slidesContent.match(/\*\*(.+?)\*\*/);
    const description = descMatch ? descMatch[1] : '';
    
    lessons.push({
      date: dir,
      title: title,
      subtitle: subtitle,
      description: description,
      path: `${dir}/`
    });
  }
}

// Split lessons into current and archived
const archiveDate = new Date(ARCHIVE_DATE);
const currentLessons = lessons.filter(lesson => new Date(lesson.date) >= archiveDate);
const archivedLessons = lessons.filter(lesson => new Date(lesson.date) < archiveDate);

console.log(`📊 Current lessons: ${currentLessons.length}, Archived: ${archivedLessons.length}`);

// Generate HTML
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Seminary Slides</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 2rem;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    header {
      text-align: center;
      color: white;
      margin-bottom: 3rem;
    }
    
    h1 {
      font-size: 3rem;
      margin-bottom: 0.5rem;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .subtitle {
      font-size: 1.2rem;
      opacity: 0.9;
    }
    
    section {
      margin-bottom: 3rem;
    }
    
    .section-title {
      font-size: 2rem;
      color: white;
      text-align: center;
      margin-bottom: 1.5rem;
      font-weight: 600;
    }
    
    .archive-divider {
      border: none;
      height: 2px;
      background: linear-gradient(to right, transparent, rgba(255,255,255,0.3), transparent);
      margin: 3rem auto;
      max-width: 800px;
    }
    
    .archive-title {
      opacity: 0.8;
      font-size: 1.5rem;
    }
    
    .archive-description {
      text-align: center;
      color: white;
      opacity: 0.7;
      font-size: 1rem;
      margin-bottom: 1.5rem;
    }
    
    .lessons-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 1.5rem;
    }
    
    .lesson-card {
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      transition: transform 0.2s, box-shadow 0.2s;
      text-decoration: none;
      color: inherit;
      display: block;
    }
    
    .lesson-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }
    
    .lesson-date {
      color: #667eea;
      font-weight: 600;
      font-size: 0.9rem;
      margin-bottom: 0.5rem;
    }
    
    .lesson-title {
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #2d3748;
    }
    
    .lesson-subtitle {
      font-size: 1rem;
      color: #4a5568;
      margin-bottom: 0.5rem;
    }
    
    .lesson-description {
      font-size: 0.9rem;
      color: #718096;
      line-height: 1.4;
    }
    
    .view-link {
      display: inline-block;
      margin-top: 1rem;
      color: #667eea;
      font-weight: 600;
      font-size: 0.9rem;
    }
    
    .lesson-card:hover .view-link {
      text-decoration: underline;
    }
    
    .lesson-card.archived {
      opacity: 0.85;
      background: #f7fafc;
    }
    
    .lesson-card.archived:hover {
      opacity: 1;
    }
    
    footer {
      text-align: center;
      color: white;
      margin-top: 3rem;
      opacity: 0.8;
      font-size: 0.9rem;
    }
    
    @media (max-width: 768px) {
      h1 {
        font-size: 2rem;
      }
      
      .lessons-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>📖 Seminary Slides</h1>
      <p class="subtitle">Doctrine and Covenants 2025</p>
    </header>
    
    ${currentLessons.length > 0 ? `
    <section>
      <h2 class="section-title">Current Trimester</h2>
      <div class="lessons-grid">
        ${currentLessons.map(lesson => `
          <a href="${lesson.path}" class="lesson-card">
            <div class="lesson-date">${lesson.date}</div>
            <div class="lesson-title">${lesson.title}</div>
            ${lesson.subtitle ? `<div class="lesson-subtitle">${lesson.subtitle}</div>` : ''}
            ${lesson.description ? `<div class="lesson-description">${lesson.description}</div>` : ''}
            <div class="view-link">View Slideshow →</div>
          </a>
        `).join('')}
      </div>
    </section>
    ` : ''}
    
    ${archivedLessons.length > 0 ? `
    <hr class="archive-divider" />
    
    <section>
      <h2 class="section-title archive-title">📦 Archived Lessons</h2>
      <p class="archive-description">Lessons from previous trimesters</p>
      <div class="lessons-grid">
        ${archivedLessons.map(lesson => `
          <a href="${lesson.path}" class="lesson-card archived">
            <div class="lesson-date">${lesson.date}</div>
            <div class="lesson-title">${lesson.title}</div>
            ${lesson.subtitle ? `<div class="lesson-subtitle">${lesson.subtitle}</div>` : ''}
            ${lesson.description ? `<div class="lesson-description">${lesson.description}</div>` : ''}
            <div class="view-link">View Slideshow →</div>
          </a>
        `).join('')}
      </div>
    </section>
    ` : ''}
    
    <footer>
      <p>Built with ❤️ using Slidev</p>
      <p>Updated ${new Date().toLocaleDateString()}</p>
    </footer>
  </div>
</body>
</html>
`;

// Write the index.html file
fs.writeFileSync(path.join(distDir, 'index.html'), html);
console.log(`✓ Generated landing page with ${lessons.length} lessons`);

// Create .nojekyll file to prevent GitHub Pages from processing with Jekyll
fs.writeFileSync(path.join(distDir, '.nojekyll'), '');
console.log(`✓ Created .nojekyll file for GitHub Pages`);