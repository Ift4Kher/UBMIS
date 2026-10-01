@echo off
echo Starting UBMIS Server...
cd /d "%~dp0"
call venv\Scripts\activate
python manage.py runserver
pause
