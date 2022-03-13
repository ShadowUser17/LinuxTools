#!/usr/bin/env python3
import typing
import pathlib
import argparse
import traceback
import subprocess


class DirCollection:
    def __init__(self, base_dir: str) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()

    def __iter__(self) -> typing.Iterator:
        return map(lambda it: str(it.parent), self._list)

    def __len__(self) -> int:
        return len(self._list)

    def pop(self) -> pathlib.Path:
        return self._list.pop()

    def update(self) -> None:
        tmp_data = list()

        for item in self._base.iterdir():
            if item.is_dir():
                sub_items = list(filter(lambda it: it.is_dir(), item.iterdir()))
                sub_items = list(map(lambda it: it.joinpath('.git'), sub_items))
                sub_items = list(filter(lambda it: it.exists(), sub_items))
                tmp_data.extend(sub_items)

        self._list = tmp_data


def get_args() -> argparse.Namespace:
    pass


if __name__ == '__main__':
    try:
        pass

    except Exception:
        traceback.print_exc()
