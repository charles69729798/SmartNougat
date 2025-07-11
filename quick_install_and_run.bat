@echo off
REM SmartNougat Quick Install and Run
REM Git clone + install + ready to use

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cls
echo ================================================================================
echo                    SmartNougat Quick Install and Run
echo                         원클릭 설치 및 실행 도구
echo ================================================================================
echo.
echo 이 스크립트는 다음 작업을 자동으로 수행합니다:
echo 1. Git을 사용하여 SmartNougat 다운로드
echo 2. 모든 의존성 자동 설치
echo 3. 사용 준비 완료
echo.
echo 설치 위치: %CD%\SmartNougat
echo ================================================================================
echo.
pause

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Git이 설치되어 있지 않습니다!
    echo.
    echo Git을 먼저 설치해주세요:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Python이 설치되어 있지 않습니다!
    echo.
    echo Python 3.8 이상을 설치해주세요:
    echo https://www.python.org/downloads/
    echo.
    echo 중요: "Add Python to PATH" 옵션을 반드시 체크하세요!
    echo.
    pause
    exit /b 1
)

echo [1/4] Git과 Python이 설치되어 있습니다.
echo.

REM Clone repository
echo [2/4] SmartNougat 다운로드 중...
if exist SmartNougat (
    echo.
    echo SmartNougat 폴더가 이미 존재합니다.
    echo 삭제하고 새로 다운로드하시겠습니까? (Y/N)
    set /p delete_choice="선택: "
    if /i "!delete_choice!"=="Y" (
        echo 기존 폴더 삭제 중...
        rmdir /S /Q SmartNougat
    ) else (
        echo 기존 폴더를 사용합니다.
        goto :ENTER_FOLDER
    )
)

git clone https://github.com/charles69729798/SmartNougat.git
if errorlevel 1 (
    echo.
    echo [오류] Git clone 실패!
    echo 인터넷 연결을 확인하세요.
    pause
    exit /b 1
)

:ENTER_FOLDER
cd SmartNougat
echo.
echo [3/4] SmartNougat 폴더로 이동 완료
echo.

REM Install dependencies
echo [4/4] 의존성 설치 중... (10-20분 소요)
echo.

REM Check if already installed
if exist "pdf-extract-kit-models\models\MFD\YOLO\yolo_v8_ft.pt" (
    if exist "nougat-latex-ocr" (
        echo 이미 설치되어 있습니다!
        goto :CREATE_SHORTCUTS
    )
)

REM Run full installation
call install_all_windows.bat
if errorlevel 1 (
    echo.
    echo [오류] 설치 중 문제가 발생했습니다.
    echo install_all_windows.bat을 직접 실행해보세요.
    pause
    exit /b 1
)

:CREATE_SHORTCUTS
echo.
echo ================================================================================
echo ✅ SmartNougat 설치 완료!
echo ================================================================================
echo.

REM Create convenient batch files
echo 편의 실행 파일 생성 중...

REM Create run_0712.bat for the enhanced version
echo @echo off > run_0712.bat
echo REM SmartNougat 0712 - LaTeX 자동 수정 버전 >> run_0712.bat
echo set PYTHONIOENCODING=utf-8 >> run_0712.bat
echo chcp 65001 ^>nul >> run_0712.bat
echo. >> run_0712.bat
echo if "%%~1"=="" ( >> run_0712.bat
echo     echo SmartNougat 0712 - LaTeX 자동 수정 버전 >> run_0712.bat
echo     echo. >> run_0712.bat
echo     echo 사용법: run_0712.bat 파일.pdf [페이지범위] >> run_0712.bat
echo     echo. >> run_0712.bat
echo     echo 예시: >> run_0712.bat
echo     echo   run_0712.bat document.pdf >> run_0712.bat
echo     echo   run_0712.bat document.pdf 1-10 >> run_0712.bat
echo     echo   run_0712.bat "C:\문서\파일.pdf" >> run_0712.bat
echo     echo. >> run_0712.bat
echo     echo 특징: LaTeX 문법 자동 수정 후 별도 파일 생성 >> run_0712.bat
echo     echo   - model_fixed.json >> run_0712.bat
echo     echo   - output_fixed.md >> run_0712.bat
echo     echo   - result_viewer_fixed.html >> run_0712.bat
echo     echo. >> run_0712.bat
echo     pause >> run_0712.bat
echo     exit /b >> run_0712.bat
echo ^) >> run_0712.bat
echo. >> run_0712.bat
echo python smartnougat_0712.py %%* >> run_0712.bat
echo pause >> run_0712.bat

echo ✅ run_0712.bat 생성 완료
echo.

REM Show usage instructions
echo ================================================================================
echo 사용 방법:
echo ================================================================================
echo.
echo 1. 기본 버전 (원본만):
echo    run_smartnougat.bat 파일.pdf
echo.
echo 2. 향상된 버전 (원본 + LaTeX 자동 수정):
echo    run_0712.bat 파일.pdf
echo.
echo 3. 직접 실행:
echo    python smartnougat_standalone.py 파일.pdf
echo    python smartnougat_0712.py 파일.pdf
echo.
echo 현재 위치: %CD%
echo ================================================================================
echo.

REM Ask if user wants to process a file now
echo 지금 파일을 처리하시겠습니까? (Y/N)
set /p process_now="선택: "

if /i "!process_now!"=="Y" (
    echo.
    echo PDF 또는 DOCX 파일의 전체 경로를 입력하세요:
    echo (예: C:\Documents\paper.pdf)
    set /p file_path="파일 경로: "
    
    if exist "!file_path!" (
        echo.
        echo 어떤 버전을 사용하시겠습니까?
        echo [1] 기본 버전 (빠름)
        echo [2] LaTeX 자동 수정 버전 (권장)
        set /p version_choice="선택 (1 또는 2): "
        
        if "!version_choice!"=="2" (
            echo.
            echo LaTeX 자동 수정 버전으로 처리 중...
            python smartnougat_0712.py "!file_path!"
        ) else (
            echo.
            echo 기본 버전으로 처리 중...
            python smartnougat_standalone.py "!file_path!"
        )
    ) else (
        echo.
        echo [오류] 파일을 찾을 수 없습니다: !file_path!
    )
)

echo.
pause