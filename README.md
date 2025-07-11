# SmartNougat

Standalone document processing with Nougat - Extract formulas from PDF/DOCX and convert to LaTeX

## Overview

SmartNougat is a powerful document processing tool that extracts mathematical formulas from PDF and DOCX files and converts them to LaTeX format. It uses state-of-the-art deep learning models for formula detection and recognition.

## Features

- 📄 **PDF/DOCX Support**: Process both PDF and Word documents
- 🔍 **Formula Detection**: YOLO-based mathematical formula detection
- 🧮 **LaTeX Conversion**: Accurate formula recognition using Nougat
- 🇰🇷 **Korean Text Support**: Full support for Korean language
- 📊 **Layout Visualization**: Generate PDF with highlighted formulas
- 🌐 **HTML Viewer**: Interactive result viewer with MathJax rendering

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-capable GPU (optional, for faster processing)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Nougat LaTeX OCR
```bash
git clone https://github.com/Norm/nougat-latex-ocr.git
cd nougat-latex-ocr
pip install -e .
```

### Step 3: Download MFD Model
```python
python download_mfd_model.py
```

## Usage

### Basic Usage
```bash
python smartnougat_standalone.py input.pdf
```

### With Options
```bash
# Process specific pages
python smartnougat_standalone.py input.pdf -p 1-10

# Custom output directory
python smartnougat_standalone.py input.pdf -o ./results

# Use GPU
python smartnougat_standalone.py input.pdf --device cuda
```

### Page Range Options
- Single page: `-p 5`
- Range: `-p 1-10`
- Multiple pages: `-p 1,3,5`
- From beginning: `-p :10`
- To end: `-p 10:`

## Output Structure

```
output_directory/
├── input.pdf              # Original PDF (if from DOCX)
├── input_pages_1-10.pdf   # Extracted pages
├── layout.pdf             # Visualization with formula boxes
├── images/                # Extracted formula images
│   └── formula_page0_000.png
├── pages/                 # Page images
├── txt/
│   ├── model.json        # Formula locations and LaTeX
│   ├── middle.json       # Processing metadata
│   └── output.md         # Extracted text with formulas
├── result_viewer.html    # Interactive viewer
└── processing_summary.json
```

## Examples

### Windows Batch Script
```batch
@echo off
set PYTHONIOENCODING=utf-8
python smartnougat_standalone.py "C:\documents\paper.pdf" -p 1-5
```

### Process DOCX File
```bash
python smartnougat_standalone.py document.docx -p 10-20
```

## Performance

- **Processing Speed**: ~60-90 seconds per page (CPU)
- **Formula Detection**: 0.3-0.9 confidence score
- **Memory Usage**: Automatic cache management every 5 pages

## Technical Details

### Models Used
- **Formula Detection**: YOLO v8 (PDF-Extract-Kit)
- **Formula Recognition**: Nougat (Facebook Research)
- **Text Extraction**: PyMuPDF
- **OCR (Optional)**: PaddleOCR

### Formula Categories
- Category 13: Inline formulas (blue boxes in layout.pdf)
- Category 14: Block formulas (red boxes in layout.pdf)

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```bash
   python smartnougat_standalone.py input.pdf --device cpu
   ```

2. **Korean Text Not Displayed**
   ```bash
   set PYTHONIOENCODING=utf-8  # Windows
   export PYTHONIOENCODING=utf-8  # Linux/Mac
   ```

3. **MFD Model Not Found**
   ```bash
   python download_mfd_model.py
   ```

## License

This project uses the following open-source components:
- Nougat: MIT License
- YOLO: AGPL-3.0 License
- PyMuPDF: AGPL-3.0 License

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- [Nougat](https://github.com/facebookresearch/nougat) by Facebook Research
- [PDF-Extract-Kit](https://github.com/opendatalab/PDF-Extract-Kit) for the MFD model
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing