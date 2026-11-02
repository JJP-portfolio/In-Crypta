@echo off
setlocal enabledelayedexpansion
title IN CRYPTA - Versión Desktop (Windows)

:: Obtener directorio del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Configurar PYTHONPATH para que los módulos locales tengan prioridad
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

:: Autodetección del intérprete Python (.venv prioritario)
set "PYTHON_BIN="

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_BIN=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_BIN=py -3"
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_BIN=python"
        )
    )
)

if "%PYTHON_BIN%"=="" (
    echo ========================================================
    echo   [ERROR] No se encontró Python instalado en el sistema.
    echo ========================================================
    echo   Por favor instala Python 3.10 o superior desde:
    echo   https://www.python.org/downloads/
    echo   (Asegurate de marcar la casilla "Add python.exe to PATH")
    echo ========================================================
    pause
    exit /b 1
)

echo ========================================================
echo   IN CRYPTA 1.0.0 - Versión Desktop (Windows)
echo ========================================================
echo   Directorio : %SCRIPT_DIR%
echo   Intérprete : %PYTHON_BIN%
echo ========================================================

:: Verificar dependencias (pygame / pygame-ce)
%PYTHON_BIN% -c "import pygame" >nul 2>nul
if !errorlevel! neq 0 (
    echo ▶ Instalando dependencias necesarias (pygame-ce)...
    %PYTHON_BIN% -m pip install pygame-ce
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo instalar pygame-ce automáticamente.
        echo Ejecuta manualmente en la terminal: pip install pygame-ce
        pause
        exit /b 1
    )
)

echo ▶ Iniciando IN CRYPTA...
%PYTHON_BIN% "%SCRIPT_DIR%main.py" %*

if !errorlevel! neq 0 (
    echo.
    echo El juego finalizó con código de error !errorlevel!.
    pause
)
