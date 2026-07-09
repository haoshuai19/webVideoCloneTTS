<#
.TITLE TTS Studio — 一键启动
.DESCRIPTION 同时启动后端 (FastAPI :8000) 和前端 (Vite :5173)
#>

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

# Colors
$CYAN = "Cyan"
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"

Write-Host "========================================" -ForegroundColor $CYAN
Write-Host "   TTS Studio - 一键启动" -ForegroundColor $CYAN
Write-Host "========================================" -ForegroundColor $CYAN
Write-Host ""

# --- Backend ---
Write-Host "[1/2] 启动后端 (FastAPI :8000)..." -ForegroundColor $YELLOW
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    python -m uvicorn app.main:app --port 8000 --host 0.0.0.0
} -ArgumentList $ROOT\backend

# Wait for backend to be ready
Write-Host "  等待后端就绪..." -ForegroundColor $YELLOW
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($resp.Content -match '"status":"ok"') {
            $ready = $true
            break
        }
    } catch {}
    Start-Sleep 1
}
if ($ready) {
    Write-Host "  后端已就绪 ✓ http://localhost:8000" -ForegroundColor $GREEN
} else {
    Write-Host "  后端启动超时，请检查日志" -ForegroundColor $RED
}

# --- Frontend ---
Write-Host ""
Write-Host "[2/2] 启动前端 (Vite :5173)..." -ForegroundColor $YELLOW
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList $ROOT\frontend

Start-Sleep 5
Write-Host "  前端已启动 ✓ http://localhost:5173" -ForegroundColor $GREEN

Write-Host ""
Write-Host "========================================" -ForegroundColor $GREEN
Write-Host "   服务已全部启动!" -ForegroundColor $GREEN
Write-Host "   前端: http://localhost:5173" -ForegroundColor $CYAN
Write-Host "   后端: http://localhost:8000" -ForegroundColor $CYAN
Write-Host "========================================" -ForegroundColor $GREEN
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor $YELLOW

# Wait for either job to complete (user presses Ctrl+C)
Wait-Job $backendJob, $frontendJob -Timeout 999999 | Out-Null

# Cleanup on exit
Write-Host "正在停止服务..." -ForegroundColor $YELLOW
Stop-Job $backendJob -ErrorAction SilentlyContinue
Stop-Job $frontendJob -ErrorAction SilentlyContinue
Remove-Job $backendJob -ErrorAction SilentlyContinue
Remove-Job $frontendJob -ErrorAction SilentlyContinue

# Kill orphaned processes
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "uvicorn" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "vite" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "已停止所有服务" -ForegroundColor $GREEN
