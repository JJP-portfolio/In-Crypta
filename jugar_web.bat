@echo off
setlocal enabledelayedexpansion
title IN CRYPTA - Web Runtime (Windows)

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "PYTHON_EXE="
set "PYTHON_ARG="

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    "%SCRIPT_DIR%.venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
        set "PYTHON_ARG="
        goto :python_ok
    )
)

where py >nul 2>nul
if !errorlevel! equ 0 (
    py -3 -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARG=-3"
        goto :python_ok
    )
    py -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
        goto :python_ok
    )
)

where python >nul 2>nul
if !errorlevel! equ 0 (
    python -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
        goto :python_ok
    )
)

for %%V in (314 313 312 311 310 39) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :python_ok
    )
    if exist "%ProgramFiles%\Python%%V\python.exe" (
        set "PYTHON_EXE=%ProgramFiles%\Python%%V\python.exe"
        goto :python_ok
    )
)

echo [ERROR] No se encontro Python para iniciar el servidor web local.
pause
exit /b 1

:python_ok
echo ========================================================
echo   IN CRYPTA 1.0.0 - Plataforma Web (GDevelop JS / PixiJS)
echo ========================================================
echo   Abriendo navegador en http://localhost:8000/export/gdevelop/index.html ...
echo   Para cerrar el servidor, presiona Ctrl+C en esta ventana.
echo ========================================================

start http://localhost:8000/export/gdevelop/index.html
"%PYTHON_EXE%" %PYTHON_ARG% -m http.server 8000
