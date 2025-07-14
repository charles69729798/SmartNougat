#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create HTML viewer for fixed LaTeX results - SmartNougat compatible version
"""

import json
import html
import base64
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime


def check_and_install_mathjax():
    """Check if MathJax is installed, install if not"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Check multiple possible locations
    # Priority: output/mathjax (for easy HTML access)
    possible_paths = [
        script_dir / "output" / "mathjax" / "package" / "es5" / "tex-svg.js",
        script_dir / "output" / "mathjax" / "node_modules" / "mathjax" / "es5" / "tex-svg.js",
        script_dir / "mathjax" / "package" / "es5" / "tex-svg.js",
        script_dir / "mathjax" / "node_modules" / "mathjax" / "es5" / "tex-svg.js",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.relative_to(script_dir))
    
    # MathJax not found, try to install
    print("[!] MathJax가 설치되어 있지 않습니다. 자동 설치를 시작합니다...")
    
    # Create mathjax directory
    mathjax_dir.mkdir(exist_ok=True)
    
    # Try npm first
    npm_path = None
    for cmd in ["npm", "npm.cmd"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            npm_path = cmd
            break
        except:
            pass
    
    if npm_path:
        print("[*] npm을 사용하여 MathJax를 설치합니다...")
        try:
            # Change to mathjax directory
            os.chdir(mathjax_dir)
            
            # Initialize package.json
            subprocess.run([npm_path, "init", "-y"], capture_output=True)
            
            # Install MathJax
            result = subprocess.run([npm_path, "install", "mathjax@3"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[✓] MathJax 설치 완료!")
                # Return to original directory
                os.chdir(script_dir)
                
                # Check again
                for path in possible_paths:
                    if path.exists():
                        return str(path.relative_to(script_dir))
            else:
                print(f"[!] npm 설치 실패: {result.stderr}")
        except Exception as e:
            print(f"[!] npm 설치 중 오류: {e}")
        finally:
            os.chdir(script_dir)
    
    # Try PowerShell download as fallback
    print("[*] PowerShell을 사용하여 MathJax를 다운로드합니다...")
    try:
        ps_cmd = [
            "powershell", "-Command",
            f"Invoke-WebRequest -Uri 'https://registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz' -OutFile '{mathjax_dir}/mathjax.tgz'"
        ]
        subprocess.run(ps_cmd, check=True)
        
        # Extract using tar
        tar_cmd = ["tar", "-xzf", str(mathjax_dir / "mathjax.tgz"), "-C", str(mathjax_dir)]
        subprocess.run(tar_cmd, check=True)
        
        # Remove tgz file
        (mathjax_dir / "mathjax.tgz").unlink()
        
        print("[✓] MathJax 다운로드 및 압축 해제 완료!")
        
        # Check again
        for path in possible_paths:
            if path.exists():
                return str(path.relative_to(script_dir))
                
    except Exception as e:
        print(f"[!] PowerShell 다운로드 실패: {e}")
    
    # If all fails, return None
    print("[!] MathJax 설치에 실패했습니다. CDN을 사용합니다.")
    return None


def create_fixed_viewer(output_dir, scale=1.5, use_local_mathjax=None):
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
    
    # Determine MathJax source
    # Calculate relative path from output HTML to mathjax
    # HTML is at: output/[output_name]/result_viewer_fixed.html
    # MathJax is at: output/mathjax/package/es5/tex-svg.js
    # So we need to go up 1 level (../) to output, then to mathjax
    
    if use_local_mathjax is None:
        # Auto-detect: try local first
        local_path = check_and_install_mathjax()
        if local_path:
            # Check if it's in output/mathjax (go up 1 level)
            if local_path.startswith("output/mathjax"):
                mathjax_src = f"../{local_path.replace('output/', '').replace(os.sep, '/')}"
            else:
                # Otherwise go up 2 levels
                mathjax_src = f"../../{local_path.replace(os.sep, '/')}"
            print(f"[✓] 로컬 MathJax 사용: {local_path}")
        else:
            mathjax_src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
            print("[!] CDN MathJax 사용 (인터넷 연결 필요)")
    elif use_local_mathjax:
        # Force local
        local_path = check_and_install_mathjax()
        if local_path:
            # Check if it's in output/mathjax (go up 1 level)
            if local_path.startswith("output/mathjax"):
                mathjax_src = f"../{local_path.replace('output/', '').replace(os.sep, '/')}"
            else:
                # Otherwise go up 2 levels
                mathjax_src = f"../../{local_path.replace(os.sep, '/')}"
            print(f"[✓] 로컬 MathJax 사용: {local_path}")
        else:
            print("[!] 로컬 MathJax를 찾을 수 없어 CDN을 사용합니다.")
            mathjax_src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
    else:
        # Force CDN
        mathjax_src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
        print("[*] CDN MathJax 사용")
    
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
    <script id="MathJax-script" async src="{mathjax_src}"></script>
    
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
            position: relative;
        }}
        
        .copy-btn {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            padding: 6px 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .copy-btn:hover {{
            opacity: 1;
            background: #0056b3;
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
            background: #2563eb;
            padding: 20px;
            border-radius: 4px;
            margin-top: 10px;
            overflow-x: auto;
            overflow-y: auto;
            max-width: 100%;
            min-height: 60px;
            max-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            border: 1px solid #1d4ed8;
        }}
        
        .rendered-math .MathJax,
        .rendered-math .MathJax_Display,
        .rendered-math mjx-container,
        .rendered-math mjx-container svg,
        .rendered-math mjx-container svg g,
        .rendered-math mjx-container svg path,
        .rendered-math mjx-container svg text {{
            color: white !important;
            fill: white !important;
            stroke: white !important;
        }}
        
        .rendered-math mjx-container svg g[data-mml-node="math"] * {{
            fill: white !important;
            stroke: white !important;
        }}
        
        .math-container {{
            display: inline-block;
            transition: transform 0.2s ease;
            max-width: 100%;
            overflow: hidden;
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
        
        # Extract det_idx from filename for display
        # filename format: formula_page0_003.png -> 003
        det_num = int(result['filename'].split('_')[-1].replace('.png', ''))
        
        html_content += f'''
    <div class="formula-card">
        <div class="card-header">
            <span><strong>#{det_num}</strong> Page {result['page_index'] + 1} | <span class="{category_class}">{category_name} Formula</span></span>
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
                <div class="latex-code" id="original-{result['index']}">{html.escape(result['original_latex'])}</div>
                <button class="copy-btn" onclick="copyLatexText('original-{result['index']}')">복사</button>
            </div>'''
        
        # Fixed LaTeX box (코드만)
        fixed_label = "수정된 LaTeX / Fixed LaTeX" if result['was_fixed'] else "동일 / Same"
        html_content += f'''
            <div class="latex-box fixed">
                <h4>{fixed_label}</h4>
                <div class="latex-code" id="fixed-{result['index']}">{html.escape(result['fixed_latex'])}</div>
                <button class="copy-btn" onclick="copyLatexText('fixed-{result['index']}')">복사</button>
            </div>'''
        
        html_content += '''
        </div>
        
        <!-- 수정된 버전 렌더링 -->
        <div class="rendered-math" id="render-''' + str(result['index']) + '''">
            <h4 style="position: absolute; top: 10px; left: 15px; margin: 0; font-size: 14px; color: #bfdbfe;">렌더링 결과:</h4>
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
        
        // Copy LaTeX text to clipboard
        function copyLatexText(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent || element.innerText;
            const btn = event.target;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(function() {
                    showCopySuccess(btn);
                }).catch(function(err) {
                    fallbackCopyTextToClipboard(text, btn);
                });
            } else {
                fallbackCopyTextToClipboard(text, btn);
            }
        }
        
        // Fallback copy method for older browsers
        function fallbackCopyTextToClipboard(text, btn) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.top = "0";
            textArea.style.left = "0";
            textArea.style.position = "fixed";
            
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showCopySuccess(btn);
                } else {
                    alert('복사 실패');
                }
            } catch (err) {
                alert('복사 실패: ' + err);
            }
            
            document.body.removeChild(textArea);
        }
        
        // Show copy success feedback
        function showCopySuccess(btn) {
            const originalText = btn.textContent;
            btn.textContent = '복사완료!';
            btn.style.background = '#28a745';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '#007bff';
            }, 1500);
        }
        
        // Auto-fit math content to container width
        function autoFitMath() {
            document.querySelectorAll('.math-container').forEach((container, index) => {
                const parent = container.closest('.rendered-math');
                if (parent && container.scrollWidth > parent.clientWidth) {
                    const scale = Math.min(1, (parent.clientWidth - 40) / container.scrollWidth);
                    const id = index;
                    zoomLevels[id] = Math.round(scale * 100);
                    container.style.transform = `scale(${scale})`;
                    
                    const zoomDisplay = parent.querySelector('.zoom-level');
                    if (zoomDisplay) {
                        zoomDisplay.textContent = `${Math.round(scale * 100)}%`;
                    }
                }
            });
        }
        
        // Force white color for MathJax elements
        function forceMathWhite() {
            document.querySelectorAll('.rendered-math mjx-container svg').forEach(svg => {
                svg.style.fill = 'white';
                svg.style.color = 'white';
                svg.querySelectorAll('*').forEach(element => {
                    element.style.fill = 'white';
                    element.style.stroke = 'white';
                    element.style.color = 'white';
                });
            });
        }
        
        // Auto-fit on load
        window.addEventListener('load', () => {
            setTimeout(() => {
                autoFitMath();
                forceMathWhite();
            }, 1000); // Wait for MathJax to render
        });
        
        // Re-fit on window resize
        window.addEventListener('resize', autoFitMath);
        
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
        print("Usage: python create_fixed_viewer_v2.py <output_directory> [scale] [--local-mathjax|--cdn-mathjax]")
        print("  기본값: 로컬 MathJax 자동 감지 (없으면 자동 설치)")
        print("  --local-mathjax: 로컬 MathJax 강제 사용")
        print("  --cdn-mathjax: CDN MathJax 강제 사용")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    # Parse arguments
    scale = 1.5
    use_local_mathjax = None  # None = auto-detect
    
    for arg in sys.argv[2:]:
        if arg == "--local-mathjax":
            use_local_mathjax = True
        elif arg == "--cdn-mathjax":
            use_local_mathjax = False
        else:
            try:
                scale = float(arg)
            except ValueError:
                pass
    
    if not create_fixed_viewer(output_dir, scale, use_local_mathjax):
        sys.exit(1)


if __name__ == "__main__":
    main()