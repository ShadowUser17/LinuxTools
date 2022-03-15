#!/usr/bin/env python3
import typing
import pathlib
import argparse
import traceback
import subprocess


class DirCollection:
    def __init__(self, base_dir: str, exclude_list: list) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()
        self._exclude = tuple(exclude_list)


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
                sub_items = list(filter(lambda it: not (str(it) in self._exclude), sub_items))
                tmp_data.extend(sub_items)

        self._list = tmp_data


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_base', help='Set repositories collection directory.')
    parser.add_argument('-e', dest='dir_file', default='', help='Set repositories exclude list.')
    return parser.parse_args()


def get_exclude_list(dir_file) -> list:
    dir_file = pathlib.Path(dir_file)
    dir_list = list()

    if not dir_file.is_file():
        return dir_list

    with dir_file.open('r') as fd:
        for line in fd:
            dir_list.append(line.rsplit())

    return dir_list


if __name__ == '__main__':
    try:
        args = get_args()
        exclude_list = get_exclude_list(args.dir_file)

        dirs = DirCollection(args.dir_base, exclude_list)
        dirs.update()

        for item in dirs:
            print(item)

    except Exception:
        traceback.print_exc()
