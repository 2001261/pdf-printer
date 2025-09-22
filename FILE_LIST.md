# PDF Printer 项目文件清单

## 主要源代码文件
- main.py - 主应用程序入口
- ui_handler.py - 用户界面处理
- pdf_handler.py - PDF文件处理
- scaling_handler.py - 缩放功能处理
- page_size_handler.py - 页面尺寸处理
- layout_handler.py - 页面布局处理
- print_handler.py - 打印功能处理
- layout_drawer.py - 布局绘制处理
- display_handler.py - 显示处理
- display_refresher.py - 显示刷新处理

## 配置和依赖文件
- requirements.txt - 项目依赖列表
- pdf_printer.spec - Windows打包配置文件
- pdf_printer_macos.spec - macOS打包配置文件

## 打包脚本
- build_windows.bat - Windows打包批处理脚本
- build_macos.sh - macOS打包shell脚本

## 文档文件
- README.md - 项目说明文档
- PACKAGING.md - 详细打包指南
- ICON_CREATION.md - 图标创建指南

## 打包后生成的目录
- dist/ - 打包生成的可执行文件目录
- build/ - 打包过程中的临时文件目录

所有文件都已准备就绪，可以进行Windows和macOS平台的打包操作。