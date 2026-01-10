---
name: md-to-html
description: Convert Markdown files to beautifully styled HTML with modern purple gradient theme. Use this skill when users need to: (1) Convert .md files to .html format, (2) Generate HTML reports or documentation from Markdown, (3) Create styled HTML pages with responsive design, (4) Transform Markdown content with tables, code blocks, and special formatting into professional HTML output.
---

# Markdown to HTML Converter

Convert Markdown files to beautifully styled HTML with a modern purple gradient theme, responsive design, and comprehensive formatting support.

## Quick Start

To convert a Markdown file to HTML:

```bash
python scripts/md_to_html.py input.md
```

This generates `input.html` in the same directory with all styles inline.

## Usage Options

### Basic Conversion
```bash
python scripts/md_to_html.py document.md
```

### Specify Output File
```bash
python scripts/md_to_html.py document.md -o output.html
```

### Custom Title and Subtitle
```bash
python scripts/md_to_html.py document.md -t "My Report" -s "Performance Analysis 2024"
```

### All Options
```bash
python scripts/md_to_html.py input.md -o output.html -t "Custom Title" -s "Custom Subtitle"
```

## Supported Markdown Features

### Headers
- H1-H6 with styled hierarchy
- H1: White text with shadow (page title in header)
- H2: Purple with bottom border (main sections)
- H3: Violet (subsections)

### Text Formatting
- **Bold text** with `**text**` or `__text__`
- *Italic text* with `*text*` or `_text_`
- `Inline code` with backticks
- [Links](url) with `[text](url)`
- ![Images](url) with `![alt](url)`

### Code Blocks
Fenced code blocks with language specification:
````markdown
```python
def hello():
    print("Hello, World!")
```
````

Features:
- Dark theme background (#2d2d2d)
- Syntax highlighting ready
- Monospace font (Consolas/Monaco)
- Preserves indentation and line breaks
- Horizontal scrolling for long lines

### Tables
Standard Markdown tables with:
- Purple header background (#667eea)
- Zebra striping (alternating row colors)
- Hover effects on rows
- Rounded corners and shadow

Example:
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### Lists
- Unordered lists with `-` or `*`
- Ordered lists with `1.`, `2.`, etc.
- Colored markers (purple/violet)

### Special Content Boxes

Create highlighted boxes using blockquotes with markers:

**Info Box** (blue border, gray gradient):
```markdown
> 📘 This is an informational note
```

**Warning Box** (orange border, yellow gradient):
```markdown
> ⚠️ This is a warning or important notice
```

**Success Box** (green border, green gradient):
```markdown
> ✅ This is a success message or recommendation
```

### Other Elements
- Horizontal rules with `---`, `***`, or `___`
- Paragraphs (automatic)
- Images with rounded corners and shadow

## Design Features

### Color Scheme
- Primary gradient: #667eea → #764ba2 (purple)
- Background: Full gradient
- Container: White with rounded corners
- Accent colors: Purple (#667eea) and Violet (#764ba2)

### Layout
- Gradient header with title and subtitle
- White content area with 40px padding
- Max-width: 1200px, centered
- Box shadow for depth

### Responsive Design
- Mobile-friendly breakpoints
- Adjusts padding and font sizes
- Tables scale appropriately
- Works on all screen sizes

### Typography
- System fonts: -apple-system, Microsoft YaHei
- Clear hierarchy with size and color
- Optimal line height (1.6)
- Readable code fonts

### Interactive Elements
- Table row hover effects
- Link hover color changes
- Smooth transitions (0.3s ease)

## Output Characteristics

The generated HTML file:
- ✅ Self-contained (all CSS inline)
- ✅ No external dependencies
- ✅ UTF-8 encoded
- ✅ HTML5 standard
- ✅ Opens directly in any browser
- ✅ Print-friendly
- ✅ Professional appearance

## Common Workflows

### Generate Report from Markdown
1. User provides Markdown file path
2. Run: `python scripts/md_to_html.py report.md -t "Performance Report" -s "Q4 2024"`
3. Output: `report.html` ready to share

### Batch Conversion
For multiple files, run the script for each:
```bash
python scripts/md_to_html.py file1.md
python scripts/md_to_html.py file2.md
python scripts/md_to_html.py file3.md
```

### Custom Styling Needs
If users need different colors or styles, modify the `get_html_template()` function in `scripts/md_to_html.py`:
- Change gradient colors in `.header` and `body` background
- Adjust heading colors in `h1`, `h2`, `h3` styles
- Modify box colors in `.info-box`, `.warning-box`, `.success-box`

## Technical Notes

### Code Block Formatting
The script preserves code formatting with:
- `white-space: pre;` in CSS
- Escaped HTML characters
- Original indentation maintained
- Line breaks preserved

### Table Parsing
Tables require:
- Header row with `|` delimiters
- Separator row with `-` characters
- Data rows with `|` delimiters
- Proper alignment of columns

### Character Encoding
Always uses UTF-8 to support:
- Chinese characters (中文)
- Emoji (📘 ⚠️ ✅)
- Special symbols
- International text

## Troubleshooting

**Issue**: Code blocks lose formatting
- **Solution**: Ensure code blocks use triple backticks (```)

**Issue**: Tables don't render
- **Solution**: Check separator row has proper `|---|---|` format

**Issue**: Special characters display incorrectly
- **Solution**: Ensure input file is UTF-8 encoded

**Issue**: Output file not created
- **Solution**: Check write permissions in output directory

## Examples

See the script in action:
```bash
# Simple conversion
python scripts/md_to_html.py README.md

# With custom title
python scripts/md_to_html.py analysis.md -t "Data Analysis Report"

# Full customization
python scripts/md_to_html.py doc.md -o final.html -t "Project Documentation" -s "Version 2.0"
```

The generated HTML will have:
- Beautiful purple gradient header
- Clean white content area
- Styled tables, code blocks, and lists
- Responsive design for all devices
- Professional appearance suitable for reports and documentation
