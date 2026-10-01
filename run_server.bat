@echo off
echo Starting University Bus Management System...
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found! Please ensure 'venv' exists in this directory.
    pause
    exit /b
)
venv\Scripts\python manage.py runserver 8000
pause
