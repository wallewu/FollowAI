#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to HTML Converter with Modern Purple Gradient Theme
Converts Markdown files to beautifully styled HTML with inline CSS
"""

import sys
import re
import argparse
from pathlib import Path

def escape_html(text):
    """Escape HTML special characters"""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

def parse_markdown(md_content):
    """Parse Markdown content and convert to HTML"""
    lines = md_content.split('\n')
    html_lines = []
    in_code_block = False
    in_table = False
    in_list = False
    code_language = ''
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line.strip()[3:].strip()
                html_lines.append(f'<pre><code class="language-{code_language}">')
            else:
                in_code_block = False
                html_lines.append('</code></pre>')
            i += 1
            continue
        
        if in_code_block:
            html_lines.append(escape_html(line))
            i += 1
            continue
        
        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{parse_inline(line[2:])}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{parse_inline(line[3:])}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{parse_inline(line[4:])}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{parse_inline(line[5:])}</h4>')
        elif line.startswith('##### '):
            html_lines.append(f'<h5>{parse_inline(line[6:])}</h5>')
        elif line.startswith('###### '):
            html_lines.append(f'<h6>{parse_inline(line[7:])}</h6>')
        
        # Tables
        elif '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                html_lines.append('<table>')
                # Parse header row
                cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                html_lines.append('<thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{parse_inline(cell)}</th>')
                html_lines.append('</tr></thead>')
                # Skip separator line
                i += 1
                if i < len(lines) and '|' in lines[i] and '-' in lines[i]:
                    i += 1
                html_lines.append('<tbody>')
                continue
            else:
                # Parse data row
                cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<td>{parse_inline(cell)}</td>')
                html_lines.append('</tr>')
        elif in_table and not ('|' in line):
            in_table = False
            html_lines.append('</tbody></table>')
            continue
        
        # Lists
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                in_list = True
                html_lines.append('<ul>')
            html_lines.append(f'<li>{parse_inline(line.strip()[2:])}</li>')
        elif line.strip() and line[0].isdigit() and '. ' in line:
            if not in_list:
                in_list = True
                html_lines.append('<ol>')
            content = line.strip().split('. ', 1)[1]
            html_lines.append(f'<li>{parse_inline(content)}</li>')
        elif in_list and not line.strip():
            html_lines.append('</ul>' if lines[i-1].strip().startswith(('-', '*')) else '</ol>')
            in_list = False
        
        # Special boxes (blockquotes with markers)
        elif line.strip().startswith('> '):
            content = line.strip()[2:]
            if content.startswith('⚠️') or content.startswith('**警告') or content.startswith('**Warning'):
                html_lines.append(f'<div class="warning-box">{parse_inline(content)}</div>')
            elif content.startswith('✅') or content.startswith('**建议') or content.startswith('**Success'):
                html_lines.append(f'<div class="success-box">{parse_inline(content)}</div>')
            else:
                html_lines.append(f'<div class="info-box">{parse_inline(content)}</div>')
        
        # Horizontal rule
        elif line.strip() in ['---', '***', '___']:
            html_lines.append('<hr>')
        
        # Paragraphs
        elif line.strip():
            html_lines.append(f'<p>{parse_inline(line)}</p>')
        else:
            html_lines.append('')
        
        i += 1
    
    # Close any open tags
    if in_table:
        html_lines.append('</tbody></table>')
    if in_list:
        html_lines.append('</ul>')
    
    return '\n'.join(html_lines)

def parse_inline(text):
    """Parse inline Markdown elements"""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    
    # Images
    text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', text)
    
    return text

def get_html_template():
    """Return the HTML template with modern purple gradient theme"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 60px 40px;
            text-align: center;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        h1 {{
            font-size: 2.5em;
            color: white;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        h2 {{
            font-size: 2em;
            color: #667eea;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        h3 {{
            font-size: 1.5em;
            color: #764ba2;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        h4 {{
            font-size: 1.3em;
            color: #667eea;
            margin-top: 25px;
            margin-bottom: 12px;
        }}
        
        h5 {{
            font-size: 1.1em;
            color: #764ba2;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        h6 {{
            font-size: 1em;
            color: #667eea;
            margin-top: 15px;
            margin-bottom: 8px;
        }}
        
        p {{
            margin-bottom: 15px;
            color: #333;
        }}
        
        /* Info Box */
        .info-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
            border-left: 4px solid #3498db;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        /* Warning Box */
        .warning-box {{
            background: linear-gradient(135deg, #fff9e6 0%, #ffecb3 100%);
            border-left: 4px solid #ff6b35;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        /* Success Box */
        .success-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left: 4px solid #2e7d32;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        thead {{
            background: #667eea;
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tbody tr:hover {{
            background-color: #e8eaf6;
            transition: all 0.3s ease;
        }}
        
        /* Code Blocks */
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        pre code {{
            font-family: Consolas, Monaco, "Courier New", monospace;
            font-size: 0.9em;
            line-height: 1.5;
            white-space: pre;
            display: block;
        }}
        
        /* Inline Code */
        code {{
            background: #f4f4f4;
            color: #e83e8c;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, Monaco, "Courier New", monospace;
            font-size: 0.9em;
        }}
        
        pre code {{
            background: transparent;
            color: #f8f8f2;
            padding: 0;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
            color: #333;
        }}
        
        ul li::marker {{
            color: #667eea;
        }}
        
        ol li::marker {{
            color: #764ba2;
            font-weight: bold;
        }}
        
        /* Links */
        a {{
            color: #667eea;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        /* Horizontal Rule */
        hr {{
            border: none;
            border-top: 2px solid #e0e0e0;
            margin: 30px 0;
        }}
        
        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        /* Strong and Emphasis */
        strong {{
            color: #667eea;
            font-weight: 600;
        }}
        
        em {{
            color: #764ba2;
            font-style: italic;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header {{
                padding: 40px 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            h2 {{
                font-size: 1.6em;
            }}
            
            h3 {{
                font-size: 1.3em;
            }}
            
            table {{
                font-size: 0.9em;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>
        <div class="content">
{content}
        </div>
    </div>
</body>
</html>'''

def convert_md_to_html(md_file, output_file=None, title=None, subtitle=None):
    """Convert Markdown file to HTML"""
    md_path = Path(md_file)
    
    if not md_path.exists():
        print(f"Error: File '{md_file}' not found.")
        return False
    
    # Read Markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first H1 if not provided
    if not title:
        first_line = md_content.split('\n')[0]
        if first_line.startswith('# '):
            title = first_line[2:].strip()
        else:
            title = md_path.stem
    
    if not subtitle:
        subtitle = "Generated from Markdown"
    
    # Convert Markdown to HTML
    html_content = parse_markdown(md_content)
    
    # Generate full HTML
    template = get_html_template()
    full_html = template.format(
        title=title,
        subtitle=subtitle,
        content=html_content
    )
    
    # Determine output file
    if not output_file:
        output_file = md_path.with_suffix('.html')
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"[SUCCESS] Converted '{md_file}' to '{output_file}'")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to HTML with modern purple gradient theme'
    )
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output', help='Output HTML file (default: same name as input with .html extension)')
    parser.add_argument('-t', '--title', help='Document title (default: extracted from first H1 or filename)')
    parser.add_argument('-s', '--subtitle', help='Document subtitle (default: "Generated from Markdown")')
    
    args = parser.parse_args()
    
    success = convert_md_to_html(
        args.input,
        args.output,
        args.title,
        args.subtitle
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
