# Deployment to GitHub Pages

This repository is configured to automatically build and deploy all seminary slideshows to GitHub Pages whenever you push to the `main` branch.

## 🚀 Automatic Deployment

Every time you push to `main`, the GitHub Action will:

1. **Build all slideshows** - Converts each `lessons/*/slides.md` to a static HTML presentation
2. **Generate landing page** - Creates an index page with links to all lessons
3. **Deploy to GitHub Pages** - Publishes everything to `https://[username].github.io/seminary-slides/`

## 📋 Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **GitHub Actions**
4. Save the settings

### 2. Push to Main

Once GitHub Pages is enabled, simply push to the `main` branch:

```bash
git add .
git commit -m "Add new lesson"
git push origin main
```

The deployment will start automatically. You can watch the progress in the **Actions** tab.

### 3. Access Your Slides

After the first successful deployment, your slides will be available at:

```
https://[your-username].github.io/seminary-slides/
```

Each individual lesson will be at:

```
https://[your-username].github.io/seminary-slides/2025-12-05/
```

## 🧪 Testing Locally

Before pushing, you can test the build process locally:

```bash
# Build all slideshows and generate landing page
npm run build-all

# Preview the built site
npx serve dist
```

Then open http://localhost:3000 to see the landing page.

## 📁 Project Structure

```
seminary-slides/
├── lessons/
│   ├── 2025-12-05/
│   │   ├── slides.md          # Source slides
│   │   └── materials/         # Additional resources
│   ├── 2025-11-14/
│   │   └── slides.md
│   └── templates/             # Templates (not deployed)
├── dist/                      # Generated site (git ignored)
│   ├── index.html            # Landing page
│   ├── 2025-12-05/           # Built slideshow
│   └── 2025-11-14/           # Built slideshow
└── .github/
    ├── workflows/
    │   └── deploy.yml        # GitHub Action
    └── scripts/
        ├── build-all.js      # Build script
        └── generate-index.js # Landing page generator
```

## 🎨 Customizing the Landing Page

To customize the landing page appearance, edit:

```
.github/scripts/generate-index.js
```

The styles are embedded in the HTML template within that file.

## 🔧 Troubleshooting

### Build Fails

Check the Actions tab for error messages. Common issues:

- **Syntax errors in slides.md** - Ensure proper YAML frontmatter
- **Missing dependencies** - Make sure package.json is up to date
- **Large assets** - GitHub Pages has a 1GB soft limit

### Pages Not Updating

1. Check that GitHub Pages is enabled in Settings
2. Verify the Action completed successfully in the Actions tab
3. Clear your browser cache
4. Wait a few minutes - GitHub Pages can take 5-10 minutes to update

### Custom Domain

To use a custom domain:

1. Add a `CNAME` file to the `dist/` directory with your domain
2. Update DNS settings to point to GitHub Pages
3. Configure in repository Settings → Pages

## 📝 Notes

- The `templates` folder is excluded from deployment
- Only directories with `slides.md` are built
- The landing page shows lessons in reverse chronological order (newest first)
- Each slideshow is built with its date as the base path for proper routing

## 🆘 Need Help?

If you encounter issues:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the [Slidev build documentation](https://sli.dev/guide/hosting.html)
3. Check the Actions logs for specific error messages

