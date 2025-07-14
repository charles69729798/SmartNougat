@echo off
REM SmartNougat GUI 실행기

set PYTHONIOENCODING=utf-8
chcp 65001 >nul

echo SmartNougat GUI를 시작합니다...
python smartnougat_gui.py

if errorlevel 1 (
    echo.
    echo GUI 실행 중 오류가 발생했습니다.
    echo Python과 필요한 패키지가 설치되어 있는지 확인하세요.
    pause
)