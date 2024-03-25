#!/usr/bin/env python3
import os
import sys
import json
import logging
import traceback
import subprocess

#from urllib import request


def configure_logger() -> None:
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S', level=log_level
    )


def exec_command(args: list) -> str:
    logging.info("Run: {}".format(" ".join(args)))
    cmd = subprocess.Popen(
        args=args, shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    status = cmd.wait()
    if status:
        print(cmd.stderr.read().decode(), file=sys.stderr)
        raise Exception("Command exit status: {} != 0".format(status))

    else:
        out = cmd.stdout.read()
        return out.decode()


def filter_output(data: list) -> list:
    logging.debug("Run: filter_output()")

    tmp = []
    tmp.extend(filter(lambda item: item["outdated"], data))
    tmp.extend(filter(lambda item: item["deprecated"], data))
    return tmp


def format_output(data: list) -> str:
    logging.debug("Run: format_output()")

    outdated = []
    deprecated = []

    for item in data:
        chart = item["chartName"]
        release = item["release"]
        namespace = item["namespace"]
        installed = item["Installed"]["version"]
        latest = item["Latest"]["version"]

        if item["outdated"]:
            outdated.append("- {}/{}/{} ({}, {})".format(namespace, chart, release, installed, latest))

        else:
            deprecated.append("- {}/{}/{} ({}, {})".format(namespace, chart, release, installed, latest))

    outdated_str = "Outdated:\n{}".format("\n".join(outdated))
    deprecated_str = "Deprecated:\n{}".format("\n".join(deprecated))
    return "{}\n{}".format(outdated_str, deprecated_str)


try:
    configure_logger()
    data = json.loads(exec_command(["nova", "find", "--helm", "--format=json"]))
    print(format_output(filter_output(data)))

except Exception:
    logging.error(traceback.format_exc())
    sys.exit(1)
