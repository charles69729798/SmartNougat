#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create HTML viewer with automatic MathJax detection
HTML 내부에서 자동으로 MathJax를 찾아서 로드
"""

import json
import html
import base64
import sys
import os
from pathlib import Path
from datetime import datetime


def create_fixed_viewer(output_dir, scale=1.5):
    """Create HTML viewer with automatic MathJax detection"""
    
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
    
    # Process data
    formula_results = []
    fixed_count = 0
    total_formulas = 0
    formula_index = 0
    
    for page_idx, (orig_page, fixed_page) in enumerate(zip(original_data, fixed_data)):
        for det_idx, (orig_det, fixed_det) in enumerate(
            zip(orig_page.get('layout_dets', []), fixed_page.get('layout_dets', []))
        ):
            if 'latex' in orig_det:
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
    
    # Generate HTML with automatic MathJax detection
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartNougat Fixed LaTeX Results</title>
    
    <!-- MathJax Auto-Detection Script -->
    <script>
        // MathJax 자동 감지 및 로드
        (function() {{
            // 가능한 MathJax 경로들 (우선순위 순서)
            var mathjaxPaths = [
                // 1. 같은 폴더
                './mathjax/package/es5/tex-svg.js',
                '../mathjax/package/es5/tex-svg.js',
                '../../mathjax/package/es5/tex-svg.js',
                '../../../mathjax/package/es5/tex-svg.js',
                
                // 2. node_modules 경로
                './node_modules/mathjax/es5/tex-svg.js',
                '../node_modules/mathjax/es5/tex-svg.js',
                '../../node_modules/mathjax/es5/tex-svg.js',
                
                // 3. 전역 설치 경로 (Windows)
                'C:/mathjax/package/es5/tex-svg.js',
                'D:/mathjax/package/es5/tex-svg.js',
                
                // 4. CDN (최후의 수단)
                'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
            ];
            
            // MathJax 설정
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
            
            // 순차적으로 경로 시도
            function tryLoadMathJax(index) {{
                if (index >= mathjaxPaths.length) {{
                    console.error('MathJax를 찾을 수 없습니다!');
                    document.getElementById('mathjax-status').innerHTML = 
                        '<span style="color: red;">⚠️ MathJax 로드 실패 - 수식이 렌더링되지 않습니다</span>';
                    return;
                }}
                
                var path = mathjaxPaths[index];
                var script = document.createElement('script');
                script.src = path;
                script.async = true;
                
                script.onload = function() {{
                    console.log('MathJax 로드 성공:', path);
                    var status = document.getElementById('mathjax-status');
                    if (status) {{
                        if (path.includes('cdn.jsdelivr.net')) {{
                            status.innerHTML = '<span style="color: orange;">🌐 CDN MathJax 사용중 (인터넷 필요)</span>';
                        }} else {{
                            status.innerHTML = '<span style="color: green;">✅ 로컬 MathJax 사용중</span>';
                        }}
                    }}
                }};
                
                script.onerror = function() {{
                    console.log('시도 실패:', path);
                    // 다음 경로 시도
                    tryLoadMathJax(index + 1);
                }};
                
                document.head.appendChild(script);
            }}
            
            // 첫 번째 경로부터 시도
            tryLoadMathJax(0);
        }})();
    </script>
    
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
            text-align: center;
        }}
        
        .stats h2 {{
            margin-top: 0;
            color: #2563eb;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2563eb;
        }}
        
        .stat-label {{
            color: #6b7280;
            margin-top: 5px;
        }}
        
        #mathjax-status {{
            text-align: center;
            padding: 10px;
            background: #f9fafb;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        .formula-item {{
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .formula-header {{
            background: #f3f4f6;
            padding: 10px 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .formula-title {{
            font-weight: bold;
            color: #374151;
        }}
        
        .fixed-badge {{
            background: #10b981;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .formula-content {{
            padding: 20px;
        }}
        
        .formula-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .formula-image {{
            text-align: center;
            padding: 10px;
            background: #f9fafb;
            border-radius: 4px;
        }}
        
        .formula-image img {{
            max-width: 100%;
            height: auto;
        }}
        
        .latex-panel {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 4px;
        }}
        
        .latex-box {{
            margin-bottom: 15px;
        }}
        
        .latex-box h4 {{
            margin: 0 0 10px 0;
            color: #374151;
            font-size: 14px;
        }}
        
        .latex-code {{
            background: white;
            padding: 10px;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
            margin-bottom: 10px;
        }}
        
        .copy-btn {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        .copy-btn:hover {{
            background: #1d4ed8;
        }}
        
        .rendered-math {{
            background: #2563eb;
            padding: 30px;
            border-radius: 4px;
            text-align: center;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: auto;
        }}
        
        .rendered-math h4 {{
            position: absolute;
            top: 10px;
            left: 15px;
            margin: 0;
            font-size: 14px;
            color: #bfdbfe;
        }}
        
        .rendered-math mjx-container {{
            color: white !important;
            fill: white !important;
        }}
        
        .rendered-math svg {{
            fill: white !important;
            max-width: 100%;
            height: auto;
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        
        .zoom-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .zoom-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .zoom-level {{
            color: white;
            font-size: 12px;
            min-width: 40px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>SmartNougat LaTeX 수정 결과</h1>
    
    <div id="mathjax-status">
        <span style="color: #6b7280;">🔍 MathJax 로드 중...</span>
    </div>
    
    <div class="stats">
        <h2>처리 통계</h2>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">{total_formulas}</div>
                <div class="stat-label">전체 수식</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{fixed_count}</div>
                <div class="stat-label">수정된 수식</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{fixed_count/total_formulas*100:.1f}%</div>
                <div class="stat-label">수정 비율</div>
            </div>
        </div>
    </div>
'''

    # Add formula items
    images_dir = output_dir / "images"
    
    for result in formula_results:
        # Read image file and convert to base64
        img_path = images_dir / result['filename']
        if img_path.exists():
            with open(img_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                img_src = f"data:image/png;base64,{img_data}"
        else:
            img_src = ""
        
        fixed_badge = '<span class="fixed-badge">수정됨</span>' if result['was_fixed'] else ''
        
        # Determine labels based on whether it was fixed
        if result['was_fixed']:
            original_label = "원본 LaTeX (오류 포함):"
            fixed_label = "수정된 LaTeX ✓:"
        else:
            original_label = "원본 LaTeX:"
            fixed_label = "검증된 LaTeX:"
        
        html_content += f'''
    <div class="formula-item">
        <div class="formula-header">
            <span class="formula-title">#{result['index'] + 1} Page {result['page_index'] + 1} | Block Formula</span>
            {fixed_badge}
        </div>
        <div class="formula-content">
            <div class="formula-grid">
                <div class="formula-image">
                    <h4>원본 이미지</h4>
                    <img src="{img_src}" class="formula-image" alt="{result['filename']}">
                </div>
                
                <div class="latex-panel">
                    <div class="latex-box">
                        <h4>{original_label}</h4>
                        <div class="latex-code" id="original-{result['index']}">{html.escape(result['original_latex'])}</div>
                        <button class="copy-btn" onclick="copyLatexText('original-{result['index']}')">복사</button>
                    </div>
                    
                    <div class="latex-box">
                        <h4>{fixed_label}</h4>
                        <div class="latex-code" id="fixed-{result['index']}">{html.escape(result['fixed_latex'])}</div>
                        <button class="copy-btn" onclick="copyLatexText('fixed-{result['index']}')">복사</button>
                    </div>
                </div>
            </div>
            
            <!-- 수정된 버전 렌더링 -->
            <div class="rendered-math" id="render-{result['index']}">
                <h4 style="position: absolute; top: 10px; left: 15px; margin: 0; font-size: 14px; color: #bfdbfe;">렌더링 결과:</h4>
                <div class="zoom-controls">
                    <button class="zoom-btn" onclick="zoomOut({result['index']})">−</button>
                    <span class="zoom-level" id="zoom-level-{result['index']}">100%</span>
                    <button class="zoom-btn" onclick="zoomIn({result['index']})">+</button>
                </div>
                $${result['fixed_latex']}$$
            </div>
        </div>
    </div>
'''
    
    # Add JavaScript
    html_content += '''
    <script>
        function copyLatexText(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                // Find the button that was clicked
                const button = element.nextElementSibling;
                const originalText = button.textContent;
                button.textContent = '✓ 복사됨';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            }).catch(err => {
                console.error('복사 실패:', err);
                alert('복사 실패');
            });
        }
        
        // Zoom functionality
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
        
        function applyZoom(id, zoom) {
            const element = document.querySelector(`#render-${id} mjx-container`);
            if (element) {
                element.style.transform = `scale(${zoom / 100})`;
                element.style.transformOrigin = 'center';
            }
            document.getElementById(`zoom-level-${id}`).textContent = zoom + '%';
        }
        
        // Force white color for math
        function forceMathWhite() {
            document.querySelectorAll('.rendered-math mjx-container svg').forEach(svg => {
                svg.style.fill = 'white';
                svg.querySelectorAll('*').forEach(element => {
                    element.style.fill = 'white';
                    element.style.stroke = 'white';
                });
            });
        }
        
        // Apply white color after MathJax renders
        if (window.MathJax) {
            MathJax.startup.document.subscribe('endUpdate', forceMathWhite);
        }
        
        // Also apply on load
        window.addEventListener('load', () => {
            setTimeout(forceMathWhite, 1000);
        });
        
        // Mouse wheel zoom
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
</html>'''
    
    # Write HTML file
    html_path = output_dir / "result_viewer_fixed.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[Success] Fixed HTML viewer created: {html_path}")
    print("[*] HTML이 자동으로 MathJax를 찾아서 로드합니다!")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_fixed_viewer_v3.py <output_directory> [scale]")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    if not create_fixed_viewer(output_dir, scale):
        sys.exit(1)


if __name__ == "__main__":
    main()