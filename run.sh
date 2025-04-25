#!/bin/bash

echo "正在启动Python包管理器..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "错误: 激活虚拟环境失败"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 安装依赖失败"
    exit 1
fi

# 运行应用
echo "正在启动应用..."
python src/main.py
if [ $? -ne 0 ]; then
    echo "错误: 启动应用失败"
    exit 1
fi

# 退出虚拟环境
deactivate 