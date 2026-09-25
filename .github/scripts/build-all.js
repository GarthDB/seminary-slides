const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const lessonsDir = path.join(__dirname, '../../lessons');
const distDir = path.join(__dirname, '../../dist');
const manifestPath = path.join(distDir, '.build-manifest.json');

// Recursively hash a directory's contents so unchanged lessons (including
// their materials/ subfolder) can skip a rebuild.
function hashDir(dir) {
  const hash = crypto.createHash('sha256');
  const files = [];

  function walk(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else {
        files.push(fullPath);
      }
    }
  }
  walk(dir);

  for (const file of files) {
    hash.update(path.relative(dir, file));
    hash.update(fs.readFileSync(file));
  }
  return hash.digest('hex');
}

// Check if running in GitHub Actions (for correct base path)
const isGitHubActions = process.env.GITHUB_ACTIONS === 'true';
const basePathPrefix = isGitHubActions ? '/seminary-slides' : '';

console.log('🔨 Building all seminary slideshows...\n');
if (isGitHubActions) {
  console.log('📍 Running in GitHub Actions - using full base path\n');
} else {
  console.log('📍 Running locally - using relative base path\n');
}

// Create dist directory
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Get all lesson directories (exclude templates)
const dirs = fs.readdirSync(lessonsDir, { withFileTypes: true })
  .filter(dirent => dirent.isDirectory() && dirent.name !== 'templates')
  .map(dirent => dirent.name)
  .sort();

// Load the manifest from a prior run's cached dist/, if any.
let manifest = {};
if (fs.existsSync(manifestPath)) {
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  } catch {
    manifest = {};
  }
}
const newManifest = {};

let successCount = 0;
let failCount = 0;
let skippedCount = 0;

// Build each lesson
for (const dir of dirs) {
  const slidesPath = path.join(lessonsDir, dir, 'slides.md');

  if (fs.existsSync(slidesPath)) {
    const outputDir = path.join(distDir, dir);
    const hash = hashDir(path.join(lessonsDir, dir));
    const unchanged = manifest[dir] === hash && fs.existsSync(path.join(outputDir, 'index.html'));

    if (unchanged) {
      console.log(`⏭️  Skipping unchanged: ${dir}`);
      newManifest[dir] = hash;
      successCount++;
      skippedCount++;
      continue;
    }

    console.log(`📖 Building ${dir}...`);

    try {
      // Create output directory
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // Build the slideshow with correct base path
      const basePath = `${basePathPrefix}/${dir}/`;
      execSync(
        `npx slidev build "${slidesPath}" --base "${basePath}" --out "${outputDir}"`,
        { stdio: 'inherit', cwd: path.join(__dirname, '../..') }
      );
      
      // Verify the build was successful
      const indexPath = path.join(outputDir, 'index.html');
      if (!fs.existsSync(indexPath)) {
        throw new Error('Build completed but index.html not found');
      }
      
      // Note: 404.html is automatically created by @sctg/vite-plugin-github-pages-spa
      // This plugin handles SPA routing on GitHub Pages
      
      // Create presenter and overview subdirectories with 404.html for nested route support
      const nestedRoutes = ['presenter', 'overview'];
      for (const route of nestedRoutes) {
        const routeDir = path.join(outputDir, route);
        if (!fs.existsSync(routeDir)) {
          fs.mkdirSync(routeDir, { recursive: true });
        }
        // Copy index.html to each subdirectory as 404.html for SPA routing
        fs.copyFileSync(indexPath, path.join(routeDir, '404.html'));
      }
      
      console.log(`✅ Built ${dir}\n`);
      newManifest[dir] = hash;
      successCount++;
    } catch (error) {
      console.error(`❌ Failed to build ${dir}`);
      console.error(error.message);
      if (error.stack) {
        console.error(error.stack);
      }
      failCount++;
      // Exit with error in CI
      if (isGitHubActions) {
        process.exit(1);
      }
    }
  }
}

// Remove stale dist/<dir> entries for lessons that no longer exist (can
// linger in a restored cache after a lesson is deleted/renamed).
const currentDirs = new Set(dirs);
for (const entry of fs.readdirSync(distDir, { withFileTypes: true })) {
  if (entry.isDirectory() && !currentDirs.has(entry.name)) {
    console.log(`🗑️  Removing stale build: ${entry.name}`);
    fs.rmSync(path.join(distDir, entry.name), { recursive: true, force: true });
  }
}

// Save the manifest so the next run can skip unchanged lessons.
fs.writeFileSync(manifestPath, JSON.stringify(newManifest, null, 2));

// Generate landing page
console.log('🏠 Generating landing page...');
try {
  require('./generate-index.js');
  console.log('✅ Landing page generated\n');
} catch (error) {
  console.error('❌ Failed to generate landing page');
  console.error(error.message);
}

// Summary
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
if (failCount === 0) {
  console.log(`✨ Build complete!`);
  console.log(`   Success: ${successCount} (${skippedCount} unchanged, skipped)`);
  console.log(`   Output: ${distDir}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  if (!isGitHubActions) {
    console.log('💡 To preview locally, run:');
    console.log(`   npx serve dist\n`);
  }
} else {
  console.log(`❌ Build failed!`);
  console.log(`   Success: ${successCount}`);
  console.log(`   Failed: ${failCount}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  process.exit(1);
}

