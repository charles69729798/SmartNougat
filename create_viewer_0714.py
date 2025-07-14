#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create vertical layout HTML viewer with LaTeX to OMML conversion
이미지 → 원본 LaTeX → 검증된 LaTeX → OMML 형식 → 렌더링 순서로 세로 배치
"""

import json
import html
import base64
import sys
import os
import re
from pathlib import Path
from datetime import datetime


class LaTeXToOMML:
    """Convert LaTeX to Office Math Markup Language (OMML) format"""
    
    # Greek letter mappings
    GREEK_LETTERS = {
        '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
        '\\epsilon': 'ε', '\\zeta': 'ζ', '\\eta': 'η', '\\theta': 'θ',
        '\\iota': 'ι', '\\kappa': 'κ', '\\lambda': 'λ', '\\mu': 'μ',
        '\\nu': 'ν', '\\xi': 'ξ', '\\pi': 'π', '\\rho': 'ρ',
        '\\sigma': 'σ', '\\tau': 'τ', '\\upsilon': 'υ', '\\phi': 'φ',
        '\\chi': 'χ', '\\psi': 'ψ', '\\omega': 'ω',
        '\\Alpha': 'Α', '\\Beta': 'Β', '\\Gamma': 'Γ', '\\Delta': 'Δ',
        '\\Epsilon': 'Ε', '\\Zeta': 'Ζ', '\\Eta': 'Η', '\\Theta': 'Θ',
        '\\Iota': 'Ι', '\\Kappa': 'Κ', '\\Lambda': 'Λ', '\\Mu': 'Μ',
        '\\Nu': 'Ν', '\\Xi': 'Ξ', '\\Pi': 'Π', '\\Rho': 'Ρ',
        '\\Sigma': 'Σ', '\\Tau': 'Τ', '\\Upsilon': 'Υ', '\\Phi': 'Φ',
        '\\Chi': 'Χ', '\\Psi': 'Ψ', '\\Omega': 'Ω'
    }
    
    # Math symbols
    MATH_SYMBOLS = {
        '\\times': '×', '\\div': '÷', '\\pm': '±', '\\mp': '∓',
        '\\cdot': '·', '\\ast': '*', '\\star': '★', '\\circ': '∘',
        '\\bullet': '•', '\\oplus': '⊕', '\\ominus': '⊖', '\\otimes': '⊗',
        '\\oslash': '⊘', '\\odot': '⊙', '\\dagger': '†', '\\ddagger': '‡',
        '\\amalg': '⨿', '\\vee': '∨', '\\wedge': '∧', '\\cap': '∩',
        '\\cup': '∪', '\\sqcap': '⊓', '\\sqcup': '⊔', '\\uplus': '⊎'
    }
    
    # Relation symbols
    RELATION_SYMBOLS = {
        '\\leq': '≤', '\\geq': '≥', '\\neq': '≠', '\\approx': '≈',
        '\\equiv': '≡', '\\sim': '∼', '\\simeq': '≃', '\\propto': '∝',
        '\\subset': '⊂', '\\subseteq': '⊆', '\\supset': '⊃', '\\supseteq': '⊇',
        '\\in': '∈', '\\ni': '∋', '\\notin': '∉', '\\ll': '≪',
        '\\gg': '≫', '\\prec': '≺', '\\succ': '≻', '\\perp': '⊥',
        '\\parallel': '∥', '\\mid': '∣', '\\nmid': '∤'
    }
    
    # Arrow symbols
    ARROW_SYMBOLS = {
        '\\rightarrow': '→', '\\leftarrow': '←', '\\leftrightarrow': '↔',
        '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\Leftrightarrow': '⇔',
        '\\uparrow': '↑', '\\downarrow': '↓', '\\updownarrow': '↕',
        '\\nearrow': '↗', '\\searrow': '↘', '\\swarrow': '↙', '\\nwarrow': '↖',
        '\\mapsto': '↦', '\\hookrightarrow': '↪', '\\hookleftarrow': '↩'
    }
    
    # Other symbols
    OTHER_SYMBOLS = {
        '\\infty': '∞', '\\partial': '∂', '\\nabla': '∇', '\\forall': '∀',
        '\\exists': '∃', '\\nexists': '∄', '\\emptyset': '∅', '\\varnothing': '∅',
        '\\complement': '∁', '\\neg': '¬', '\\lnot': '¬', '\\land': '∧',
        '\\lor': '∨', '\\angle': '∠', '\\measuredangle': '∡', '\\sphericalangle': '∢',
        '\\prime': '′', '\\backprime': '‵', '\\ldots': '…', '\\cdots': '⋯',
        '\\vdots': '⋮', '\\ddots': '⋱', '\\therefore': '∴', '\\because': '∵',
        '\\qed': '∎', '\\blacksquare': '■', '\\square': '□', '\\triangle': '△',
        '\\bigtriangleup': '△', '\\bigtriangledown': '▽', '\\diamond': '◊',
        '\\lozenge': '◊', '\\blacklozenge': '⧫', '\\bigcirc': '○',
        '\\copyright': '©', '\\pounds': '£', '\\yen': '¥', '\\euro': '€',
        '\\section': '§', '\\paragraph': '¶', '\\dagger': '†', '\\ddagger': '‡'
    }
    
    def __init__(self):
        # Combine all symbol dictionaries
        self.all_symbols = {}
        self.all_symbols.update(self.GREEK_LETTERS)
        self.all_symbols.update(self.MATH_SYMBOLS)
        self.all_symbols.update(self.RELATION_SYMBOLS)
        self.all_symbols.update(self.ARROW_SYMBOLS)
        self.all_symbols.update(self.OTHER_SYMBOLS)
    
    def convert(self, latex):
        """Convert LaTeX to OMML format"""
        if not latex:
            return ""
        
        omml = latex
        
        # Step 1: Convert fractions
        omml = self._convert_fractions(omml)
        
        # Step 2: Convert square roots
        omml = self._convert_sqrt(omml)
        
        # Step 3: Convert superscripts and subscripts
        omml = self._convert_scripts(omml)
        
        # Step 4: Convert math functions
        omml = self._convert_functions(omml)
        
        # Step 5: Convert symbols
        omml = self._convert_symbols(omml)
        
        # Step 6: Convert matrices and arrays
        omml = self._convert_matrices(omml)
        
        # Step 7: Convert delimiters
        omml = self._convert_delimiters(omml)
        
        # Step 8: Clean up
        omml = self._cleanup(omml)
        
        return omml
    
    def _convert_fractions(self, text):
        """Convert \frac{a}{b} to (a)/(b)"""
        def replace_frac(match):
            numerator = match.group(1)
            denominator = match.group(2)
            # For simple fractions, use a/b format
            if self._is_simple(numerator) and self._is_simple(denominator):
                return f"{numerator}/{denominator}"
            # For complex fractions, use parentheses
            return f"({numerator})/({denominator})"
        
        # Handle nested braces in fractions
        pattern = r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        while '\\frac{' in text:
            old_text = text
            text = re.sub(pattern, replace_frac, text)
            if text == old_text:
                break
        
        return text
    
    def _convert_sqrt(self, text):
        """Convert \sqrt{x} to √(x) and \sqrt[n]{x} to ⁿ√(x)"""
        # Handle nth roots
        def replace_nth_root(match):
            n = match.group(1)
            x = match.group(2)
            # Convert n to superscript
            superscript_n = self._to_superscript(n)
            return f"{superscript_n}√({x})"
        
        text = re.sub(r'\\sqrt\[([^\]]+)\]\{([^}]+)\}', replace_nth_root, text)
        
        # Handle square roots
        def replace_sqrt(match):
            content = match.group(1)
            if self._is_simple(content):
                return f"√{content}"
            return f"√({content})"
        
        text = re.sub(r'\\sqrt\{([^}]+)\}', replace_sqrt, text)
        
        return text
    
    def _convert_scripts(self, text):
        """Convert superscripts and subscripts"""
        # Convert superscripts
        def replace_super(match):
            base = match.group(1) if match.group(1) else ''
            script = match.group(2)
            # Try to convert to unicode superscript
            unicode_script = self._to_superscript(script)
            if unicode_script != script:
                return f"{base}{unicode_script}"
            return f"{base}^{script}"
        
        # Match optional base followed by ^{...}
        text = re.sub(r'([a-zA-Z0-9]?)\^\{([^}]+)\}', replace_super, text)
        text = re.sub(r'([a-zA-Z0-9]?)\^([a-zA-Z0-9])', r'\1^\2', text)
        
        # Convert subscripts
        def replace_sub(match):
            base = match.group(1) if match.group(1) else ''
            script = match.group(2)
            # Try to convert to unicode subscript
            unicode_script = self._to_subscript(script)
            if unicode_script != script:
                return f"{base}{unicode_script}"
            return f"{base}_{script}"
        
        # Match optional base followed by _{...}
        text = re.sub(r'([a-zA-Z0-9]?)_\{([^}]+)\}', replace_sub, text)
        text = re.sub(r'([a-zA-Z0-9]?)_([a-zA-Z0-9])', r'\1_\2', text)
        
        return text
    
    def _convert_functions(self, text):
        """Convert math functions"""
        # Common functions that should be in roman font
        functions = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                    'sinh', 'cosh', 'tanh', 'coth',
                    'arcsin', 'arccos', 'arctan',
                    'ln', 'log', 'exp', 'det', 'dim',
                    'lim', 'sup', 'inf', 'max', 'min',
                    'gcd', 'lcm', 'deg', 'det', 'ker']
        
        for func in functions:
            # Replace \func with func
            text = text.replace(f'\\{func}', func)
            # Replace \mathrm{func} with func
            text = text.replace(f'\\mathrm{{{func}}}', func)
        
        # Special cases
        text = text.replace('\\displaystyle', '')
        text = text.replace('\\textstyle', '')
        text = text.replace('\\scriptstyle', '')
        text = text.replace('\\scriptscriptstyle', '')
        
        # Limits
        text = re.sub(r'\\lim_\{([^}]+)\}', r'lim_{\1}', text)
        
        # Sums and products
        text = re.sub(r'\\sum_\{([^}]+)\}\^\{([^}]+)\}', r'∑_{\1}^{\2}', text)
        text = re.sub(r'\\prod_\{([^}]+)\}\^\{([^}]+)\}', r'∏_{\1}^{\2}', text)
        text = re.sub(r'\\int_\{([^}]+)\}\^\{([^}]+)\}', r'∫_{\1}^{\2}', text)
        
        # Simple sum/prod/int
        text = text.replace('\\sum', '∑')
        text = text.replace('\\prod', '∏')
        text = text.replace('\\int', '∫')
        text = text.replace('\\oint', '∮')
        
        return text
    
    def _convert_symbols(self, text):
        """Convert LaTeX symbols to Unicode"""
        # Sort by length to avoid partial replacements
        sorted_symbols = sorted(self.all_symbols.items(), key=lambda x: len(x[0]), reverse=True)
        
        for latex_symbol, unicode_symbol in sorted_symbols:
            text = text.replace(latex_symbol, unicode_symbol)
        
        # Special cases
        text = text.replace('\\\\', '\n')  # Line break
        text = text.replace('\\,', ' ')    # Thin space
        text = text.replace('\\:', ' ')    # Medium space
        text = text.replace('\\;', ' ')    # Thick space
        text = text.replace('\\!', '')     # Negative thin space
        text = text.replace('\\quad', '  ') # Quad space
        text = text.replace('\\qquad', '    ') # Double quad space
        
        return text
    
    def _convert_matrices(self, text):
        """Convert matrices and arrays"""
        # Simple matrix conversion
        matrix_envs = ['matrix', 'pmatrix', 'bmatrix', 'vmatrix', 'Vmatrix']
        
        for env in matrix_envs:
            pattern = rf'\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}'
            
            def replace_matrix(match):
                content = match.group(1)
                # Convert to matrix notation
                rows = content.split('\\\\')
                formatted_rows = []
                
                for row in rows:
                    if row.strip():
                        cells = [cell.strip() for cell in row.split('&')]
                        formatted_rows.append('\t'.join(cells))
                
                matrix_content = '\n'.join(formatted_rows)
                
                # Add appropriate brackets
                if env == 'pmatrix':
                    return f"(\n{matrix_content}\n)"
                elif env == 'bmatrix':
                    return f"[\n{matrix_content}\n]"
                elif env == 'vmatrix':
                    return f"|\n{matrix_content}\n|"
                elif env == 'Vmatrix':
                    return f"||\n{matrix_content}\n||"
                else:
                    return f"\n{matrix_content}\n"
            
            text = re.sub(pattern, replace_matrix, text, flags=re.DOTALL)
        
        # Array environment
        pattern = r'\\begin\{array\}(?:\{[^}]+\})?(.*?)\\end\{array\}'
        text = re.sub(pattern, lambda m: m.group(1).replace('\\\\', '\n').replace('&', '\t'), 
                     text, flags=re.DOTALL)
        
        return text
    
    def _convert_delimiters(self, text):
        """Convert delimiter commands"""
        # Remove \left and \right
        text = text.replace('\\left', '')
        text = text.replace('\\right', '')
        
        # Convert delimiter sizes
        text = text.replace('\\big', '')
        text = text.replace('\\Big', '')
        text = text.replace('\\bigg', '')
        text = text.replace('\\Bigg', '')
        
        # Convert special delimiters
        text = text.replace('\\langle', '⟨')
        text = text.replace('\\rangle', '⟩')
        text = text.replace('\\lceil', '⌈')
        text = text.replace('\\rceil', '⌉')
        text = text.replace('\\lfloor', '⌊')
        text = text.replace('\\rfloor', '⌋')
        text = text.replace('\\|', '‖')
        
        return text
    
    def _cleanup(self, text):
        """Clean up the converted text"""
        # Remove remaining braces that are not part of subscripts/superscripts
        text = re.sub(r'(?<![\^_])\{([^}]+)\}', r'\1', text)
        
        # Remove \mathrm, \mathbf, etc.
        text = re.sub(r'\\math[a-z]+\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\text[a-z]*\{([^}]+)\}', r'\1', text)
        
        # Remove spacing commands
        text = re.sub(r'\\[hv]space\{[^}]+\}', ' ', text)
        text = re.sub(r'\\[hv]space\*?\{[^}]+\}', ' ', text)
        
        # Remove font size commands
        text = re.sub(r'\\(?:tiny|scriptsize|footnotesize|small|normalsize|large|Large|LARGE|huge|Huge)', '', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove any remaining backslashes
        text = text.replace('\\', '')
        
        return text
    
    def _is_simple(self, expr):
        """Check if expression is simple (single character or number)"""
        expr = expr.strip()
        return len(expr) <= 3 and not any(c in expr for c in ['+', '-', '*', '/', '^', '_', ' '])
    
    def _to_superscript(self, text):
        """Convert text to Unicode superscript where possible"""
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
            'n': 'ⁿ', 'i': 'ⁱ'
        }
        
        result = ''
        for char in text:
            result += superscript_map.get(char, char)
        
        return result if result != text else text
    
    def _to_subscript(self, text):
        """Convert text to Unicode subscript where possible"""
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
            '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
            'a': 'ₐ', 'e': 'ₑ', 'o': 'ₒ', 'x': 'ₓ', 'h': 'ₕ',
            'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'p': 'ₚ',
            's': 'ₛ', 't': 'ₜ'
        }
        
        result = ''
        for char in text:
            result += subscript_map.get(char, char)
        
        return result if result != text else text


def create_fixed_viewer(output_dir, scale=1.5):
    """Create HTML viewer for fixed LaTeX results with OMML conversion"""
    
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
    
    # Initialize OMML converter (현재 사용하지 않음)
    # omml_converter = LaTeXToOMML()
    
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
                
                # Convert to OMML (현재 사용하지 않음)
                # omml_text = omml_converter.convert(fixed_latex)
                
                formula_results.append({
                    'index': formula_index,
                    'page_index': page_idx,
                    'original_latex': orig_latex,
                    'fixed_latex': fixed_latex,
                    # 'omml': omml_text,
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
    <title>SmartNougat LaTeX Results with OMML</title>
    
    <!-- MathJax -->
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true
            }},
            svg: {{
                fontCache: 'global',
                scale: {scale * 0.8}
            }}
        }};
    </script>
    <script id="MathJax-script" async src="../mathjax/node_modules/mathjax/es5/tex-svg.js"></script>
    
    <style>
        body {{
            font-family: -apple-system, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .formula-card {{
            background: white;
            margin-bottom: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
            font-size: 16px;
        }}
        
        .formula-number {{
            font-weight: bold;
            color: #2563eb;
        }}
        
        .category-inline {{
            color: #10b981;
            font-weight: 500;
        }}
        
        .category-block {{
            color: #8b5cf6;
            font-weight: 500;
        }}
        
        .fixed {{
            color: #10b981;
            font-weight: 600;
        }}
        
        /* 이미지 섹션 */
        .formula-image {{
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            position: relative;
            overflow: auto;
        }}
        
        .formula-image img {{
            max-width: 100%;
            height: auto;
            display: inline-block;
            transform-origin: center;
            transition: transform 0.2s ease;
            transform: scale(1.2);
        }}
        
        .formula-image .zoom-controls {{
            background: rgba(37, 99, 235, 0.9);
        }}
        
        /* LaTeX 코드 박스 */
        .latex-box {{
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .latex-box h4 {{
            margin: 0;
            padding: 10px 15px;
            background: #f3f4f6;
            font-size: 14px;
            font-weight: 600;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .latex-code {{
            padding: 15px;
            background: #e5e7eb;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            font-weight: bold;
            color: #111827;
        }}
        
        /* 렌더링 결과 */
        .rendered-math {{
            background: #2563eb;
            padding: 32px 20px;
            border-radius: 8px;
            text-align: center;
            min-height: 80px;
            position: relative;
            color: white;
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
        
        /* 줌 컨트롤 */
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
        
        .rendered-math mjx-container {{
            color: white !important;
            max-width: 100%;
            overflow-x: auto;
        }}
        
        .rendered-math svg {{
            fill: white !important;
        }}
        
        .rendered-math svg * {{
            fill: white !important;
            stroke: white !important;
        }}
        
        /* 복사 버튼 */
        .copy-btn {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 6px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            margin: 10px 15px;
        }}
        
        .copy-btn:hover {{
            background: #1d4ed8;
        }}
        
        /* 수정 표시 */
        .status-original {{
            color: #6b7280;
        }}
        
        .status-fixed {{
            color: #10b981;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <h1>SmartNougat LaTeX Processing Results</h1>
    
    <div class="stats">
        <h2>Processing Summary</h2>
        <p>Total Formulas: <strong>{total_formulas}</strong></p>
        <p>Fixed: <strong class="fixed">{fixed_count}</strong></p>
        <p>Fix Rate: <strong>{fixed_count/total_formulas*100:.1f}%</strong></p>
    </div>
'''

    # Add each formula
    images_dir = output_dir / "images"
    
    for result in formula_results:
        # Read image file and convert to base64
        img_path = images_dir / result['filename']
        img_base64 = ""
        if img_path.exists():
            with open(img_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Extract det_idx from filename for display
        det_num = int(result['filename'].split('_')[-1].replace('.png', ''))
        
        # Determine category
        category = result.get('category_id', '')
        category_class = 'category-inline' if category == 13 else 'category-block'
        category_name = 'Inline' if category == 13 else 'Block'
        
        # Status
        status_text = '🔧 Fixed' if result['was_fixed'] else '✓ Original'
        status_class = 'status-fixed' if result['was_fixed'] else 'status-original'
        
        html_content += f'''
    <div class="formula-card">
        <!-- Header -->
        <div class="card-header">
            <div>
                <span class="formula-number">#{det_num}</span> 
                Page {result['page_index'] + 1} | 
                <span class="{category_class}">{category_name} Formula</span>
            </div>
            <span class="{status_class}">{status_text}</span>
        </div>
        
        <!-- 1. 이미지 -->
        <div class="formula-image" id="image-{result['index']}">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOutImage({result['index']})">−</button>
                <span class="zoom-level" id="image-zoom-level-{result['index']}">100%</span>
                <button class="zoom-btn" onclick="zoomInImage({result['index']})">+</button>
            </div>
            <img src="data:image/png;base64,{img_base64}" alt="{result['filename']}" id="img-{result['index']}">
        </div>
        
        <!-- 2. 원본 LaTeX -->
        <div class="latex-box">
            <h4>원본 LaTeX / Original LaTeX</h4>
            <div class="latex-code" id="original-{result['index']}">{html.escape(result['original_latex'])}</div>
            <button class="copy-btn" onclick="copyLatex('original-{result['index']}')">Copy LaTeX</button>
        </div>'''
        
        # 원본과 수정이 다른 경우에만 수정된 LaTeX 표시
        if result['was_fixed']:
            html_content += f'''
        
        <!-- 3. 수정된 LaTeX -->
        <div class="latex-box">
            <h4>수정된 LaTeX / Fixed LaTeX</h4>
            <div class="latex-code" id="fixed-{result['index']}">{html.escape(result['fixed_latex'])}</div>
            <button class="copy-btn" onclick="copyLatex('fixed-{result['index']}')">Copy LaTeX</button>
        </div>'''
        
        html_content += f'''
        
        <!-- 4. 렌더링 결과 -->
        <div class="rendered-math" id="render-{result['index']}">
            <h4>렌더링 결과 / Rendered Result</h4>
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut({result['index']})">−</button>
                <span class="zoom-level" id="zoom-level-{result['index']}">100%</span>
                <button class="zoom-btn" onclick="zoomIn({result['index']})">+</button>
            </div>
            $${result['fixed_latex']}$$
        </div>
    </div>
'''

    # Add JavaScript
    html_content += '''
    
    <script>
        // 줌 레벨 저장
        const zoomLevels = {};
        const imageZoomLevels = {};
        
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
        
        // 이미지 줌 함수
        function zoomInImage(id) {
            const current = imageZoomLevels[id] || 100;
            const newZoom = Math.min(current + 10, 300);
            imageZoomLevels[id] = newZoom;
            applyImageZoom(id, newZoom);
        }
        
        function zoomOutImage(id) {
            const current = imageZoomLevels[id] || 100;
            const newZoom = Math.max(current - 10, 50);
            imageZoomLevels[id] = newZoom;
            applyImageZoom(id, newZoom);
        }
        
        function applyImageZoom(id, zoom) {
            const element = document.getElementById(`img-${id}`);
            if (element) {
                element.style.transform = `scale(${zoom / 100})`;
            }
            document.getElementById(`image-zoom-level-${id}`).textContent = zoom + '%';
        }
        
        function copyLatex(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                const button = element.nextElementSibling;
                const originalText = button.textContent;
                button.textContent = '✓ Copied';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Copy failed:', err);
                // Fallback method
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                textArea.style.top = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    const button = element.nextElementSibling;
                    const originalText = button.textContent;
                    button.textContent = '✓ Copied';
                    setTimeout(() => {
                        button.textContent = originalText;
                    }, 2000);
                } catch (err) {
                    console.error('Fallback copy failed:', err);
                    alert('Copy failed. Please select and copy manually.');
                }
                document.body.removeChild(textArea);
            });
        }
        
        // Force white color for math
        function forceMathWhite() {
            document.querySelectorAll('.rendered-math mjx-container svg').forEach(svg => {
                svg.style.fill = 'white';
                svg.querySelectorAll('*').forEach(element => {
                    element.style.fill = 'white';
                    if (element.style.stroke && element.style.stroke !== 'none') {
                        element.style.stroke = 'white';
                    }
                });
            });
        }
        
        // Apply white color after MathJax renders
        if (window.MathJax) {
            window.MathJax.startup.promise.then(() => {
                forceMathWhite();
            });
        }
        
        // Also apply on load
        window.addEventListener('load', () => {
            setTimeout(forceMathWhite, 1000);
        });
        
        // Ctrl + 마우스 휠 줌
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
    html_path = output_dir / "result_viewer_0714.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[Success] HTML viewer with OMML created: {html_path}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_viewer_0714.py <output_directory>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    if not create_fixed_viewer(output_dir):
        sys.exit(1)


if __name__ == "__main__":
    main()