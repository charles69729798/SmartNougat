#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create HTML viewer for fixed LaTeX results - SmartNougat compatible version
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
    
    # Read original and fixed JSON
    model_json_path = txt_dir / "model.json"
    fixed_json_path = txt_dir / "model_fixed.json"
    
    if not model_json_path.exists():
        print(f"Error: {model_json_path} not found")
        return False
        
    if not fixed_json_path.exists():
        print(f"Error: {fixed_json_path} not found")
        return False
    
    with open(model_json_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
        
    with open(fixed_json_path, 'r', encoding='utf-8') as f:
        fixed_data = json.load(f)
    
    # Count statistics
    total_formulas = 0
    fixed_count = 0
    
    # Process data
    formula_results = []
    formula_index = 0
    
    for page_idx, (orig_page, fixed_page) in enumerate(zip(original_data, fixed_data)):
        if 'layout_dets' in orig_page:
            orig_dets = orig_page.get('layout_dets', [])
            fixed_dets = fixed_page.get('layout_dets', [])
            
            for det_idx, (orig_det, fixed_det) in enumerate(zip(orig_dets, fixed_dets)):
                total_formulas += 1
                
                orig_latex = orig_det.get('latex', '')
                fixed_latex = fixed_det.get('latex', '')
                
                # Check if latex was fixed
                was_fixed = orig_latex != fixed_latex
                if was_fixed:
                    fixed_count += 1
                
                formula_results.append({
                    'index': formula_index,
                    'page_index': page_idx,
                    'original_latex': orig_latex,
                    'fixed_latex': fixed_latex,
                    'was_fixed': was_fixed,
                    'category_id': orig_det.get('category_id', ''),
                    'filename': f"formula_page{page_idx}_{det_idx:03d}.png"
                })
                formula_index += 1
    
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
        
        .latex-panel {{
            margin: 20px 0;
        }}
        
        .latex-box {{
            background: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            border: 2px solid #ddd;
            margin-bottom: 10px;
        }}
        
        .latex-box.original {{
            border-color: #ff6b6b;
        }}
        
        .latex-box.fixed {{
            border-color: #51cf66;
        }}
        
        .latex-box h4 {{
            margin: 0 0 10px 0;
            font-size: 14px;
        }}
        
        .latex-box.original h4 {{
            color: #ff6b6b;
        }}
        
        .latex-box.fixed h4 {{
            color: #51cf66;
        }}
        
        .latex-code {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        .rendered-math {{
            background: white;
            padding: 20px;
            border-radius: 4px;
            margin-top: 10px;
            overflow-x: auto;
            overflow-y: hidden;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .math-container {{
            display: inline-block;
            transition: transform 0.2s ease;
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 5px;
            background: rgba(255,255,255,0.9);
            padding: 5px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
        
        .zoom-btn {{
            width: 30px;
            height: 30px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 3px;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .zoom-btn:hover {{
            background: #f0f0f0;
        }}
        
        .zoom-level {{
            padding: 0 8px;
            font-size: 12px;
            display: flex;
            align-items: center;
            min-width: 45px;
            justify-content: center;
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
    
    # Add each formula
    for result in formula_results:
        # Get image path
        image_path = output_dir / "images" / result['filename']
        
        # Read image as base64
        img_base64 = ""
        if image_path.exists():
            with open(image_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine category
        category = result.get('category_id', '')
        category_class = 'category-inline' if category == 13 else 'category-block'
        category_name = 'Inline' if category == 13 else 'Block'
        
        html_content += f'''
    <div class="formula-card">
        <div class="card-header">
            <span><strong>#{result['index'] + 1}</strong> Page {result['page_index'] + 1} | <span class="{category_class}">{category_name} Formula</span></span>
            <span>{('🔧 Fixed' if result['was_fixed'] else '✓ Original')}</span>
        </div>
        '''
        
        if img_base64:
            html_content += f'''
        <img src="data:image/png;base64,{img_base64}" class="formula-image" alt="{result['filename']}">
        '''
        
        # LaTeX panel
        html_content += '''
        <div class="latex-panel">'''
        
        # Original LaTeX box (코드만)
        html_content += f'''
            <div class="latex-box original">
                <h4>원본 LaTeX / Original LaTeX</h4>
                <div class="latex-code">{html.escape(result['original_latex'])}</div>
            </div>'''
        
        # Fixed LaTeX box (코드만)
        fixed_label = "수정된 LaTeX / Fixed LaTeX" if result['was_fixed'] else "동일 / Same"
        html_content += f'''
            <div class="latex-box fixed">
                <h4>{fixed_label}</h4>
                <div class="latex-code">{html.escape(result['fixed_latex'])}</div>
            </div>'''
        
        html_content += '''
        </div>
        
        <!-- 수정된 버전 렌더링 -->
        <div class="rendered-math" id="render-''' + str(result['index']) + '''">
            <h4>렌더링 결과:</h4>
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut(''' + str(result['index']) + ''')">−</button>
                <span class="zoom-level" id="zoom-level-''' + str(result['index']) + '''">100%</span>
                <button class="zoom-btn" onclick="zoomIn(''' + str(result['index']) + ''')">+</button>
                <button class="zoom-btn" onclick="resetZoom(''' + str(result['index']) + ''')" title="Reset">⟲</button>
            </div>
            <div class="math-container" id="math-container-''' + str(result['index']) + '''">'''
        
        html_content += f'''
                $${result['fixed_latex']}$$
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
                    const id = mathElement.id.replace('render-', '');
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
        print("Usage: python create_fixed_viewer_v2.py <output_directory> [scale]")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    if not create_fixed_viewer(output_dir, scale):
        sys.exit(1)


if __name__ == "__main__":
    main()