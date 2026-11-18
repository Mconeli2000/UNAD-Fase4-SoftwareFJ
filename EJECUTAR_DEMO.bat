@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel% equ 0 (
  py -m software_fj --demo
) else (
  python -m software_fj --demo
)
echo.
pause
