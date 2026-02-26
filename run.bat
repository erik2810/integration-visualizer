@echo off

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo No venv found. Run setup.bat first.
)

if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

if not defined APP_PORT set APP_PORT=8000
start "Backend" python -m uvicorn backend.app:app --host 0.0.0.0 --port %APP_PORT% --reload
timeout /t 2 /nobreak >nul

start "Frontend" npm run dev

echo Frontend: http://localhost:3000
echo Backend:  http://localhost:%APP_PORT%
echo Close this window to stop.
pause
