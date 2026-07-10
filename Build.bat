@echo off
setlocal EnableExtensions

title Leo Note Build

echo =====================================
echo          Leo Note Build Tool
echo =====================================
echo.

cd /d "%~dp0"

set "PYTHON=python"
set "SPEC_FILE=build.spec"
set "MAIN_FILE=sticky_notes.py"
set "VERSION_FILE=version_info.txt"
set "DIST_EXE=dist\LeoNote.exe"

echo [1/5] Checking Python...
where %PYTHON% >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    echo Install Python and make sure "python" works in Command Prompt.
    goto :fail
)

echo [2/5] Installing/updating build dependencies...
%PYTHON% -m pip install --upgrade pip
if errorlevel 1 goto :fail

%PYTHON% -m pip install --upgrade pyinstaller pystray pillow
if errorlevel 1 goto :fail

echo [3/5] Validating required files...
if not exist "%SPEC_FILE%" (
    echo ERROR: Missing %SPEC_FILE%
    goto :fail
)

if not exist "%MAIN_FILE%" (
    echo ERROR: Missing %MAIN_FILE%
    goto :fail
)

if not exist "%VERSION_FILE%" (
    echo ERROR: Missing %VERSION_FILE%
    goto :fail
)

if not exist "icon.ico" (
    echo WARNING: icon.ico not found. Build may fail because build.spec requires it.
)

echo [4/5] Cleaning previous build output...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"

echo [5/5] Building executable...
%PYTHON% -m PyInstaller --clean "%SPEC_FILE%"
if errorlevel 1 goto :fail

echo.
if exist "%DIST_EXE%" (
    echo =====================================
    echo Build completed successfully.
    echo Output: %DIST_EXE%
    echo =====================================
    goto :end
) else (
    echo ERROR: Build finished but %DIST_EXE% was not found.
    goto :fail
)

:fail
echo.
echo =====================================
echo Build failed.
echo =====================================
pause
exit /b 1

:end
echo.
pause
exit /b 0