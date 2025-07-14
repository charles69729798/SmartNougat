@echo off
echo [MathJax 로컬 다운로드]
echo.
echo Node.js가 필요 없습니다! 순수 JavaScript 라이브러리입니다.
echo.

REM 스크립트 위치로 이동
cd /d "%~dp0"

REM MathJax 폴더 확인
if exist "mathjax\package\es5\tex-svg.js" (
    echo ✓ MathJax가 이미 설치되어 있습니다!
    echo   위치: mathjax\package\es5\tex-svg.js
    pause
    exit /b 0
)

REM MathJax 폴더 생성
if not exist "mathjax" mkdir mathjax

echo 다운로드 중... (약 15MB)
echo.

REM PowerShell로 다운로드 (Windows 기본 포함)
echo PowerShell을 사용하여 다운로드합니다...
powershell -Command "& {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz' -OutFile 'mathjax\mathjax.tgz'}"

if not exist "mathjax\mathjax.tgz" (
    echo.
    echo [오류] 다운로드 실패! 인터넷 연결을 확인하세요.
    pause
    exit /b 1
)

echo 압축 해제 중...

REM tar로 압축 해제 (Windows 10 1803 이상 기본 포함)
cd mathjax
tar -xzf mathjax.tgz
del mathjax.tgz
cd ..

echo.
echo ================================================================================
echo ✅ MathJax 설치 완료!
echo ================================================================================
echo.
echo 위치: mathjax\package\es5\tex-svg.js
echo.
echo 이제 오프라인에서도 LaTeX 수식을 렌더링할 수 있습니다.
echo Node.js 설치 필요 없음!
echo.
pause