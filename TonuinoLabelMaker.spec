block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui', 'ui'),
        ('src/resources/templates.json', 'resources'),
        ('src/resources/espuino_logo.png', 'resources'),
        ('src/resources/tonuino_logo.png', 'resources'),
    ],
    hiddenimports=['PyQt6.QtPrintSupport', 'src.ui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=True,
    name="TonuinoLabelMaker",
    debug=False,
    bootloader_ignore_signal=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arc=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe, 
    a.binaries,
    a.datas,
    stip=False,
    upx=True,
    upx_exclude=[],
    name="TonuinoLabelMaker"
)
