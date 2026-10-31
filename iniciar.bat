@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul

echo ==========================================
echo   R6 Overlay - Launcher tactico
echo   Arranque estable de Python 3.12
echo ==========================================

REM Preferir Python 3.12 de 64 bits instalado desde python.org. El alias de
REM Microsoft Store (WindowsApps\python.exe) no se selecciona automaticamente.
where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
    if not errorlevel 1 goto use_py312
)

REM Fallback: primer python.exe real de PATH, ignorando el alias WindowsApps.
set "PYTHON_PATH="
for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | findstr /i "\\WindowsApps\\" >nul
    if errorlevel 1 if not defined PYTHON_PATH (
        "%%P" -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] in ((3,10),(3,11),(3,12)) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_PATH=%%P"
    )
)
if defined PYTHON_PATH goto use_path_python

echo.
echo [ERROR] No se encontro Python 3.12 de 64 bits (o Python 3.10/3.11 x64).
echo Instala Python 3.12 desde https://www.python.org/downloads/windows/
echo Durante la instalacion activa "Add python.exe to PATH".
echo No uses el alias de Microsoft Store para ejecutar este proyecto.
pause
exit /b 1

:use_py312
set "PYRUN=py -3.12"
echo [Python] Se utilizara Python 3.12 x64 mediante el launcher oficial.
goto install_deps

:use_path_python
"%PYTHON_PATH%" --version
set "PYRUN_PATH=%PYTHON_PATH%"
echo [Python] Se utilizara %PYTHON_PATH%.
goto install_deps

:install_deps
echo.
echo [1/2] Verificando e instalando dependencias...
if defined PYRUN (
    %PYRUN% -m pip install --upgrade pip --quiet --disable-pip-version-check
    if errorlevel 1 goto pip_error
    %PYRUN% -m pip install -r requirements.txt --quiet --disable-pip-version-check
) else (
    "%PYRUN_PATH%" -m pip install --upgrade pip --quiet --disable-pip-version-check
    if errorlevel 1 goto pip_error
    "%PYRUN_PATH%" -m pip install -r requirements.txt --quiet --disable-pip-version-check
)
if errorlevel 1 goto pip_error

echo.
echo [Audio] Verificando PyAudioWPatch en el mismo Python que ejecutara el overlay...
if defined PYRUN (
    %PYRUN% -c "import pyaudiowpatch" >nul 2>nul
    if errorlevel 1 (
        echo [Audio] No esta instalado. Instalando wheel binario para Windows...
        %PYRUN% -m pip install --disable-pip-version-check --no-input --only-binary=:all: "PyAudioWPatch==0.2.12.9"
    )
    %PYRUN% -c "import pyaudiowpatch; print('PyAudioWPatch OK:', getattr(pyaudiowpatch, '__version__', 'instalado'))" 2>nul
    if errorlevel 1 echo [ADVERTENCIA] Audio no disponible. El HUD y la vision pueden seguir funcionando.
) else (
    "%PYRUN_PATH%" -c "import pyaudiowpatch" >nul 2>nul
    if errorlevel 1 (
        echo [Audio] No esta instalado. Instalando wheel binario para Windows...
        "%PYRUN_PATH%" -m pip install --disable-pip-version-check --no-input --only-binary=:all: "PyAudioWPatch==0.2.12.9"
    )
    "%PYRUN_PATH%" -c "import pyaudiowpatch; print('PyAudioWPatch OK:', getattr(pyaudiowpatch, '__version__', 'instalado'))" 2>nul
    if errorlevel 1 echo [ADVERTENCIA] Audio no disponible. El HUD y la vision pueden seguir funcionando.
)

echo.
echo [2/2] Abriendo launcher.py...
set "PYTHONUNBUFFERED=1"
if defined PYRUN (
    %PYRUN% launcher.py
) else (
    "%PYRUN_PATH%" launcher.py
)
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo [ERROR] El launcher finalizo con codigo %EXITCODE%.
    echo Revisa overlay_log.txt y faulthandler_dump.txt.
    pause
)
exit /b %EXITCODE%

:pip_error
echo.
echo [ERROR] No se pudieron instalar las dependencias.
echo Comprueba tu conexion y que Python sea de 64 bits.
pause
exit /b 1
