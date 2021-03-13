#!/usr/bin/env python3
import os
import pathlib
import traceback


try:
    if os.getuid():
        raise PermissionError('Run it as root!')
 
    pacman = pathlib.Path('/var/cache/pacman/pkg')
 
    for file in pacman.glob('*'):
        print('Remove:', file.name)
        file.unlink()

except Exception:
    traceback.print_exc()

