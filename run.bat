@echo off
chcp 65001
echo 正在启动Python包管理器...

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist venv (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖失败
    pause
    exit /b 1
)

:: 运行应用
echo 正在启动应用...
set PYTHONPATH=%CD%
python src/main.py
if errorlevel 1 (
    echo 错误: 启动应用失败
    pause
    exit /b 1
)

:: 退出虚拟环境
deactivate 