@echo off
REM SmartNougat - Start Here!
REM One-click installer and launcher

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  SmartNougat - PDF/DOCX to LaTeX               ║
echo ║                     수식 추출 및 LaTeX 변환 도구                 ║
echo ╔════════════════════════════════════════════════════════════════╝
echo.

REM Check if first run (no installation)
if not exist "pdf-extract-kit-models\models\MFD\YOLO\yolo_v8_ft.pt" goto :FIRST_RUN
if not exist "nougat-latex-ocr" goto :FIRST_RUN

REM Already installed - show menu
:MAIN_MENU
echo 설치가 완료되었습니다! / Installation complete!
echo.
echo 선택하세요 / Choose an option:
echo.
echo [1] PDF/DOCX 파일 처리 / Process PDF/DOCX file
echo [2] 설치 상태 확인 / Check installation status
echo [3] 설치 가이드 보기 / View installation guide
echo [4] 종료 / Exit
echo.
set /p choice="선택 / Select (1-4): "

if "%choice%"=="1" goto :PROCESS_FILE
if "%choice%"=="2" goto :CHECK_STATUS
if "%choice%"=="3" goto :VIEW_GUIDE
if "%choice%"=="4" exit /b 0
goto :MAIN_MENU

:FIRST_RUN
echo 처음 실행하시는군요! / First time running!
echo SmartNougat을 설치해야 합니다. / Need to install SmartNougat.
echo.
echo 설치를 시작하시겠습니까? / Start installation?
echo [Y] 예, 설치합니다 / Yes, install
echo [N] 아니오, 나중에 / No, later
echo.
set /p install="선택 / Select (Y/N): "

if /i "%install%"=="Y" (
    echo.
    echo 설치를 시작합니다... / Starting installation...
    call install_all_windows.bat
    echo.
    pause
    cls
    goto :MAIN_MENU
) else (
    echo.
    echo 나중에 다시 실행해주세요. / Please run again later.
    pause
    exit /b 0
)

:PROCESS_FILE
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    파일 처리 / Process File                     ║
echo ╔════════════════════════════════════════════════════════════════╝
echo.
echo 처리할 파일을 이 창에 끌어다 놓고 Enter를 누르세요.
echo Drag and drop your file here and press Enter.
echo.
echo 또는 파일 경로를 입력하세요 / Or type file path:
echo (예시 / Example: C:\Documents\paper.pdf)
echo.
set /p filepath="파일 경로 / File path: "

REM Remove quotes if present
set filepath=%filepath:"=%

if not exist "%filepath%" (
    echo.
    echo 파일을 찾을 수 없습니다! / File not found!
    echo.
    pause
    goto :MAIN_MENU
)

echo.
echo 페이지 범위를 입력하세요 (선택사항) / Enter page range (optional):
echo 예시 / Examples: 1-10, 5, :10, 10:
echo 전체 처리는 Enter만 누르세요 / Press Enter for all pages
echo.
set /p pages="페이지 / Pages: "

echo.
echo 처리 중... / Processing...
echo.

if "%pages%"=="" (
    python smartnougat_standalone.py "%filepath%"
) else (
    python smartnougat_standalone.py "%filepath%" -p %pages%
)

echo.
echo 처리 완료! / Processing complete!
echo 결과는 output 폴더를 확인하세요. / Check output folder for results.
echo.
pause
goto :MAIN_MENU

:CHECK_STATUS
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  설치 상태 확인 / Check Status                  ║
echo ╔════════════════════════════════════════════════════════════════╝
echo.

python -c "import sys; import os; print('Python Version:', sys.version.split()[0]); import torch; print('PyTorch:', torch.__version__); import ultralytics; print('YOLO: OK'); import fitz; print('PyMuPDF:', fitz.version); from transformers import AutoModel; print('Transformers: OK'); import win32com.client; print('pywin32: OK'); model_exists = os.path.exists('pdf-extract-kit-models/models/MFD/YOLO/yolo_v8_ft.pt'); print('YOLO Model:', 'Found' if model_exists else 'Not Found'); nougat_exists = os.path.exists('nougat-latex-ocr'); print('Nougat OCR:', 'Found' if nougat_exists else 'Not Found')" 2>nul

if errorlevel 1 (
    echo.
    echo 일부 구성 요소가 설치되지 않았습니다. / Some components are not installed.
    echo install_all_windows.bat을 실행하세요. / Run install_all_windows.bat
)

echo.
pause
goto :MAIN_MENU

:VIEW_GUIDE
cls
if exist "INSTALL_GUIDE_KR.md" (
    type INSTALL_GUIDE_KR.md | more
) else if exist "INSTALL_GUIDE.md" (
    type INSTALL_GUIDE.md | more
) else (
    echo 설치 가이드를 찾을 수 없습니다. / Installation guide not found.
)
echo.
pause
goto :MAIN_MENU