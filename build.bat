@echo off
setlocal

rem Activate virtual environment
call venv\Scripts\activate

rem Clean previous builds
echo Cleaning previous build ...
if exist .\dist\ rmdir /s /q .\dist\
if exist .\build\ rmdir /s /q .\build\

rem Create spec file
echo Creating spec file ...
rem pyinstaller --name=TonuinoLabelMaker --windowed --onedir --specpath=%CD% src\main.py

rem Build the application
echo Building the application ...
pyinstaller TonuinoLabelMaker.spec

echo Build complete.
pause
