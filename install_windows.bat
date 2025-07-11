@echo off
REM SmartNougat Windows Installer
REM For Windows 10/11 users

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ========================================
echo SmartNougat Windows Installer
echo ========================================
echo.

REM Check if Python is installed
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check if pip is available
echo [2/7] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed!
    echo Installing pip...
    python -m ensurepip --default-pip
)
echo.

REM Upgrade pip
echo [3/7] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install required packages
echo [4/7] Installing required packages...
echo This may take several minutes...
echo.

REM Install PyTorch (CPU version for compatibility)
echo Installing PyTorch...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo WARNING: PyTorch installation failed. Trying alternative method...
    python -m pip install torch torchvision
)
echo.

REM Install other requirements
echo Installing other dependencies...
python -m pip install -r requirements.txt
echo.

REM Download MFD model
echo [5/7] Downloading YOLO MFD model...
echo This may take a few minutes (model size: ~50MB)...
python download_mfd_model.py
if errorlevel 1 (
    echo WARNING: Model download failed. You may need to download manually later.
    echo.
)

REM Clone and install Nougat LaTeX OCR
echo [6/7] Installing Nougat LaTeX OCR...
if exist nougat-latex-ocr (
    echo Nougat LaTeX OCR already exists, skipping clone...
) else (
    echo Cloning Nougat LaTeX OCR repository...
    git clone https://github.com/NormXU/nougat-latex-ocr.git
    if errorlevel 1 (
        echo ERROR: Failed to clone Nougat LaTeX OCR
        echo Please check your internet connection and git installation
        pause
        exit /b 1
    )
)

cd nougat-latex-ocr
python -m pip install -e .
cd ..
echo.

REM Create test script
echo [7/7] Creating test script...
echo import sys > test_installation.py
echo print("Testing SmartNougat installation...") >> test_installation.py
echo try: >> test_installation.py
echo     import torch >> test_installation.py
echo     print("✓ PyTorch installed") >> test_installation.py
echo except: >> test_installation.py
echo     print("✗ PyTorch not found") >> test_installation.py
echo     sys.exit(1) >> test_installation.py
echo. >> test_installation.py
echo try: >> test_installation.py
echo     import ultralytics >> test_installation.py
echo     print("✓ Ultralytics (YOLO) installed") >> test_installation.py
echo except: >> test_installation.py
echo     print("✗ Ultralytics not found") >> test_installation.py
echo     sys.exit(1) >> test_installation.py
echo. >> test_installation.py
echo try: >> test_installation.py
echo     import fitz >> test_installation.py
echo     print("✓ PyMuPDF installed") >> test_installation.py
echo except: >> test_installation.py
echo     print("✗ PyMuPDF not found") >> test_installation.py
echo     sys.exit(1) >> test_installation.py
echo. >> test_installation.py
echo try: >> test_installation.py
echo     from transformers import AutoModel >> test_installation.py
echo     print("✓ Transformers installed") >> test_installation.py
echo except: >> test_installation.py
echo     print("✗ Transformers not found") >> test_installation.py
echo     sys.exit(1) >> test_installation.py
echo. >> test_installation.py
echo import os >> test_installation.py
echo if os.path.exists("pdf-extract-kit-models/models/MFD/YOLO/yolo_v8_ft.pt"): >> test_installation.py
echo     print("✓ YOLO MFD model found") >> test_installation.py
echo else: >> test_installation.py
echo     print("✗ YOLO MFD model not found - run download_mfd_model.py") >> test_installation.py
echo. >> test_installation.py
echo if os.path.exists("nougat-latex-ocr"): >> test_installation.py
echo     print("✓ Nougat LaTeX OCR found") >> test_installation.py
echo else: >> test_installation.py
echo     print("✗ Nougat LaTeX OCR not found") >> test_installation.py
echo. >> test_installation.py
echo print("\nInstallation test completed!") >> test_installation.py

echo.
echo ========================================
echo Running installation test...
echo ========================================
python test_installation.py
del test_installation.py

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To use SmartNougat:
echo   1. Place your PDF or DOCX file in this folder
echo   2. Run: run_smartnougat.bat yourfile.pdf
echo.
echo Example:
echo   run_smartnougat.bat document.pdf
echo   run_smartnougat.bat document.pdf 1-10
echo.
pause