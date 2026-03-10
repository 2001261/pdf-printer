# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主脚本及其依赖
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'fitz'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的标准库模块
        'tkinter', 'unittest', 'email', 'http', 'urllib', 'xml', 
        'pydoc', 'doctest', 'argparse', 'difflib', 'inspect', 
        'pickle', 'tarfile', 'gzip', 'bz2', 'zipfile', 'lzma', 
        'calendar', 'sqlite3', 'csv', 'bdb', 'pdb', 'py_compile',
        'compileall', 'distutils', 'ftplib', 'imaplib', 'poplib',
        'smtpd', 'smtplib', 'telnetlib', 'uuid', 'webbrowser',
        'cgi', 'cgitb', 'wsgiref', 'platform', 'plistlib',
        'dummy_threading', 'threading', '_threading_local',
        
        # 排除大型科学计算库
        'numpy', 'scipy', 'matplotlib', 'pandas', 'sklearn',
        'tensorflow', 'torch', 'cv2', 'PIL', 'sympy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2
)

# 创建PYZ归档
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFPrinter_Optimized',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 剥离符号表
    upx=True,    # 使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)