# SmartNougat Installation Guide (Windows 10/11)

## Prerequisites

### 1. Python Installation
- Open Command Prompt (cmd)
- Type `python --version`
- Python 3.8 or higher required
- Download from https://www.python.org/downloads/ if not installed
- **IMPORTANT**: Check "Add Python to PATH" during installation!

### 2. Git Installation
- Type `git --version` in Command Prompt
- Download from https://git-scm.com/download/win if not installed

## Installation

### Method 1: Automatic Installation (Recommended)

1. **Clone Repository**
   ```cmd
   git clone https://github.com/charles69729798/SmartNougat.git
   cd SmartNougat
   ```

2. **Run Installation Script**
   ```cmd
   install_windows.bat
   ```
   - Automatically installs all required packages
   - Takes approximately 5-10 minutes

3. **Verify Installation**
   - Installation test runs automatically
   - All items should show ✓ for success

### Method 2: Manual Installation

1. **Clone Repository**
   ```cmd
   git clone https://github.com/charles69729798/SmartNougat.git
   cd SmartNougat
   ```

2. **Install Packages**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Install Nougat LaTeX OCR**
   ```cmd
   git clone https://github.com/NormXU/nougat-latex-ocr.git
   cd nougat-latex-ocr
   pip install -e .
   cd ..
   ```

4. **Download YOLO MFD Model**
   ```cmd
   python download_mfd_model.py
   ```

## Usage

### Basic Usage
```cmd
run_smartnougat.bat document.pdf
```

### Specify Pages
```cmd
run_smartnougat.bat document.pdf 1-10
```

### Process DOCX Files
```cmd
run_smartnougat.bat document.docx
```

## Troubleshooting

### Python Not Found Error
1. Verify Python is added to PATH
2. Check system environment variables
3. Reinstall Python with PATH option checked

### pip Errors
```cmd
python -m ensurepip --default-pip
python -m pip install --upgrade pip
```

### Character Encoding Issues
```cmd
set PYTHONIOENCODING=utf-8
chcp 65001
```

### CUDA/GPU Errors
- CPU version is installed by default
- Install CUDA for GPU support

## Output Files

After processing, the following files are created:
- `output_filename_timestamp/` folder
  - `layout.pdf` - PDF with formula boxes highlighted
  - `result_viewer.html` - Interactive result viewer
  - `txt/output.md` - Extracted text with formulas
  - `images/` - Extracted formula images

## Support

For issues, please visit:
https://github.com/charles69729798/SmartNougat/issues