#!/usr/bin/env python3
__version__ = "0.1.0"

import os
import sys
import pathlib
import datetime
import argparse
import traceback


qemu_root_dir = pathlib.Path(os.environ.get("QEMU_BASE_DIR", os.path.expanduser("~/qemu")))
qemu_iso_dir = pathlib.Path(os.environ.get("QEMU_ISO_DIR", qemu_root_dir.joinpath("iso")))
qemu_vms_dir = pathlib.Path(os.environ.get("QEMU_VMS_DIR", qemu_root_dir.joinpath("vms")))
qemu_tmp_dir = pathlib.Path(os.environ.get("QEMU_TMP_DIR", qemu_root_dir.joinpath("tmp")))


def list_items(path: pathlib.Path, format: str) -> None:
    print(path, ":", sep="")
    for item in path.iterdir():
        if item.is_file:
            stat = item.stat()
            print("\t{} {}:{}:{} {} \"{}\" \"{}\"".format(
                item.name,
                stat.st_uid,
                stat.st_gid,
                oct(stat.st_mode).lstrip("0o"),
                stat.st_size,
                datetime.datetime.fromtimestamp(stat.st_ctime).strftime(format),
                datetime.datetime.fromtimestamp(stat.st_mtime).strftime(format)
            ))

    else:
        print()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", dest="type", choices=["all", "iso", "img", "tmp"], default="all", help="Set items type.")
    parser.add_argument("--format", dest="format", default=r"%Y-%m-%d_%H:%M:%S", help="Set time format.")
    return parser.parse_args()


try:
    args = get_args()

    if args.type == "iso":
        list_items(qemu_iso_dir, args.format)

    elif args.type == "img":
        list_items(qemu_vms_dir, args.format)

    elif args.type == "tmp":
        list_items(qemu_tmp_dir, args.format)

    else:
        list_items(qemu_iso_dir, args.format)
        list_items(qemu_vms_dir, args.format)
        list_items(qemu_tmp_dir, args.format)

except Exception:
    traceback.print_exc()
    sys.exit(1)
