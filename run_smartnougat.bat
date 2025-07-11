@echo off
REM SmartNougat Windows Batch Script
REM Usage: run_smartnougat.bat input.pdf [page_range]

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check arguments
if "%~1"=="" (
    echo SmartNougat - Extract formulas from PDF/DOCX and convert to LaTeX
    echo.
    echo Usage: run_smartnougat.bat input_file [page_range]
    echo.
    echo Examples:
    echo   run_smartnougat.bat document.pdf
    echo   run_smartnougat.bat document.pdf 1-10
    echo   run_smartnougat.bat document.docx 5
    echo.
    pause
    exit /b 1
)

REM Set input file
set INPUT_FILE=%~1

REM Set page range if provided
if "%~2"=="" (
    set PAGE_ARGS=
) else (
    set PAGE_ARGS=-p %~2
)

REM Run SmartNougat
echo ========================================
echo SmartNougat Processing
echo ========================================
echo Input: %INPUT_FILE%
if not "%PAGE_ARGS%"=="" echo Pages: %~2
echo ========================================
echo.

python smartnougat_standalone.py "%INPUT_FILE%" %PAGE_ARGS%

echo.
echo ========================================
echo Processing Complete
echo ========================================
pause