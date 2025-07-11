@echo off
REM SmartNougat Smart Installer - 가상환경 자동 감지 설치
REM 가상환경 사용 가능하면 venv 사용, 불가능하면 일반 설치

setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cls
echo ================================================================================
echo                    SmartNougat Smart Installer
echo                   가상환경 자동 감지 설치 도구
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다!
    echo Python 3.8 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [✓] Python 설치 확인
python --version

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Git이 설치되어 있지 않습니다!
    echo Git을 설치해주세요: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [✓] Git 설치 확인
echo.

REM Clone repository if not exists
if not exist "smartnougat_standalone.py" (
    echo [1/5] SmartNougat 다운로드 중...
    if exist SmartNougat (
        cd SmartNougat
    ) else (
        git clone https://github.com/charles69729798/SmartNougat.git
        if errorlevel 1 (
            echo [오류] Git clone 실패!
            pause
            exit /b 1
        )
        cd SmartNougat
    )
) else (
    echo [1/5] SmartNougat 파일이 이미 존재합니다.
)

REM Test if venv is available
echo.
echo [2/5] 가상환경(venv) 사용 가능 여부 확인 중...
python -m venv --help >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] 가상환경을 사용할 수 없습니다.
    echo     → 일반 설치 모드로 진행합니다.
    set USE_VENV=NO
    goto :INSTALL_DEPS
)

REM Check if running in restricted environment
python -c "import venv" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] venv 모듈을 사용할 수 없습니다.
    echo     → 일반 설치 모드로 진행합니다.
    set USE_VENV=NO
    goto :INSTALL_DEPS
)

REM Try to create venv
echo [3/5] 가상환경 생성 시도 중...
if exist "smartnougat_env" (
    echo      → 기존 가상환경이 존재합니다. 사용합니다.
    set USE_VENV=YES
    goto :ACTIVATE_VENV
)

python -m venv smartnougat_env >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] 가상환경 생성 실패 (권한 또는 정책 문제)
    echo     → 일반 설치 모드로 진행합니다.
    set USE_VENV=NO
    goto :INSTALL_DEPS
)

echo [✓] 가상환경 생성 성공!
set USE_VENV=YES

:ACTIVATE_VENV
if "%USE_VENV%"=="YES" (
    echo [4/5] 가상환경 활성화 중...
    call smartnougat_env\Scripts\activate.bat
    if errorlevel 1 (
        echo [!] 가상환경 활성화 실패
        echo     → 일반 설치 모드로 전환합니다.
        set USE_VENV=NO
    ) else (
        echo [✓] 가상환경 활성화 성공!
        echo.
        echo ┌─────────────────────────────────────────┐
        echo │  🌟 가상환경 모드로 설치합니다 🌟       │
        echo │  - 시스템 Python에 영향 없음            │
        echo │  - 깔끔한 패키지 관리                   │
        echo └─────────────────────────────────────────┘
    )
) else (
    echo.
    echo ┌─────────────────────────────────────────┐
    echo │  ⚠️  일반 모드로 설치합니다 ⚠️          │
    echo │  - 시스템 Python에 직접 설치            │
    echo │  - 기존 패키지와 충돌 가능성 있음       │
    echo └─────────────────────────────────────────┘
)

:INSTALL_DEPS
echo.
echo [5/5] 패키지 설치 중... (10-20분 소요)
echo.

REM Update pip
python -m pip install --upgrade pip

REM Install PyTorch
echo [설치] PyTorch (CPU 버전)...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo [재시도] PyTorch 설치...
    python -m pip install torch torchvision torchaudio
)

REM Install other requirements
echo.
echo [설치] 기타 패키지들...
python -m pip install -r requirements.txt

REM Download MFD model
echo.
echo [다운로드] YOLO MFD 모델...
if not exist "pdf-extract-kit-models\models\MFD\YOLO\yolo_v8_ft.pt" (
    python download_mfd_model.py
)

REM Install Nougat LaTeX OCR
echo.
echo [설치] Nougat LaTeX OCR...
if not exist "nougat-latex-ocr" (
    git clone https://github.com/NormXU/nougat-latex-ocr.git
)
cd nougat-latex-ocr
python -m pip install -e .
cd ..

echo.
echo ================================================================================
echo ✅ SmartNougat 설치 완료!
echo ================================================================================
echo.

REM Create execution scripts based on venv usage
if "%USE_VENV%"=="YES" (
    REM Create venv-aware batch files
    echo @echo off > run_smartnougat.bat
    echo REM SmartNougat 실행기 (가상환경) >> run_smartnougat.bat
    echo call smartnougat_env\Scripts\activate.bat >> run_smartnougat.bat
    echo set PYTHONIOENCODING=utf-8 >> run_smartnougat.bat
    echo python smartnougat_standalone.py %%* >> run_smartnougat.bat
    echo pause >> run_smartnougat.bat
    
    echo @echo off > run_0712.bat
    echo REM SmartNougat 0712 실행기 (가상환경) >> run_0712.bat
    echo call smartnougat_env\Scripts\activate.bat >> run_0712.bat
    echo set PYTHONIOENCODING=utf-8 >> run_0712.bat
    echo python smartnougat_0712.py %%* >> run_0712.bat
    echo pause >> run_0712.bat
    
    echo 🌟 가상환경 모드 설치 완료!
    echo.
    echo 실행 방법:
    echo   - run_smartnougat.bat 파일.pdf  (기본 버전)
    echo   - run_0712.bat 파일.pdf         (LaTeX 자동 수정 버전)
    echo.
    echo 가상환경 수동 활성화:
    echo   smartnougat_env\Scripts\activate.bat
) else (
    REM Create normal batch files
    echo @echo off > run_smartnougat.bat
    echo REM SmartNougat 실행기 >> run_smartnougat.bat
    echo set PYTHONIOENCODING=utf-8 >> run_smartnougat.bat
    echo python smartnougat_standalone.py %%* >> run_smartnougat.bat
    echo pause >> run_smartnougat.bat
    
    echo @echo off > run_0712.bat
    echo REM SmartNougat 0712 실행기 >> run_0712.bat
    echo set PYTHONIOENCODING=utf-8 >> run_0712.bat
    echo python smartnougat_0712.py %%* >> run_0712.bat
    echo pause >> run_0712.bat
    
    echo ⚠️  일반 모드 설치 완료!
    echo.
    echo 실행 방법:
    echo   - run_smartnougat.bat 파일.pdf  (기본 버전)
    echo   - run_0712.bat 파일.pdf         (LaTeX 자동 수정 버전)
)

echo.
echo 설치 위치: %CD%
echo ================================================================================
echo.

REM Test installation
echo 설치 테스트 중...
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo [경고] PyTorch 설치 확인 실패
) else (
    echo [✓] PyTorch 정상
)

python -c "import ultralytics; print('YOLO: OK')" 2>nul
if errorlevel 1 (
    echo [경고] Ultralytics 설치 확인 실패
) else (
    echo [✓] YOLO 정상
)

echo.
pause