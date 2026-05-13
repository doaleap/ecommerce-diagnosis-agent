
@echo off
echo ========================================
echo   电商运营异常诊断系统
echo ========================================
echo.

echo [1/2] 检查 Python 依赖...
pip install -r requirements.txt -q
echo 依赖安装完成！
echo.

echo [2/2] 启动服务...
echo.
echo 服务启动后请访问：http://localhost:8000
echo.
python app.py

pause

