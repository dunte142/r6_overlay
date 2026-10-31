@echo off
cd /d "%~dp0"
echo ==========================================
echo   R6 Overlay - DEMO visual (sin juego)
echo   Muestra los paneles con datos de prueba
echo   para ver el diseno sin necesitar R6 abierto.
echo ==========================================

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python en el PATH.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt --quiet --disable-pip-version-check
python -m ui.overlay
pause
