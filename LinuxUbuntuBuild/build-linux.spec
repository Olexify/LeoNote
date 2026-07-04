# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

datas = []
for fn in ('icon.png',):
    if os.path.exists(fn):
        datas.append((fn, '.'))

a = Analysis(
    ['sticky_notes.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter','tkinter.ttk','tkinter.filedialog',
        'tkinter.messagebox','tkinter.simpledialog','json','os','datetime',
        'uuid','ctypes','sys','threading',
        'pystray','PIL','PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy','pandas','matplotlib','scipy','win32api','win32con','win32gui','pythoncom','winreg'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LeoNote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png' if os.path.exists('icon.png') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LeoNote',
)
