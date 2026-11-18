@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel% equ 0 (
  py -m software_fj
) else (
  python -m software_fj
)
echo.
pause
