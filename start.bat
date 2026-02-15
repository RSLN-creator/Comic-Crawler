@echo off
chcp 65001 >nul 2>&1

set "PROJECT_ROOT=%~dp0"
set "BACKEND_PORT=8765"
set "FRONTEND_PORT=3000"

echo ====================================================================
echo Comic-Crawler Web App
echo ====================================================================

echo [INFO] Checking Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found, please install Python 3.8+
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
    set "PIP_CMD=pip"
) else (
    set "PYTHON_CMD=py"
    set "PIP_CMD=py -m pip"
)
echo [OK] Python found

echo [INFO] Installing dependencies...
%PIP_CMD% install -r "%PROJECT_ROOT%src\web_app\backend\requirements.txt" >nul 2>&1
echo [OK] Dependencies ready

echo [INFO] Starting backend server (hidden)...
cd /d "%PROJECT_ROOT%src\web_app\backend"
powershell -Command "Start-Process -WindowStyle Hidden -FilePath '%PYTHON_CMD%' -ArgumentList '-m','uvicorn','api_server:app','--host','0.0.0.0','--port','%BACKEND_PORT%' -WorkingDirectory '%PROJECT_ROOT%src\web_app\backend'"

ping 127.0.0.1 -n 3 >nul

echo [INFO] Starting frontend server (hidden)...
cd /d "%PROJECT_ROOT%src\web_app\frontend"
powershell -Command "Start-Process -WindowStyle Hidden -FilePath '%PYTHON_CMD%' -ArgumentList '-m','http.server','%FRONTEND_PORT%' -WorkingDirectory '%PROJECT_ROOT%src\web_app\frontend'"

ping 127.0.0.1 -n 3 >nul

echo [INFO] Opening browser...
start http://localhost:%FRONTEND_PORT%

echo ====================================================================
echo Services started!
echo Backend:  http://localhost:%BACKEND_PORT%
echo Frontend: http://localhost:%FRONTEND_PORT%
echo ====================================================================
echo.
echo To stop services, run end.bat or use the button in Web UI.
echo.
echo If you need to open the page manually:
echo http://localhost:%FRONTEND_PORT%
echo.
timeout /t 5 >nul
echo This window will close automatically...
timeout /t 2 >nul
exit
