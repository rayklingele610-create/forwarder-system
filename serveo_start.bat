@echo off
chcp 65001 >nul
echo ========================================
echo   Serveo.net 免费内网穿透
echo ========================================
echo.

REM 检查SSH
ssh -V >nul 2>&1
if errorlevel 1 (
    echo [错误] SSH客户端未安装
    echo 请启用Windows功能：OpenSSH客户端
    pause
    exit /b 1
)

REM 启动Flask后端（如果未运行）
tasklist | findstr "python.*server.py" >nul
if errorlevel 1 (
    echo [启动] 后端服务...
    start /B python server.py
    timeout /t 3 >nul
)

REM 启动Serveo穿透
echo [启动] Serveo内网穿透...
echo 正在连接 serveo.net，请等待10-20秒...
echo 成功后你会看到公网地址，如：https://xxx.serveo.net
echo.

ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:5000 serveo.net

echo.
echo ========================================
echo 如果连接成功，你会获得一个公网地址
echo 如：https://xxx.serveo.net
echo 任何人都可以通过该地址访问你的货代系统
echo ========================================
echo.
pause