@echo off
REM SmartNougat Complete Windows Installer
REM Installs Python and all dependencies automatically
REM Requires: Windows 10/11, MS Office installed

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ================================================================================
echo SmartNougat Complete Windows Installer
echo ================================================================================
echo This will install:
echo - Python 3.11 (if not installed)
echo - Git for Windows (if not installed)
echo - All SmartNougat dependencies
echo - YOLO MFD model
echo - Nougat LaTeX OCR
echo.
echo Requirements: Windows 10/11, MS Office installed
echo ================================================================================
echo.
pause

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as administrator.
    echo Some installations may require admin privileges.
    echo.
)

REM Create temp directory for downloads
set TEMP_DIR=%TEMP%\SmartNougat_Install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Check Python installation
echo [Step 1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Installing Python 3.11...
    echo.
    
    REM Download Python installer
    echo Downloading Python 3.11 installer...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP_DIR%\python_installer.exe'}"
    
    if not exist "%TEMP_DIR%\python_installer.exe" (
        echo ERROR: Failed to download Python installer.
        echo Please install Python manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    REM Install Python silently
    echo Installing Python 3.11...
    "%TEMP_DIR%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_launcher=1
    
    REM Wait for installation
    timeout /t 10 /nobreak >nul
    
    REM Refresh PATH
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
    set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
    
    REM Verify installation
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python installation failed.
        echo Please install Python manually with "Add to PATH" option.
        pause
        exit /b 1
    )
    echo Python installed successfully!
) else (
    python --version
    echo Python is already installed.
)
echo.

REM Check Git installation
echo [Step 2/8] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo Git not found. Installing Git for Windows...
    echo.
    
    REM Download Git installer
    echo Downloading Git installer...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe' -OutFile '%TEMP_DIR%\git_installer.exe'}"
    
    if not exist "%TEMP_DIR%\git_installer.exe" (
        echo ERROR: Failed to download Git installer.
        echo Please install Git manually from https://git-scm.com/download/win
        pause
        exit /b 1
    )
    
    REM Install Git silently
    echo Installing Git...
    "%TEMP_DIR%\git_installer.exe" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
    
    REM Wait for installation
    timeout /t 10 /nobreak >nul
    
    REM Refresh PATH
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
    
    REM Verify installation
    git --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Git installation failed.
        echo Please install Git manually.
        pause
        exit /b 1
    )
    echo Git installed successfully!
) else (
    git --version
    echo Git is already installed.
)
echo.

REM Check MS Office (Word)
echo [Step 3/8] Checking MS Office installation...
powershell -Command "& {try { $word = New-Object -ComObject Word.Application; $word.Quit(); Write-Host 'MS Word found.'; exit 0 } catch { Write-Host 'MS Word not found!'; exit 1 }}"
if errorlevel 1 (
    echo WARNING: MS Word not detected. DOCX conversion will not work.
    echo Please ensure MS Office is installed for DOCX support.
    echo.
    pause
)
echo.

REM Update pip
echo [Step 4/8] Updating pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Installing pip...
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
)
echo.

REM Install Visual C++ Redistributable (required for some packages)
echo [Step 5/8] Checking Visual C++ Redistributable...
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if errorlevel 1 (
    echo Downloading Visual C++ Redistributable...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%TEMP_DIR%\vc_redist.x64.exe'}"
    
    if exist "%TEMP_DIR%\vc_redist.x64.exe" (
        echo Installing Visual C++ Redistributable...
        "%TEMP_DIR%\vc_redist.x64.exe" /quiet /norestart
        timeout /t 5 /nobreak >nul
    )
) else (
    echo Visual C++ Redistributable is already installed.
)
echo.

REM Install Python packages
echo [Step 6/8] Installing Python packages...
echo This may take 10-20 minutes depending on your internet speed...
echo.

REM Install PyTorch first (CPU version for compatibility)
echo Installing PyTorch (CPU version)...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo Trying alternative PyTorch installation...
    python -m pip install torch torchvision torchaudio
)
echo.

REM Install other core packages
echo Installing core packages...
python -m pip install transformers>=4.30.0
python -m pip install ultralytics>=8.0.0
python -m pip install PyMuPDF>=1.23.0
python -m pip install loguru>=0.7.0
python -m pip install Pillow>=10.0.0
python -m pip install numpy>=1.24.0
python -m pip install opencv-python>=4.8.0
python -m pip install huggingface-hub>=0.16.0
python -m pip install sentencepiece>=0.1.99
python -m pip install protobuf>=3.20.0
echo.

REM Install Windows-specific packages
echo Installing Windows-specific packages...
python -m pip install pywin32>=305
python -m pip install docx2pdf>=0.1.8
echo.

REM Install optional packages
echo Installing optional packages...
python -m pip install paddlepaddle>=2.5.0 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
python -m pip install paddleocr>=2.7.0
echo.

REM Clone SmartNougat if not in SmartNougat directory
if not exist "smartnougat_standalone.py" (
    echo [Step 7/8] Cloning SmartNougat repository...
    git clone https://github.com/charles69729798/SmartNougat.git SmartNougat_temp
    xcopy SmartNougat_temp\* . /E /Y >nul
    rmdir /S /Q SmartNougat_temp
) else (
    echo [Step 7/8] SmartNougat files found.
)
echo.

REM Download MFD model
echo [Step 8/8] Downloading YOLO MFD model...
if not exist "pdf-extract-kit-models\models\MFD\YOLO\yolo_v8_ft.pt" (
    python download_mfd_model.py
    if errorlevel 1 (
        echo WARNING: Model download failed. Trying alternative method...
        
        REM Alternative download using PowerShell
        echo Creating model directory...
        if not exist "pdf-extract-kit-models\models\MFD\YOLO" mkdir "pdf-extract-kit-models\models\MFD\YOLO"
        
        echo Downloading model file directly...
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://huggingface.co/opendatalab/pdf-extract-kit-1.0/resolve/main/models/MFD/YOLO/yolo_v8_ft.pt' -OutFile 'pdf-extract-kit-models\models\MFD\YOLO\yolo_v8_ft.pt' } catch { Write-Host 'Download failed' }}"
    )
) else (
    echo YOLO MFD model already exists.
)
echo.

REM Install Nougat LaTeX OCR
echo Installing Nougat LaTeX OCR...
if not exist "nougat-latex-ocr" (
    git clone https://github.com/Norm/nougat-latex-ocr.git
    if errorlevel 1 (
        echo ERROR: Failed to clone Nougat LaTeX OCR
        echo Please check your internet connection
        pause
        exit /b 1
    )
)
cd nougat-latex-ocr
python -m pip install -e .
cd ..
echo.

REM Create test script
echo Creating test script...
python -c "print('import sys'); print('import os'); print('errors = 0'); print(''); print('print(\"=\"*60)'); print('print(\"SmartNougat Installation Test\")'); print('print(\"=\"*60)'); print(''); print('try:'); print('    import torch'); print('    print(\"✓ PyTorch installed - Version:\", torch.__version__)'); print('except Exception as e:'); print('    print(\"✗ PyTorch not found:\", str(e))'); print('    errors += 1'); print(''); print('try:'); print('    import ultralytics'); print('    print(\"✓ Ultralytics (YOLO) installed\")'); print('except Exception as e:'); print('    print(\"✗ Ultralytics not found:\", str(e))'); print('    errors += 1'); print(''); print('try:'); print('    import fitz'); print('    print(\"✓ PyMuPDF installed - Version:\", fitz.version)'); print('except Exception as e:'); print('    print(\"✗ PyMuPDF not found:\", str(e))'); print('    errors += 1'); print(''); print('try:'); print('    from transformers import AutoModel'); print('    print(\"✓ Transformers installed\")'); print('except Exception as e:'); print('    print(\"✗ Transformers not found:\", str(e))'); print('    errors += 1'); print(''); print('try:'); print('    import win32com.client'); print('    print(\"✓ pywin32 installed (for DOCX support)\")'); print('except Exception as e:'); print('    print(\"✗ pywin32 not found:\", str(e))'); print('    errors += 1'); print(''); print('try:'); print('    import paddle'); print('    print(\"✓ PaddlePaddle installed (optional OCR)\")'); print('except Exception as e:'); print('    print(\"⚠ PaddlePaddle not found (optional):\", str(e))'); print(''); print('if os.path.exists(\"pdf-extract-kit-models/models/MFD/YOLO/yolo_v8_ft.pt\"):'); print('    print(\"✓ YOLO MFD model found\")'); print('else:'); print('    print(\"✗ YOLO MFD model not found\")'); print('    errors += 1'); print(''); print('if os.path.exists(\"nougat-latex-ocr\"):'); print('    print(\"✓ Nougat LaTeX OCR found\")'); print('else:'); print('    print(\"✗ Nougat LaTeX OCR not found\")'); print('    errors += 1'); print(''); print('print(\"=\"*60)'); print('if errors == 0:'); print('    print(\"✓ All components installed successfully!\")'); print('else:'); print('    print(f\"✗ {errors} component(s) failed to install\")'); print('    sys.exit(1)')" > test_install.py

python test_install.py
set TEST_RESULT=%errorlevel%
del test_install.py

REM Clean up temp directory
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%"

echo.
echo ================================================================================
if %TEST_RESULT% equ 0 (
    echo ✓ SmartNougat Installation Complete!
    echo ================================================================================
    echo.
    echo Quick Start:
    echo 1. Place your PDF or DOCX file in this folder
    echo 2. Run: run_smartnougat.bat yourfile.pdf
    echo.
    echo Examples:
    echo   run_smartnougat.bat document.pdf
    echo   run_smartnougat.bat document.pdf 1-10
    echo   run_smartnougat.bat report.docx
    echo.
    echo For Korean text: Make sure to use UTF-8 encoding
    echo   set PYTHONIOENCODING=utf-8
) else (
    echo ✗ Installation completed with errors
    echo ================================================================================
    echo.
    echo Please check the error messages above and try:
    echo 1. Run this installer as Administrator
    echo 2. Check your internet connection
    echo 3. Manually install failed components
    echo.
    echo For help, visit: https://github.com/charles69729798/SmartNougat/issues
)
echo.
pause