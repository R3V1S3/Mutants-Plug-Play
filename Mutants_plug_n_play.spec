# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Mutants_plug_n_play.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('D:/Mutants_plug_n_play/azure.tcl', '.'),
        ('D:/Mutants_plug_n_play/theme', 'theme'),
        ('D:/Mutants_plug_n_play/OpenHardwareMonitor', 'OpenHardwareMonitor'),
        ('D:/Mutants_plug_n_play/step1.png', '.'),
        ('D:/Mutants_plug_n_play/step2.png', '.'),
        ('D:/Mutants_plug_n_play/step3.png', '.'),
        ('D:/Mutants_plug_n_play/step4.png', '.'),
        ('D:/Mutants_plug_n_play/motherboard-icon-16.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    onefile=True,
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Mutants plug & play',
    icon='D:\Mutants_plug_n_play\motherboard-icon-16.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Mutants plug & play',
)
