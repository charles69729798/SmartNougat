@echo off
REM Test OMML conversion feature

set PYTHONIOENCODING=utf-8
chcp 65001 >nul

echo Testing SmartNougat with OMML conversion...
echo.

REM Test with sample file
python smartnougat_0712.py "C:\test\1_1.docx" -p 1-2

echo.
echo Check the result_viewer_0714.html file for OMML format!
pause