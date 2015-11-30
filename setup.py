# -*- coding: utf-8 -*-

# An advanced setup script to create multiple executables and demonstrate a few
# of the features available to setup scripts
#
# hello.py is a very simple 'Hello, world' type script which also displays the
# environment in which the script runs
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

import sys
from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'compressed': True,
        'includes': [
            'hotkeys',
            'multiprocessing',
            'sys',
            'os',
            'random',
            'time',
            're',
            'select',
            'socket',
            'threading',
            'ctypes',
            'win32con',
            'hashlib',
            'subprocess',
            'nice_update'
        ],
        'path': sys.path + ['modules']
    }
}

executables = [
    Executable(	script='Lekker_Voten.py',
				compress=True,
				icon='lekker_voten.ico'),
    #Executable('advanced_2.py')
]

setup(name='Niceguys voting',
      version='1.0',
      description='Niceguys voting, Twitch votes made easy',
      options=options,
      executables=executables,
      )
