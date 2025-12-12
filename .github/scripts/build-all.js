const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const lessonsDir = path.join(__dirname, '../../lessons');
const distDir = path.join(__dirname, '../../dist');

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

let successCount = 0;
let failCount = 0;

// Build each lesson
for (const dir of dirs) {
  const slidesPath = path.join(lessonsDir, dir, 'slides.md');
  
  if (fs.existsSync(slidesPath)) {
    console.log(`📖 Building ${dir}...`);
    
    try {
      const outputDir = path.join(distDir, dir);
      
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
      
      console.log(`✅ Built ${dir}\n`);
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
  console.log(`   Success: ${successCount}`);
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

