#!/usr/bin/env python3
import os
import queue
import typing
import pathlib
import argparse
import traceback
import threading
import subprocess


class GitCollection:
    def __init__(self, base_dir: str) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()

    def __iter__(self) -> typing.Iterator:
        return map(lambda it: str(it.parent), self._list)

    def update(self) -> None:
        for sub_dir in self._base.iterdir():
            if sub_dir.is_dir():
                sub_items = filter(lambda it: it.is_dir(), sub_dir.iterdir())
                sub_items = map(lambda it: it.joinpath('.git'), sub_items)
                sub_items = filter(lambda it: it.exists(), sub_items)
                self._list.extend(sub_items)


class GitUpdate:
    def __init__(self, git_list: GitCollection) -> None:
        self._list = list(git_list)
        self._fail = list()

        self._queue = queue.Queue()
        self._cpus = os.cpu_count()

        if not self._cpus:
            self._cpus = 2

    def _git_exec(self) -> None:
        while not self._queue.empty():
            git_repo = self._queue.get()

            cmd = subprocess.Popen(
                ['/usr/bin/git', 'pull', 'origin', '--rebase'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=git_repo, shell=False
            )

            if cmd.wait():
                self._fail.append(git_repo)

            print('Repo:', git_repo)
            self._queue.task_done()

    def update(self) -> None:
        print('Repositories:', len(self._list))

        for item in self._list:
            self._queue.put(item)

        for tid in range(self._cpus):
            thr_item = threading.Thread(target=self._git_exec)
            print('Start worker:', tid)
            thr_item.start()

        self._queue.join()

        if self._fail:
            print('\nUpdate failure:')
            for item in self._fail:
                print('-', item)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_base', help='Set repositories collection directory.')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()

        dirs = GitCollection(args.dir_base)
        dirs.update()

        repos = GitUpdate(dirs)
        repos.update()

    except Exception:
        traceback.print_exc()
