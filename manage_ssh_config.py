#!/usr/bin/env python3
import os
import sys
import pathlib
import argparse
import traceback


class ConfigManager:
    def __init__(self):
        self._config = pathlib.Path(os.environ.get("SSH_CONFIG", "~/.ssh/config"))
        self._config = self._config.expanduser()
        self.load_config()

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

    def add_item(self, host: str) -> None:
        if not self.get_item(host):
            self._items.append({"Host": host})

    def get_item(self, host: str) -> dict:
        item = list(filter(lambda item: item.get("Host", "") == host, self._items))
        return item[0] if item else {}

    def del_item(self, host: str) -> None:
        item = self.get_item(host)
        if item:
            self._items.remove(item)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["ls", "get", "add", "del"], help="Set action.")
    parser.add_argument("--host", dest="hostname", help="Set hostname.")
    # parser.add_argument("--user", dest="username", help="Set username.")
    # parser.add_argument("--pkey", dest="ssh_pkey", help="Set path to key.")
    return parser.parse_args()


def print_item(item: dict) -> None:
    for (key, val) in item.items():
        print(key, val)


try:
    args = get_args()
    config = ConfigManager()

    if args.cmd == "ls":
        print(config)

    elif args.cmd == "get":
        print_item(config.get_item(args.hostname))

    elif args.cmd == "add" and args.hostname:
        config.add_item(args.hostname)
        config.save_config()
        print_item(config.get_item(args.hostname))

    elif args.cmd == "del" and args.hostname:
        config.del_item(args.hostname)
        config.save_config()
        print_item(config.get_item(args.hostname))

except Exception:
    traceback.print_exc()
    sys.exit(1)
