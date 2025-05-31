#!/usr/bin/env python3
import os
import sys
import pathlib
import traceback


class Config:
    def __init__(self):
        self._config = pathlib.Path(os.path.expanduser("~/.ssh/config"))
        self._items = None

    def __repr__(self) -> str:
        tmp = list()
        for item in self._items:
            item = list(map(lambda item: "{} {}".format(*item), item.items()))
            tmp.append("\n".join(item))

        return '\n\n'.join(tmp)

    def __str__(self) -> str:
        return self.__repr__()

    def load_config(self) -> None:
        data = self._config.read_text()
        items = map(lambda item: item.split("\n"), filter(None, data.split("\n\n")))
        self._items = [dict(map(lambda item: filter(None, item.split(" ")), item)) for item in items]

    def save_config(self) -> None:
        self._config.parent.mkdir(parents=True, exist_ok=True)
        self._config.write_text(str(self))


try:
    ssh = Config()
    ssh.load_config()
    print(ssh)

except Exception:
    traceback.print_exc()
    sys.exit(1)
