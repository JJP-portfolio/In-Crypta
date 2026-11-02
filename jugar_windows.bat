@echo off
setlocal enabledelayedexpansion
title IN CRYPTA - Version Desktop (Windows)

:: Obtener directorio del script de forma segura (con barra final)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: PYTHONPATH para que los modulos locales tengan prioridad
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

set "PYTHON_EXE="
set "PYTHON_ARG="

:: ----------------------------------------------------------------------
:: 1. Probar .venv local si existe y realmente funciona en esta maquina
:: ----------------------------------------------------------------------
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    "%SCRIPT_DIR%.venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
        set "PYTHON_ARG="
        goto :python_encontrado
    ) else (
        echo [AVISO] El entorno .venv local no es compatible con esta ruta/maquina.
        echo         Buscando Python instalado en el sistema...
    )
)

:: ----------------------------------------------------------------------
:: 2. Probar 'py' (Python Launcher oficial de Windows)
:: ----------------------------------------------------------------------
where py >nul 2>nul
if !errorlevel! equ 0 (
    py -3 -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARG=-3"
        goto :python_encontrado
    )
    py -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARG="
        goto :python_encontrado
    )
)

:: ----------------------------------------------------------------------
:: 3. Probar 'python' en PATH
:: ----------------------------------------------------------------------
where python >nul 2>nul
if !errorlevel! equ 0 (
    python -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
        set "PYTHON_ARG="
        goto :python_encontrado
    )
)

:: ----------------------------------------------------------------------
:: 4. Probar 'python3' en PATH
:: ----------------------------------------------------------------------
where python3 >nul 2>nul
if !errorlevel! equ 0 (
    python3 -c "import sys" >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python3"
        set "PYTHON_ARG="
        goto :python_encontrado
    )
)

:: ----------------------------------------------------------------------
:: 5. Buscar en rutas estandar de instalacion de Windows
:: ----------------------------------------------------------------------
for %%V in (314 313 312 311 310 39) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
            set "PYTHON_ARG="
            goto :python_encontrado
        )
    )
    if exist "%ProgramFiles%\Python%%V\python.exe" (
        "%ProgramFiles%\Python%%V\python.exe" -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=%ProgramFiles%\Python%%V\python.exe"
            set "PYTHON_ARG="
            goto :python_encontrado
        )
    )
    if exist "C:\Python%%V\python.exe" (
        "C:\Python%%V\python.exe" -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=C:\Python%%V\python.exe"
            set "PYTHON_ARG="
            goto :python_encontrado
        )
    )
)

:: ----------------------------------------------------------------------
:: Si llego aqui, no se encontro ninguna instalacion valida
:: ----------------------------------------------------------------------
echo ====================================================================
echo   [ERROR] No se encontro una instalacion funcional de Python.
echo ====================================================================
echo   Para jugar a IN CRYPTA en Windows:
echo   1. Descarga Python 3.10 o superior desde:
echo      https://www.python.org/downloads/
echo   2. Al instalar, ASEGURATE de marcar la casilla:
echo      [X] "Add python.exe to PATH" (Agregar Python al PATH)
echo   3. Luego vuelve a hacer doble clic en este archivo.
echo ====================================================================
echo.
pause
exit /b 1

:python_encontrado
echo ========================================================
echo   IN CRYPTA 1.0.0 - Version Desktop (Windows)
echo ========================================================
echo   Directorio : %SCRIPT_DIR%
if "%PYTHON_ARG%"=="" (
    echo   Interprete : %PYTHON_EXE%
) else (
    echo   Interprete : %PYTHON_EXE% %PYTHON_ARG%
)
echo ========================================================

:: ----------------------------------------------------------------------
:: Verificar si pygame / pygame-ce esta instalado
:: ----------------------------------------------------------------------
"%PYTHON_EXE%" %PYTHON_ARG% -c "import pygame" >nul 2>nul
if !errorlevel! neq 0 (
    echo ▶ Instalando dependencias necesarias (pygame-ce)...
    "%PYTHON_EXE%" %PYTHON_ARG% -m pip install --upgrade --user pygame-ce
    if !errorlevel! neq 0 (
        "%PYTHON_EXE%" %PYTHON_ARG% -m pip install pygame-ce
    )
    if !errorlevel! neq 0 (
        "%PYTHON_EXE%" %PYTHON_ARG% -m pip install --user pygame
    )
    "%PYTHON_EXE%" %PYTHON_ARG% -c "import pygame" >nul 2>nul
    if !errorlevel! neq 0 (
        echo.
        echo ========================================================
        echo   [ERROR] No se pudo instalar pygame-ce automaticamente.
        echo ========================================================
        echo   Por favor abre CMD o PowerShell y ejecuta manualmente:
        echo     pip install pygame-ce
        echo ========================================================
        echo.
        pause
        exit /b 1
    )
)

:: ----------------------------------------------------------------------
:: Iniciar el juego
:: ----------------------------------------------------------------------
echo ▶ Iniciando IN CRYPTA...
"%PYTHON_EXE%" %PYTHON_ARG% "%SCRIPT_DIR%main.py" %*
set "GAME_ERR=!errorlevel!"

if !GAME_ERR! neq 0 (
    echo.
    echo ========================================================
    echo   El juego finalizo con codigo de error !GAME_ERR!.
    echo   Revisa los mensajes anteriores para ver el detalle.
    echo ========================================================
    echo.
    pause
    exit /b !GAME_ERR!
)
