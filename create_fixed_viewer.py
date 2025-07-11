#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create HTML viewer for fixed LaTeX results
Based on batch_nougat_converter's HTML generation
"""

import json
import html
import base64
import sys
from pathlib import Path
from datetime import datetime


def create_fixed_viewer(output_dir, scale=1.5):
    """Create HTML viewer for fixed LaTeX results"""
    
    output_dir = Path(output_dir)
    txt_dir = output_dir / "txt"
    
    # Read fixed JSON
    fixed_json_path = txt_dir / "model_fixed.json"
    if not fixed_json_path.exists():
        print(f"Error: {fixed_json_path} not found")
        return False
    
    with open(fixed_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Read middle.json for metadata
    middle_json_path = txt_dir / "middle.json"
    if middle_json_path.exists():
        with open(middle_json_path, 'r', encoding='utf-8') as f:
            middle_data = json.load(f)
    else:
        middle_data = {}
    
    # Count statistics
    total_formulas = len(results)
    fixed_count = sum(1 for r in results if r.get('latex_fixes'))
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartNougat Fixed LaTeX Results</title>
    
    <!-- MathJax 3 -->
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true
            }},
            svg: {{
                fontCache: 'global',
                scale: {scale}
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
                ignoreClass: 'latex-code'
            }}
        }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    
    <style>
        body {{
            font-family: -apple-system, Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
        }}
        
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .formula-card {{
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
        }}
        
        .formula-image {{
            max-width: 100%;
            max-height: 200px;
            display: block;
            margin: 10px auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        .latex-code {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
            overflow-x: auto;
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        
        .rendered-math {{
            background: #f8f8f8;
            padding: 20px;
            border-radius: 4px;
            margin: 10px 0;
            overflow-x: auto;
            overflow-y: hidden;
            position: relative;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Rendering label */
        .render-label {{
            position: absolute;
            top: 5px;
            left: 10px;
            font-size: 12px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 3px;
            background: rgba(255,255,255,0.9);
            z-index: 10;
        }}
        
        /* Original rendering style */
        .original-render {{
            border: 2px solid #ff6b6b;
            background: #fff5f5;
        }}
        
        .original-render .render-label {{
            color: #ff6b6b;
            background: #ffe0e0;
        }}
        
        /* Fixed rendering style */
        .fixed-render {{
            border: 2px solid #51cf66;
            background: #f3fff5;
        }}
        
        .fixed-render .render-label {{
            color: #51cf66;
            background: #d3f9d8;
        }}
        
        /* Zoom controls */
        .zoom-controls {{
            position: absolute;
            top: 5px;
            right: 5px;
            display: flex;
            gap: 5px;
            background: rgba(255,255,255,0.9);
            padding: 5px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
        
        .zoom-btn {{
            width: 25px;
            height: 25px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 3px;
            font-size: 14px;
        }}
        
        .zoom-btn:hover {{
            background: #f0f0f0;
        }}
        
        .zoom-level {{
            padding: 0 8px;
            font-size: 12px;
            display: flex;
            align-items: center;
        }}
        
        .math-container {{
            display: inline-block;
            transition: transform 0.2s ease;
        }}
        
        /* Scrollbar styling */
        .rendered-math::-webkit-scrollbar {{
            height: 8px;
        }}
        
        .rendered-math::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 4px;
        }}
        
        .rendered-math::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 4px;
        }}
        
        .rendered-math::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
        
        .success {{ color: #4caf50; }}
        .failed {{ color: #f44336; }}
        .fixed {{ color: #2196F3; }}
        
        .category-inline {{ color: #2196F3; }}
        .category-block {{ color: #FF5722; }}
    </style>
</head>
<body>
    <h1>SmartNougat Fixed LaTeX Results</h1>
    
    <div class="stats">
        <p><strong>Total Formulas:</strong> {total_formulas}</p>
        <p><strong>Fixed:</strong> <span class="fixed">{fixed_count}</span></p>
        <p><strong>Unchanged:</strong> {total_formulas - fixed_count}</p>
        <p><strong>Processing Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
'''
    
    # Add each formula result
    for result in results:
        # Get image path
        image_filename = result.get('filename', f"formula_page{result.get('page_index', 0)}_{result.get('index', 0):03d}.png")
        image_path = output_dir / "images" / image_filename
        
        # Read image as base64
        img_base64 = ""
        if image_path.exists():
            with open(image_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine category
        category = result.get('category_type', '')
        category_class = 'category-inline' if '13' in str(category) else 'category-block'
        category_name = 'Inline' if '13' in str(category) else 'Block'
        
        # Check if fixed
        was_fixed = bool(result.get('latex_fixes'))
        fixes_list = result.get('latex_fixes', [])
        
        html_content += f'''
    <div class="formula-card">
        <div class="card-header">
            <span><strong>#{result.get('index', 0) + 1}</strong> Page {result.get('page_index', 0) + 1} | <span class="{category_class}">{category_name} Formula</span></span>
            <span>{'🔧 Fixed' if was_fixed else '✓ Original'}</span>
        </div>
        '''
        
        if img_base64:
            html_content += f'''
        <img src="data:image/png;base64,{img_base64}" class="formula-image" alt="{image_filename}">
        '''
        
        # Show fixed LaTeX code
        html_content += f'''
        <div class="latex-code">
            <strong>LaTeX Code:</strong><br>
            <pre>{html.escape(result.get('latex', ''))}</pre>'''
        
        # Add original LaTeX if it was fixed
        if result.get('latex_original'):
            html_content += f'''
            <details style="margin-top: 10px;">
                <summary style="cursor: pointer; color: #666;">🔧 Original (before fixes): {', '.join(fixes_list)}</summary>
                <pre style="margin-top: 5px; color: #888;">{html.escape(result['latex_original'])}</pre>
            </details>'''
        
        html_content += '''
        </div>'''
        
        # Add original rendering if there were fixes
        if result.get('latex_original'):
            html_content += f'''
        
        <div class="rendered-math original-render" id="math-original-{result.get('index', 0)}">
            <div class="render-label">Original (with errors)</div>
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut('original-{result.get('index', 0)}')">−</button>
                <span class="zoom-level" id="zoom-level-original-{result.get('index', 0)}">100%</span>
                <button class="zoom-btn" onclick="zoomIn('original-{result.get('index', 0)}')">+</button>
                <button class="zoom-btn" onclick="resetZoom('original-{result.get('index', 0)}')" title="Reset">⟲</button>
            </div>
            <div class="math-container" id="math-container-original-{result.get('index', 0)}">
                $${result.get('latex_original', '')}$$
            </div>
        </div>'''
        
        # Add fixed/final rendering
        render_label = '<div class="render-label">Fixed Rendering</div>' if result.get('latex_original') else ''
        extra_class = ' fixed-render' if result.get('latex_original') else ''
        
        html_content += f'''
        
        <div class="rendered-math{extra_class}" id="math-{result.get('index', 0)}">
            {render_label}
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut('{result.get('index', 0)}')">−</button>
                <span class="zoom-level" id="zoom-level-{result.get('index', 0)}">100%</span>
                <button class="zoom-btn" onclick="zoomIn('{result.get('index', 0)}')">+</button>
                <button class="zoom-btn" onclick="resetZoom('{result.get('index', 0)}')" title="Reset">⟲</button>
            </div>
            <div class="math-container" id="math-container-{result.get('index', 0)}">
                $${result.get('latex', '')}$$
            </div>
        </div>
    </div>
'''
    
    html_content += '''
    
    <script>
        const zoomLevels = {};
        
        function zoomIn(id) {
            const current = zoomLevels[id] || 100;
            const newZoom = Math.min(current + 10, 300);
            zoomLevels[id] = newZoom;
            applyZoom(id, newZoom);
        }
        
        function zoomOut(id) {
            const current = zoomLevels[id] || 100;
            const newZoom = Math.max(current - 10, 50);
            zoomLevels[id] = newZoom;
            applyZoom(id, newZoom);
        }
        
        function resetZoom(id) {
            zoomLevels[id] = 100;
            applyZoom(id, 100);
        }
        
        function applyZoom(id, zoom) {
            const container = document.getElementById(`math-container-${id}`);
            const zoomDisplay = document.getElementById(`zoom-level-${id}`);
            
            if (container) {
                container.style.transform = `scale(${zoom / 100})`;
                zoomDisplay.textContent = `${zoom}%`;
            }
        }
        
        // Ctrl + wheel zoom
        document.addEventListener('wheel', (e) => {
            if (e.ctrlKey) {
                e.preventDefault();
                const mathElement = e.target.closest('.rendered-math');
                if (mathElement) {
                    const id = mathElement.id.replace('math-', '').replace('original-', '');
                    if (e.deltaY < 0) {
                        zoomIn(id);
                    } else {
                        zoomOut(id);
                    }
                }
            }
        });
    </script>
</body>
</html>
'''
    
    # Save HTML
    html_path = output_dir / "result_viewer_fixed.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[Success] Fixed HTML viewer created: {html_path}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_fixed_viewer.py <output_directory> [scale]")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    if not create_fixed_viewer(output_dir, scale):
        sys.exit(1)


if __name__ == "__main__":
    main()