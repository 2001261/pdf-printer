@echo off
echo PDF Printer Windows打包脚本
echo =============================

REM 检查是否已安装Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请先安装Python。
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖项...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 无法通过requirements.txt安装依赖项，尝试直接安装...
    pip install PyQt5 PyMuPDF
    if %errorlevel% neq 0 (
        echo 错误: 无法安装依赖项。
        pause
        exit /b 1
    )
)

REM 安装PyInstaller
echo 正在安装PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 错误: 无法安装PyInstaller。
    pause
    exit /b 1
)

REM 打包应用程序
echo 正在打包应用程序...
pyinstaller --noconfirm --windowed --icon=pdf_icon.ico --name=pdf_printer main.py
if %errorlevel% neq 0 (
    echo 错误: 打包失败。
    pause
    exit /b 1
)

echo.
echo 打包完成!
echo 可执行文件位置: dist\pdf_printer.exe
echo.
echo 注意: 如果需要图标，请确保pdf_icon.ico文件存在于项目目录中。
pause