@echo off
setlocal

echo Cleaning venv build ...
if exist .\venv\ rmdir /s /q .\venv\

echo Creating virtual environment ...
python -m venv venv

echo Installing dependencies ...
python -m pip install -r requirements.txt

echo Activating venv
call venv\Scripts\activate