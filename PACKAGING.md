# PDF Printer 打包指南

## 项目概述

PDF Printer 是一个基于 PyQt5 和 PyMuPDF 的 PDF 查看和打印应用程序。本指南将帮助您将应用程序打包为 Windows 和 macOS 的可执行文件。

## 项目结构

```
pdf_printer/
├── main.py                 # 主应用程序入口
├── ui_handler.py           # 用户界面处理
├── pdf_handler.py          # PDF文件处理
├── scaling_handler.py      # 缩放功能处理
├── page_size_handler.py    # 页面尺寸处理
├── layout_handler.py       # 页面布局处理
├── print_handler.py        # 打印功能处理
├── layout_drawer.py        # 布局绘制处理
├── display_handler.py      # 显示处理
├── display_refresher.py    # 显示刷新处理
├── requirements.txt        # 项目依赖
├── pdf_printer.spec        # PyInstaller 配置文件 (Windows)
├── pdf_printer_macos.spec  # PyInstaller 配置文件 (macOS)
├── build_windows.bat       # Windows 打包脚本
├── build_macos.sh          # macOS 打包脚本
├── PACKAGING.md            # 打包详细说明
├── ICON_CREATION.md        # 图标创建指南
└── README.md               # 项目说明
```

## 依赖项

项目依赖以下 Python 包：
- PyQt5 (用于 GUI 界面)
- PyMuPDF (用于 PDF 处理)

## Windows 打包步骤

### 方法 1: 使用批处理脚本 (推荐)

1. 确保系统已安装 Python 3.6 或更高版本
2. 双击运行 `build_windows.bat` 脚本
3. 脚本将自动安装依赖项并打包应用程序
4. 生成的可执行文件位于 `dist/pdf_printer.exe`

### 方法 2: 手动打包

1. 安装依赖项:
   ```cmd
   pip install -r requirements.txt
   ```

2. 安装 PyInstaller:
   ```cmd
   pip install pyinstaller
   ```

3. 打包应用程序:
   ```cmd
   pyinstaller --noconfirm --windowed --icon=pdf_icon.ico --name=pdf_printer main.py
   ```

   或使用配置文件:
   ```cmd
   pyinstaller pdf_printer.spec
   ```

4. 生成的可执行文件位于 `dist/pdf_printer.exe`

## macOS 打包步骤

### 方法 1: 使用 shell 脚本 (推荐)

1. 确保系统已安装 Python 3.6 或更高版本
2. 在终端中运行以下命令:
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```
3. 脚本将自动安装依赖项并打包应用程序
4. 生成的应用程序位于 `dist/pdf_printer.app`

### 方法 2: 手动打包

1. 安装依赖项:
   ```bash
   pip3 install -r requirements.txt
   ```

2. 安装 PyInstaller:
   ```bash
   pip3 install pyinstaller
   ```

3. 打包应用程序:
   ```bash
   pyinstaller --noconfirm --windowed --icon=pdf_icon.icns --name=pdf_printer main.py
   ```

   或使用配置文件:
   ```bash
   pyinstaller pdf_printer_macos.spec
   ```

4. 生成的应用程序位于 `dist/pdf_printer.app`

## 创建图标文件

### Windows 图标 (ICO)

1. 准备一个 PNG 格式的图片
2. 使用在线转换工具 (如 https://convertio.co/png-ico/) 转换为 ICO 格式
3. 重命名为 `pdf_icon.ico` 并放置在项目根目录

### macOS 图标 (ICNS)

1. 准备一个 PNG 格式的图片
2. 使用在线转换工具 (如 https://convertio.co/png-icns/) 转换为 ICNS 格式
3. 重命名为 `pdf_icon.icns` 并放置在项目根目录

## 打包选项说明

- `--noconfirm`: 覆盖现有文件时不提示确认
- `--windowed`: 不显示控制台窗口 (Windows) 或创建.app bundle (macOS)
- `--icon`: 指定应用程序图标
- `--name`: 指定生成的可执行文件名称

## 注意事项

1. 打包过程中可能会包含大量不必要的依赖项，这是由于 PyInstaller 的自动依赖分析机制导致的
2. 生成的可执行文件可能较大，因为包含了 Python 解释器和所有依赖项
3. 如果打包失败，请检查依赖项是否正确安装
4. 在某些系统上可能需要安装额外的构建工具

## 故障排除

### Windows 常见问题

1. 如果出现 "MSVCP140.dll not found" 错误，请安装 Microsoft Visual C++ Redistributable
2. 如果打包过程中出现权限问题，请以管理员身份运行命令提示符

### macOS 常见问题

1. 如果遇到 "Operation not permitted" 错误，请检查系统完整性保护设置
2. 首次运行应用程序时，可能需要在系统偏好设置中允许从身份不明的开发者运行

## 许可证

本项目仅供学习和研究目的使用，未经授权禁止任何形式的商业使用。