#!/usr/bin/env python3
import sys
import pathlib
import argparse
import traceback
import subprocess


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_base", help="Set repository base dir.")
    parser.add_argument("repo_list", help="Set repository list file.")
    return parser.parse_args()


def read_repo_list(filename: str) -> list:
    data = pathlib.Path(filename).read_text()
    return list(filter(None, data.split("\n")))


def clone_repo(repo_name: str, base_dir: str) -> int:
    cmd = subprocess.Popen(
        ['/usr/bin/git', 'clone', repo_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=base_dir, shell=False
    )

    return cmd.wait()


try:
    args = get_args()

    for repo_name in read_repo_list(args.repo_list):
        print("Clone {}: ".format(repo_name), end="")
        print(clone_repo(repo_name, args.repo_base))

except Exception:
    traceback.print_exc()
    sys.exit(1)
