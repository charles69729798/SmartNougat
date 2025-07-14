@echo off
echo MathJax를 출력 폴더에 복사합니다...
echo.

REM 현재 스크립트 위치
set SCRIPT_DIR=%~dp0

REM MathJax가 있는지 확인
if not exist "%SCRIPT_DIR%mathjax" (
    echo [오류] MathJax가 설치되지 않았습니다!
    echo        먼저 download_mathjax.bat을 실행하세요.
    pause
    exit /b 1
)

REM 대상 폴더 입력
set /p OUTPUT_DIR="출력 폴더 경로를 입력하세요 (예: C:\git\mineru-latex-converter\output\1_1_smartnougat_*): "

REM 폴더 존재 확인
if not exist "%OUTPUT_DIR%" (
    echo [오류] 폴더를 찾을 수 없습니다: %OUTPUT_DIR%
    pause
    exit /b 1
)

REM MathJax 복사
echo 복사 중...
xcopy /E /I /Y "%SCRIPT_DIR%mathjax" "%OUTPUT_DIR%\mathjax"

echo.
echo ✅ 완료! 이제 HTML 파일에서 오프라인으로 수식을 볼 수 있습니다.
pause