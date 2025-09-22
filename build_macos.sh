#!/bin/bash

echo "PDF Printer macOS打包脚本"
echo "============================="

# 检查是否已安装Python
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python。请先安装Python。"
    exit 1
fi

# 安装依赖
echo "正在安装依赖项..."
if ! pip3 install -r requirements.txt; then
    echo "警告: 无法通过requirements.txt安装依赖项，尝试直接安装..."
    if ! pip3 install PyQt5 PyMuPDF; then
        echo "错误: 无法安装依赖项。"
        exit 1
    fi
fi

# 安装PyInstaller
echo "正在安装PyInstaller..."
if ! pip3 install pyinstaller; then
    echo "错误: 无法安装PyInstaller。"
    exit 1
fi

# 打包应用程序
echo "正在打包应用程序..."
if ! pyinstaller --noconfirm --windowed --icon=pdf_icon.icns --name=pdf_printer main.py; then
    echo "错误: 打包失败。"
    exit 1
fi

echo ""
echo "打包完成!"
echo "应用程序位置: dist/pdf_printer.app"
echo ""
echo "注意: 如果需要图标，请确保pdf_icon.icns文件存在于项目目录中。"