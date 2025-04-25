# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集所有需要的数据文件和依赖
datas = [
    ('src/ui', 'src/ui'),
    ('src/core', 'src/core'),
    ('config', 'config'),
    ('README.md', '.'),
]

# 收集PyQt5相关文件
qt_binaries = []
qt_datas = []
hiddenimports = ['PyQt5.sip']

# 添加额外的隐藏导入
additional_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'win32api',
    'win32con',
    'win32gui',
    'requests',
]
hiddenimports.extend(additional_imports)

# 为每个PyQt5模块收集数据
for pkg in ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets']:
    collect_result = collect_all(pkg)
    datas.extend(collect_result[0])
    binaries = collect_result[1]
    hiddenimports.extend(collect_result[2])

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
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

# 过滤重复的DLL
def remove_dup_binaries(binaries):
    seen = set()
    filtered = []
    for binary in binaries:
        name = os.path.basename(binary[0]).lower()
        if name not in seen:
            seen.add(name)
            filtered.append(binary)
    return filtered

a.binaries = remove_dup_binaries(a.binaries)

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
    console=True,  # 临时设置为True以查看错误信息
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui/resources/icon.ico',
    version='file_version_info.txt'
)
