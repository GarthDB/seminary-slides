# Seminary Lesson Slides

A collection of weekly seminary lesson presentations built with [Slidev](https://sli.dev/), designed for teaching Seminary classes for The Church of Jesus Christ of Latter-day Saints.

## 📁 Project Structure

```
seminary/
├── lessons/
│   ├── 2025-09-19/          # Today's lesson
│   │   └── slides.md
│   ├── templates/            # Reusable templates
│   │   └── lesson-template.md
│   └── [YYYY-MM-DD]/        # Future lessons
├── assets/
│   ├── images/              # Lesson images and graphics
│   └── fonts/               # Custom fonts (if needed)
├── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v20.12.2 or higher)
- npm

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the presentation for production
- `npm run export` - Export slides as HTML
- `npm run export-pdf` - Export slides as PDF
- `npm run export-png` - Export slides as PNG images

## 📝 Creating a New Lesson

1. **Copy the template:**
   ```bash
   cp lessons/templates/lesson-template.md lessons/YYYY-MM-DD/slides.md
   ```

2. **Update the date and content:**
   - Replace `[DATE]` with the actual date
   - Fill in scripture references
   - Add key principles and discussion questions
   - Customize the application section

3. **Add any images:**
   - Place images in `assets/images/`
   - Reference them in your slides using relative paths

4. **Run the lesson:**
   ```bash
   cd lessons/YYYY-MM-DD
   npm run dev
   ```

## 🎨 Customization

### Themes
The slides use the default Slidev theme, but you can customize:
- Colors and fonts in the frontmatter
- Background images
- Layouts and components

### Layouts Available
- `default` - Standard slide layout
- `section` - Section divider
- `two-cols` - Two-column layout
- `center` - Centered content
- `end` - Closing slide

### Adding Images
1. Place images in `assets/images/`
2. Reference them in slides:
   ```markdown
   ![Alt text](../assets/images/your-image.jpg)
   ```

## 📚 Lesson Structure

Each lesson follows this structure:
1. **Welcome** - Opening and class structure
2. **Scripture Study** - Main scripture focus
3. **Key Principles** - Two main principles with supporting points
4. **Discussion Questions** - Interactive questions for students
5. **Application** - Weekly challenge and personal reflection
6. **Closing** - Key takeaways and next week preview

## 🔧 Tips for Effective Seminary Slides

- Keep text concise and readable
- Use high-quality images that support the message
- Include discussion questions that encourage participation
- Make application sections practical and actionable
- Use consistent formatting across all lessons

## 📖 Resources

- [Slidev Documentation](https://sli.dev/)
- [Markdown Guide](https://www.markdownguide.org/)
- [LDS Seminary Resources](https://www.churchofjesuschrist.org/study/manual/seminary)

## 🤝 Contributing

This is a personal project for seminary teaching, but suggestions and improvements are welcome!

## 📄 License

MIT License - feel free to use this structure for your own seminary teaching needs.
