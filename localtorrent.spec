# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for LocalTorrent
# Run: pyinstaller localtorrent.spec

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

a = Analysis(
    ['localtorrent/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'localtorrent',
        'localtorrent.engine',
        'localtorrent.engine.metainfo',
        'localtorrent.engine.torrent',
        'localtorrent.engine.peer',
        'localtorrent.engine.peer_manager',
        'localtorrent.engine.piece_picker',
        'localtorrent.engine.discovery',
        'localtorrent.engine.runner',
        'localtorrent.gui',
        'localtorrent.gui.app',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='localtorrent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Set True if you want a terminal window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Add .ico path here for Windows icon
)
