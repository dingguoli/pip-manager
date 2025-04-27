@echo off
chcp 65001
echo 正在启动Python包管理器...

:: 显示详细信息
echo 脚本路径: %~dp0
echo 当前目录: %CD%

:: 确保在脚本所在目录运行
cd /d "%~dp0"
echo 切换后目录: %CD%

:: 检查必要文件是否存在
echo 检查必要文件...
echo requirements.txt 状态:
dir requirements.txt

if not exist "requirements.txt" (
    echo 错误: 未找到 requirements.txt 文件
    echo 当前目录: %CD%
    pause
    exit /b 1
)

:: 检查Python是否安装
echo 检查Python安装...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查src目录
if not exist "src" (
    echo 错误: 未找到src目录
    echo 当前目录内容:
    dir
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist venv (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        echo Python路径:
        where python
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 激活虚拟环境失败
    echo 虚拟环境目录内容:
    dir venv\Scripts
    pause
    exit /b 1
)

:: 验证虚拟环境
echo 虚拟环境信息:
echo VIRTUAL_ENV: %VIRTUAL_ENV%
python --version
where python

:: 安装依赖
echo 正在安装依赖...
echo 当前目录: %CD%
echo requirements.txt 内容:
type requirements.txt
echo.
echo 开始安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖失败
    echo Pip版本:
    pip --version
    pause
    exit /b 1
)

:: 设置 Qt 插件路径
set QT_DEBUG_PLUGINS=1
set QT_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PyQt5\Qt5\plugins
echo Qt插件路径: %QT_PLUGIN_PATH%

:: 运行应用
echo 正在启动应用...
set PYTHONPATH=%CD%;%PYTHONPATH%
echo PYTHONPATH: %PYTHONPATH%
python src/main.py
if errorlevel 1 (
    echo 错误: 启动应用失败
    echo Python路径: 
    where python
    echo 当前目录内容:
    dir
    echo.
    echo Qt插件目录内容:
    dir "%QT_PLUGIN_PATH%"
    pause
    exit /b 1
)

:: 退出虚拟环境
deactivate

pause 

dir /s /b 原始项目路径 > original_structure.txt
dir /s /b git克隆项目路径 > git_structure.txt

cd ..
rm -rf pip-manager
git clone 仓库URL 