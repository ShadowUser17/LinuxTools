#!/usr/bin/env python3
import os
import sys
import pathlib
import traceback


class Config:
    def __init__(self):
        self._config = pathlib.Path(os.path.expanduser("~/.ssh/config"))


try:
    pass

except Exception:
    traceback.print_exc()
    sys.exit(1)
