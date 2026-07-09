@echo off
chcp 65001 >nul
title TTS Studio 启动中...

echo ================================
echo   TTS Studio - 正在启动服务
echo ================================
echo.

cd /d F:\webVideoCloneTTS\backend
echo [1/3] 启动后端服务...
start "TTS-Backend" python -m uvicorn app.main:app --port 8000

echo [2/3] 等待后端就绪...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s -o NUL http://127.0.0.1:8000/health 2>nul
if errorlevel 1 goto wait_backend
echo        后端已就绪 (http://127.0.0.1:8000)

cd /d F:\webVideoCloneTTS\frontend
echo [3/3] 启动前端服务并打开浏览器...
start http://localhost:5173
npm run dev

pause
