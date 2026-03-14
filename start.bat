@echo off
chcp 65001 >nul
echo ========================================
echo 服务器监控系统 - Windows启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败
        echo 请确保已安装Python并添加到PATH
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建成功
) else (
    echo [1/4] 虚拟环境已存在
)

echo.
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✓ 虚拟环境已激活

echo.
echo [3/4] 安装/更新依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 部分依赖安装失败，但将继续运行
)
echo ✓ 依赖安装完成

echo.
echo [4/4] 启动应用...
echo ========================================
echo 应用将在 http://localhost:5000 运行
echo 窗口将最小化到后台运行
echo 如需停止服务, 请在任务管理器结束 python 进程
echo ========================================
echo.

REM 最小化启动 Flask 应用到后台
start "" /min python app.py

REM 当前启动脚本直接退出
exit /b 0
