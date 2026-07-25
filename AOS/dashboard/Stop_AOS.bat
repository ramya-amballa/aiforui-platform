@echo off
setlocal enabledelayedexpansion
title AOS Command Center - Stop

echo Stopping AOS Command Center...
echo.

set "FOUND=False"
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue).OwningProcess" 2^>nul') do (
    taskkill /PID %%P /F >nul 2>&1
    set "FOUND=True"
)

if /I "%FOUND%"=="True" (
    echo AOS Command Center has been stopped.
) else (
    echo AOS Command Center was not running.
)

echo.
pause
