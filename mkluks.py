#!/usr/bin/env python3
import os
import sys
import pathlib
import argparse
import traceback
import subprocess


def cmd_exec(*args) -> bool:
    print("Run:", " ".join(args))
    cmd = subprocess.Popen(args, shell=False)
    return False if cmd.wait() else True


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("disk_file", help="Set disk file name")
    parser.add_argument("disk_size", type=int, help="Set disk size in GB")
    parser.add_argument("key_file", help="Set key file name")

    return parser.parse_args()


try:
    if os.getuid() != 0:
        print("You must be root!")
        sys.exit(1)

    args = get_args()
    print("Disk:", args.disk_file)
    print("Size: {}G".format(args.disk_size))
    print("Key:", args.key_file)

    disk_file = pathlib.Path(args.disk_file)
    if disk_file.exists():
        print("The disk file exists!")
        sys.exit(1)

    key_file = pathlib.Path(args.key_file)
    if key_file.exists():
        print("The key file exists!")
        sys.exit(1)

    disk_size = (args.disk_size * 1024 * 1024)
    if disk_size < 1:
        print("Incorrect disk size!")
        sys.exit(1)

    # Create key file
    if not cmd_exec("dd", "if=/dev/random", "of={}".format(key_file), "bs=1", "count=512"):
        sys.exit(3)

    # Create disk file
    if not cmd_exec("dd", "if=/dev/zero", "of={}".format(disk_file), "bs=1024", "count={}".format(disk_size), "status=progress"):
        sys.exit(3)

    if not cmd_exec("modprobe", "loop"):
        sys.exit(3)

    if not cmd_exec("losetup", "/dev/loop0", str(disk_file)):
        sys.exit(3)

    if not cmd_exec("cryptsetup", "-q", "-M", "luks2", "-h", "sha256", "-c", "twofish-xts-plain64", "-s", "512", "-d", str(key_file), "luksFormat", str(disk_file), "sec0"):
        sys.exit(3)

    if not cmd_exec("cryptsetup", "--key-file", str(key_file), "open", "/dev/loop0", "sec0"):
        sys.exit(3)

    if not cmd_exec("mkfs", "-t", "ext4", "/dev/mapper/sec0"):
        sys.exit(3)

    if not cmd_exec("cryptsetup", "close", "sec0"):
        sys.exit(3)

    if not cmd_exec("losetup", "-d", "/dev/loop0"):
        sys.exit(3)

except Exception:
    traceback.print_exc()
    sys.exit(2)
