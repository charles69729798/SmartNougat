@echo off
REM SmartNougat 다운로드 및 설치 스크립트
REM 이 파일을 원하는 위치에 저장하고 실행하세요

echo SmartNougat 자동 설치를 시작합니다...
echo.

REM PowerShell로 quick_install_and_run.bat 다운로드 및 실행
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/charles69729798/SmartNougat/main/quick_install_and_run.bat' -OutFile 'quick_install_and_run.bat'; if($?) { Write-Host '다운로드 완료!' -ForegroundColor Green; Start-Process 'quick_install_and_run.bat' -Verb RunAs } else { Write-Host '다운로드 실패!' -ForegroundColor Red; pause }}"