@echo off
chcp 65001 >nul
echo 停止 TTS Studio 服务...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo 已停止
pause
