# 图标文件生成说明

## Windows图标 (ICO)

要创建Windows图标文件(pdf_icon.ico)，您可以：

1. 使用在线转换工具：
   - 访问https://convertio.co/png-ico/ 或类似网站
   - 上传PNG格式的图片
   - 转换为ICO格式
   - 下载并重命名为pdf_icon.ico

2. 使用图像编辑软件：
   - 使用GIMP、Photoshop等软件
   - 创建多尺寸图标(16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
   - 保存为ICO格式

## macOS图标 (ICNS)

要创建macOS图标文件(pdf_icon.icns)，您可以：

1. 使用在线转换工具：
   - 访问https://convertio.co/png-icns/ 或类似网站
   - 上传PNG格式的图片
   - 转换为ICNS格式
   - 下载并重命名为pdf_icon.icns

2. 使用命令行工具(在macOS上)：
   ```bash
   # 安装工具
   brew install imagemagick
   
   # 创建不同尺寸的PNG文件
   convert icon.png -resize 16x16 icon_16x16.png
   convert icon.png -resize 32x32 icon_32x32.png
   convert icon.png -resize 64x64 icon_64x64.png
   convert icon.png -resize 128x128 icon_128x128.png
   convert icon.png -resize 256x256 icon_256x256.png
   convert icon.png -resize 512x512 icon_512x512.png
   
   # 创建ICNS文件
   png2icns pdf_icon.icns icon_*.png
   ```

## 推荐图标尺寸

为获得最佳显示效果，请确保图标包含以下尺寸：
- 16x16
- 32x32
- 48x48
- 64x64
- 128x128
- 256x256
- 512x512
- 1024x1024 (用于高分辨率显示器)

## 临时解决方案

如果暂时没有图标文件，打包过程仍可正常进行，只是生成的可执行文件会使用默认图标。