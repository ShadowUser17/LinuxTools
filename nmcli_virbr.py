#!/usr/bin/env python3
import sys
import argparse
import traceback
import subprocess


def cmd_exec(cmd: list) -> str:
    ps = subprocess.Popen(
        args=cmd, shell=False,
        stdout=subprocess.PIPE
    )

    (out, _) = ps.communicate()
    return out.decode()


def list_connections() -> list:
    raw = cmd_exec(["nmcli", "-g", "name", "connection", "show"])
    tmp = list(filter(lambda item: item.startswith("bridge"), raw.split("\n")))
    return list(map(lambda item: item.split("-")[1], tmp))


def list_address() -> list:
    raw = cmd_exec(["ip", "-4", "-br", "address"])
    tmp = list(map(lambda item: item.split(" "), raw.split("\n")))
    tmp = list(map(lambda item: list(filter(None, item)), tmp))
    tmp = list(map(lambda item: item[-1], filter(None, tmp)))
    return tmp


def create_connection(name: str, address: str) -> None:
    cmd_exec(["nmcli", "connection", "add", "type", "bridge", "ifname", name])
    cmd_exec(["nmcli", "connection", "modify", "bridge-" + name, "bridge.stp", "no"])
    cmd_exec(["nmcli", "connection", "modify", "bridge-" + name, "ipv4.addresses", address])
    cmd_exec(["nmcli", "connection", "modify", "bridge-" + name, "ipv4.method", "manual"])
    cmd_exec(["nmcli", "connection", "modify", "bridge-" + name, "ipv6.method", "disabled"])
    cmd_exec(["nmcli", "connection", "up", "bridge-" + name])


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bridge", help="Example: virbr0")
    parser.add_argument("address", help="Example: 192.168.55.1/24")
    return parser.parse_args()


try:
    args = get_args()

    if args.bridge in list_connections():
        raise ValueError("This {} already exists!".format(args.bridge))

    if args.address in list_address():
        raise ValueError("This {} already exists!".format(args.address))

    print("Creating: {} {}".format(args.bridge, args.address))
    create_connection(args.bridge, args.address)

except Exception:
    traceback.print_exc()
    sys.exit(1)
