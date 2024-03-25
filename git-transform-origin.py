#!/usr/bin/env python3
from urllib import parse as urllib

import typing
import pathlib
import argparse
import traceback


class GitCollection:
    def __init__(self, base_dir: str) -> None:
        self._base = pathlib.Path(base_dir)
        self._list = list()

    def __iter__(self) -> typing.Iterator:
        return iter(self._list)

    def update(self) -> None:
        sub_items = filter(lambda it: it.is_dir(), self._base.iterdir())
        sub_items = map(lambda it: it.joinpath('.git/config'), sub_items)
        self._list = list(filter(lambda it: it.exists(), sub_items))


class GitTransform:
    def __init__(self, git_list: GitCollection) -> None:
        self._list = iter(git_list)
        self._stat = False

    def _load_config(self, cfg_path: pathlib.Path) -> list:
        git_data = list()

        with cfg_path.open('r') as fd:
            lines = map(str.lstrip, fd)
            lines = map(str.rstrip, lines)
            git_data.extend(filter(None, lines))

        return git_data

    def _transform_config(self, git_conf_data: list) -> list:
        template = 'git@{}:{}'
        git_data = list()
        self._stat = False

        for line in git_conf_data:
            if line.startswith('url'):
                tmp = line.split()
                url = urllib.urlparse(tmp[-1])

                if not url.netloc:
                    git_data.append(line)

                else:
                    tmp[-1] = template.format(url.netloc, url.path[1:])
                    git_data.append(' '.join(tmp))
                    self._stat = True

            else:
                git_data.append(line)

        return git_data

    def _save_config(self, cfg_path: pathlib.Path, git_data: list) -> None:
        with cfg_path.open('w') as fd:
            for line in git_data:
                if line.startswith('['):
                    print(line, sep='', file=fd)

                else:
                    print('\t', line, sep='', file=fd)

    def transform(self) -> None:
        for item in self._list:
            config = self._load_config(item)
            config = self._transform_config(config)

            if self._stat:
                self._save_config(item, config)
                print('Repo: ', item, ': updated', sep='')

            else:
                print('Repo: ', item, ': ignored', sep='')


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_base', help='Set repositories collection directory.')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()

        dirs = GitCollection(args.dir_base)
        dirs.update()

        repos = GitTransform(dirs)
        repos.transform()

    except Exception:
        traceback.print_exc()
