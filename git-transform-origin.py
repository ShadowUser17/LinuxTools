#!/usr/bin/env python3
import typing
import pathlib
import argparse
import traceback


class DirCollection:
    def __init__(self, base_dir: str) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()


    def __iter__(self) -> typing.Iterator:
        return iter(self._list)


    def __len__(self) -> int:
        return len(self._list)


    def pop(self) -> pathlib.Path:
        return self._list.pop()


    def update(self) -> int:
        sub_items = filter(lambda it: it.is_dir(), self._base.iterdir())
        sub_items = map(lambda it: it.joinpath('.git/config'), sub_items)
        sub_items = list(filter(lambda it: it.exists(), sub_items))

        self._list = sub_items
        return len(self._list)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_base', help='Set repositories collection directory.')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()

        dirs = DirCollection(args.dir_base)
        dirs.update()

        for item in dirs:
            print(item)

    except Exception:
        traceback.print_exc()
