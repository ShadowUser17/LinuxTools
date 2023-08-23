#!/usr/bin/env python3
import subprocess
import traceback
import json


def list_forks() -> list:
    cmd = subprocess.Popen(
        ["gh", "repo", "list", "--fork", "--json", "nameWithOwner,defaultBranchRef"],
        shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    (out, _) = cmd.communicate()
    return list(map(lambda item: [item["nameWithOwner"], item["defaultBranchRef"]["name"]], json.loads(out)))


def sync_fork(repo_name: str, repo_branch: str) -> int:
    cmd = subprocess.Popen(
        ["gh", "repo", "sync", repo_name, "--force", "--branch", repo_branch], shell=False
    )

    return cmd.wait()


try:
    for (name, branch) in list_forks():
        sync_fork(name, branch)

except Exception:
    traceback.print_exc()
