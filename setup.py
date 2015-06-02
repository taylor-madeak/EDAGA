from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['pygame', 'pygame.gfxdraw', 'tkinter' ,'tkinter.filedialog', 'xml.etree.ElementTree',
                                'os', 'sys', 'pygame.locals'], excludes = [], compressed=True)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('EDGUI_v2.py', base=base, targetName = 'EDGUI.exe', icon='edgui_icon.ico', compress=True)
]

setup(name='Elite: Dangerous Advanced Gamepad Assistant',
      version = '2.01.08',
      description = 'Elite: Dangerous Advanced Gamepad Assistant',
      options = dict(build_exe = buildOptions),
      executables = executables)
