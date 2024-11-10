@echo off
setlocal

echo Cleaning venv build ...
if exist .\venv\ rmdir /s /q .\venv\

echo Activating venv ...
call venv\Scripts\activate

echo Installing dependencies ...
python -m pip install -r requirements.txt

echo Virtual environment setup complete.