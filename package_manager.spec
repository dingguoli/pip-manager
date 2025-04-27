# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集所有必要的数据文件
datas = [
    ('src/ui', 'src/ui'),
    ('src/core', 'src/core'),
    ('resources', 'resources'),
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

# 收集所有必要的隐藏导入
hiddenimports = [
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'json',
    'logging',
    'datetime',
    'subprocess',
    'os',
    'sys',
    'pathlib',
    'typing',
    'shutil',
    'cairo',
]

# 为每个PyQt5模块收集数据
qt_modules = ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets']
for module in qt_modules:
    collect_result = collect_all(module)
    datas.extend(collect_result[0])
    hiddenimports.extend(collect_result[2])

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤重复的二进制文件
def remove_duplicate_binaries(binaries):
    seen = set()
    filtered = []
    for binary in binaries:
        if binary[0] not in seen:
            seen.add(binary[0])
            filtered.append(binary)
    return filtered

a.binaries = remove_duplicate_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PackageManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon_large.png',
    version='file_version_info.txt',
)
