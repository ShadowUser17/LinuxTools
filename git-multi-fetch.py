#!/usr/bin/env python3
import typing
import pathlib
import argparse
import traceback
import threading
import subprocess
import multiprocessing


class GitCollection:
    def __init__(self, base_dir: str, exclude_list: list) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()
        self._exclude = tuple(exclude_list)


    def __iter__(self) -> typing.Iterator:
        return map(lambda it: it.parent, self._list)


    def update(self) -> int:
        tmp_data = list()

        for item in self._base.iterdir():
            if item.is_dir():
                sub_items = list(filter(lambda it: it.is_dir(), item.iterdir()))
                sub_items = list(map(lambda it: it.joinpath('.git'), sub_items))
                sub_items = list(filter(lambda it: it.exists(), sub_items))
                sub_items = list(filter(lambda it: not (str(it) in self._exclude), sub_items))
                tmp_data.extend(sub_items)

        self._list = tmp_data
        return len(self._list)


class GitUpdate:
    def __init__(self, git_list: GitCollection) -> None:
        self._list = list(git_list)
        cpus = multiprocessing.cpu_count()
        self._lock = threading.Semaphore(cpus)


    def _git_exec(self, git_repo: pathlib.Path) -> None:
        self._lock.acquire()

        cmd = subprocess.Popen(
            ['/usr/bin/git', 'pull', 'origin', '--rebase'],
            cwd=str(git_repo), shell=False
        )

        print('Repo:', git_repo, 'Status:', cmd.wait())
        self._lock.release()


    def update(self) -> None:
        thr_list = list()

        for item in self._list:
            thr_item = threading.Thread(target=self._git_exec, args=(item,))
            thr_list.append(thr_item)
            thr_item.start()

        for item in thr_list:
            item.join()


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

        dirs = GitCollection(args.dir_base, exclude_list)
        dirs.update()

        repos = GitUpdate(dirs)
        repos.update()

    except Exception:
        traceback.print_exc()
