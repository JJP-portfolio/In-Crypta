@echo off
setlocal enabledelayedexpansion
title IN CRYPTA - Versión Desktop (Windows)

:: Obtener directorio del script y fijar como directorio de trabajo
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Configurar PYTHONPATH para priorizar módulos locales
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

echo ========================================================
echo   IN CRYPTA 1.0.0 - Version Desktop (Windows)
echo ========================================================
echo   Directorio : %SCRIPT_DIR%

:: 1. Autodeteccion del interprete Python del sistema
set "PYTHON_SYS="
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_SYS=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_SYS=py -3"
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_SYS=python"
        )
    )
)

if "%PYTHON_SYS%"=="" (
    echo ========================================================
    echo   [ERROR] No se encontro Python instalado en el sistema.
    echo ========================================================
    echo   Por favor instala Python 3.10 o superior desde:
    echo   https://www.python.org/downloads/
    echo   (Asegurate de marcar la casilla "Add python.exe to PATH")
    echo ========================================================
    pause
    exit /b 1
)

:: 2. Creacion de entorno virtual (.venv) si no existe
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [IN CRYPTA] Creando entorno virtual local en %VENV_DIR%...
    %PYTHON_SYS% -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

:: 3. Reinstalacion obligatoria de requerimientos (requirements.txt / pygame-ce)
echo [IN CRYPTA] Verificando e instalando requerimientos (pygame-ce)...
if exist "%SCRIPT_DIR%requirements.txt" (
    "%VENV_PYTHON%" -m pip install -r "%SCRIPT_DIR%requirements.txt" --upgrade
    if !errorlevel! neq 0 (
        echo [AVISO] pip install -r requirements.txt tuvo advertencias, asegurando pygame-ce...
        "%VENV_PYTHON%" -m pip install "pygame-ce>=2.5,<3"
    )
) else (
    "%VENV_PYTHON%" -m pip install "pygame-ce>=2.5,<3"
)

echo   Interprete : %VENV_PYTHON%
echo ========================================================

:: 4. Ejecucion del juego
echo [IN CRYPTA] Iniciando juego...
"%VENV_PYTHON%" "%SCRIPT_DIR%main.py" %*

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] El juego finalizo con codigo de error !errorlevel!.
    pause
    exit /b !errorlevel!
)
