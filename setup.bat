@echo off

python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required. https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo Python %%i

node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is required. https://nodejs.org/
    exit /b 1
)
for /f %%i in ('node --version') do echo Node %%i

if not exist "venv" (
    python -m venv venv
    echo Created venv
)

call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt

call npm install

if not exist ".env" if exist ".env.example" (
    copy .env.example .env >nul
    echo Created .env from .env.example
)

echo.
echo Done. Run run.bat to start.
pause
