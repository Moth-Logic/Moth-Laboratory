# -*- mode: python ; coding: utf-8 -*-
#
# Spec file de PyInstaller para "My First Calculator".
#
# Uso (en Windows, con el venv activado):
#     pyinstaller build.spec
#
# El .exe queda en dist/MyFirstCalculator.exe
#
# Por qué usamos un .spec en vez de solo pasar flags por CLI:
# a futuro, cuando agreguemos más módulos (ej. C++ vía pybind11,
# assets como iconos, o funciones científicas con dependencias
# extra), este archivo es el único lugar que hay que tocar.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MyFirstCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # sin consola negra detrás de la GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # descomentar cuando tengamos un ícono
)
