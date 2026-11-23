@echo off
title Klondike Solitaire - Desktop App
cd /d "%~dp0"

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    "%LOCALAPPDATA%\Python\bin\python.exe" gui.py
    if %ERRORLEVEL% equ 0 exit /b
)

python gui.py
if %ERRORLEVEL% equ 0 exit /b

py gui.py
