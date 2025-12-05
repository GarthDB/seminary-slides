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
      
      console.log(`✅ Built ${dir}\n`);
      successCount++;
    } catch (error) {
      console.error(`❌ Failed to build ${dir}`);
      console.error(error.message);
      failCount++;
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
console.log(`✨ Build complete!`);
console.log(`   Success: ${successCount}`);
if (failCount > 0) {
  console.log(`   Failed: ${failCount}`);
}
console.log(`   Output: ${distDir}`);
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
console.log('💡 To preview locally, run:');
console.log(`   npx serve dist\n`);

