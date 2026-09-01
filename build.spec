# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

datas = []
for fn in ('icon.png', 'icon.ico'):
    if os.path.exists(fn):
        datas.append((fn, '.'))

# Bundle sounds folder
if os.path.isdir('sounds'):
    for f in os.listdir('sounds'):
        if f.endswith('.wav'):
            datas.append((os.path.join('sounds', f), 'sounds'))

a = Analysis(
    ['sticky_notes.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter','tkinter.ttk','tkinter.filedialog',
        'tkinter.messagebox','tkinter.simpledialog','json','os','datetime',
        'uuid','ctypes','sys','threading','winsound',
        'pystray','PIL','PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy','pandas','matplotlib','scipy','pygame'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onedir build: the EXE holds only the bootloader + scripts; everything else
# lives beside it in dist/LeoNote/. Avoids re-extracting ~20 MB to a fresh
# %TEMP%\_MEIxxxxx on every launch (and the Defender rescan that follows).
# UPX is off for the same reason - decompression cost is paid every start.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LeoNote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='LeoNote',
)
