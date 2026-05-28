@echo off
chcp 65001 >nul
echo ========================================
echo   货代信息查询系统 - 一键启动脚本
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
pip list | findstr Flask >nul
if errorlevel 1 (
    echo [安装依赖] 正在安装Flask...
    pip install flask flask-cors -q
)

REM 启动Flask后端
echo [启动] 后端服务 (localhost:5000)...
start "货代系统后端" python server.py

REM 等待3秒让服务启动
timeout /t 3 /nobreak >nul

REM 检查frp配置
if exist frpc.ini (
    echo [检查] frpc.ini 配置...
    findstr "server_addr" frpc.ini >nul
    if errorlevel 1 (
        echo [警告] frpc.ini 未配置，仅限局域网访问
        echo 如需公网访问，请先注册 frp.freefrp.net 并配置frpc.ini
    ) else (
        if exist frpc.exe (
            echo [启动] frp内网穿透 (公网访问)...
            start "FRP客户端" frpc.exe -c frpc.ini
        ) else (
            echo [提示] frpc.exe 未找到，请从以下地址下载：
            echo https://github.com/fatedier/frp/releases
            echo 下载 frp_0.xx.x_windows_amd64.zip 并解压到本目录
        )
    )
)

REM 打开浏览器
echo [打开] 浏览器访问...
start "" "http://localhost:5000"

echo.
echo ========================================
echo 访问地址:
echo 局域网: http://%COMPUTERNAME%:5000
echo 或: http://192.168.0.190:5000
echo.
echo 如需公网访问，请配置 frpc.ini 并启动 frp
echo ========================================
echo.
echo 按任意键查看详细部署指南...
pause >nul
start deploy_guide.md