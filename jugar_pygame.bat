@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%jugar_windows.bat" %*
exit /b %errorlevel%
