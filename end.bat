@echo off
chcp 65001 >nul 2>&1

echo ====================================================================
echo Comic-Crawler - Stop Services
echo ====================================================================

echo [INFO] Stopping services...

set "BACKEND_PORT=8765"
set "FRONTEND_PORT=3000"

echo.
echo [INFO] Stopping backend server (port %BACKEND_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo [INFO] Killing process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [INFO] Stopping frontend server (port %FRONTEND_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo [INFO] Killing process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ====================================================================
echo Services stopped successfully!
echo ====================================================================

timeout /t 3 >nul
