@echo off
setlocal enabledelayedexpansion
title AOS Command Center - Launcher
cd /d "%~dp0"

echo ============================================
echo   AOS Command Center
echo ============================================
echo.

REM --- Step 1: Find Python -------------------------------------------------
set "PY_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py -3"
) else (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    echo Python was not found on this computer.
    echo.
    echo Please install Python from https://www.python.org/downloads
    echo IMPORTANT: during setup, check the box that says:
    echo     Add python.exe to PATH
    echo Then double-click Start_AOS.bat again.
    echo.
    mshta "javascript:alert('Python was not found on this computer.\n\nPlease install Python from https://www.python.org/downloads\n\nDuring setup, check the box that says:\nAdd python.exe to PATH\n\nThen double-click Start_AOS.bat again.');close()" >nul 2>&1
    pause
    exit /b 1
)

echo Found Python: %PY_CMD%
echo.

REM --- Step 2: Is it already running? ---------------------------------------
set "IS_RUNNING=False"
for /f %%R in ('powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { 'True' } else { 'False' }" 2^>nul') do set "IS_RUNNING=%%R"

if /I "%IS_RUNNING%"=="True" (
    echo AOS Command Center is already running - opening your browser...
    start "" "http://localhost:8501"
    timeout /t 2 /nobreak >nul
    exit /b 0
)

REM --- Step 3: Install missing packages, only if needed ----------------------
%PY_CMD% -c "import streamlit, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages - this only happens once and can
    echo take a minute or two. Please wait...
    echo.
    %PY_CMD% -m pip install --quiet -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Something went wrong installing the required packages.
        echo Please check your internet connection, then double-click
        echo Start_AOS.bat again.
        echo.
        pause
        exit /b 1
    )
    echo Packages installed successfully.
) else (
    echo Required packages are already installed.
)
echo.

REM --- Step 3b: Install spaCy + its English model, only if needed ------------
REM Powers Demand Intelligence's offline organisation-detection (no API key
REM needed) - AOS's only non-dashboard Python dependency. Same one-time,
REM automatic install pattern as Step 3 above.
%PY_CMD% -c "import spacy; spacy.load('en_core_web_sm')" >nul 2>&1
if errorlevel 1 (
    echo Installing Demand Intelligence's offline AI-detection model - this
    echo only happens once and can take a minute or two. Please wait...
    echo.
    %PY_CMD% -m pip install --quiet -r "..\demand-intelligence\runtime\requirements.txt"
    if errorlevel 1 (
        echo.
        echo Something went wrong installing spaCy. Please check your
        echo internet connection, then double-click Start_AOS.bat again.
        echo Demand Intelligence will still run without it, using the
        echo optional Claude API backend instead if ANTHROPIC_API_KEY is set.
        echo.
    ) else (
        %PY_CMD% -m spacy download en_core_web_sm
        if errorlevel 1 (
            echo.
            echo Something went wrong downloading the language model. Please
            echo check your internet connection, then double-click
            echo Start_AOS.bat again.
            echo.
        ) else (
            echo Offline AI-detection model installed successfully.
        )
    )
) else (
    echo Demand Intelligence's offline AI-detection model is already installed.
)
echo.

REM --- Step 4: Start the dashboard in its own minimized window ---------------
echo Starting AOS Command Center...
start "AOS Command Center - do not close this window" /min cmd /c "%PY_CMD% -m streamlit run app.py --server.headless=true --server.port=8501"

REM --- Step 5: Wait until it is ready, then open the browser -----------------
echo Waiting for the dashboard to become ready...
set "READY=False"
for /L %%i in (1,1,30) do (
    if /I "!READY!"=="False" (
        for /f %%R in ('powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { 'True' } else { 'False' }" 2^>nul') do set "READY=%%R"
        if /I "!READY!"=="False" timeout /t 1 /nobreak >nul
    )
)

if /I "%READY%"=="True" (
    echo Dashboard is ready - opening your browser...
    start "" "http://localhost:8501"
    timeout /t 2 /nobreak >nul
    exit /b 0
) else (
    echo.
    echo The dashboard did not start within 30 seconds.
    echo Look for a minimized window titled "AOS Command Center" on your
    echo taskbar - it may still be starting, or it may show an error message.
    echo.
    pause
    exit /b 1
)
