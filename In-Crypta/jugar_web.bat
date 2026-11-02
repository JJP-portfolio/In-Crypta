@echo off
title IN CRYPTA - Web Runtime
echo ========================================================
echo   IN CRYPTA - Plataforma Web (GDevelop JS / PixiJS)
echo ========================================================
echo Abriendo navegador en http://localhost:8000/export/gdevelop/index.html ...
echo Presiona Ctrl+C en esta ventana para cerrar el servidor.
echo.
start http://localhost:8000/export/gdevelop/index.html
.\.venv\Scripts\python.exe -m http.server 8000
