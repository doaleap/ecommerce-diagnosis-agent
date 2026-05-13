
@echo off
chcp 65001 >nul
title 电商运营异常诊断系统
color 0A
echo.
echo ========================================
echo   电商运营异常诊断系统 - 快速启动
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查环境...
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python 环境正常
echo.

echo [2/3] 安装依赖...
py -m pip install -r requirements.txt -q
echo [OK] 依赖检查完成
echo.

echo [3/3] 启动服务...
echo.
echo ========================================
echo   [START] 服务即将启动...
echo   请在浏览器打开: http://localhost:8000
echo ========================================
echo.

py app.py

pause
