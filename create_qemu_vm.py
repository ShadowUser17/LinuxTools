#!/usr/bin/env python3
__version__ = "1.0.0"

import os
import sys
import pathlib
import argparse
import traceback
import subprocess


class VM:
    def __init__(self, id: str) -> None:
        self._bios_dir = pathlib.Path(os.environ.get("QEMU_BIOS_IMG", "/usr/share/OVMF/OVMF_CODE.fd"))
        self._root_dir = pathlib.Path(os.environ.get("QEMU_BASE_DIR", os.path.expanduser("~/qemu")))
        self._iso_dir = pathlib.Path(os.environ.get("QEMU_ISO_DIR", self._root_dir.joinpath("iso")))
        self._vms_dir = pathlib.Path(os.environ.get("QEMU_VMS_DIR", self._root_dir.joinpath("vms")))
        self._tmp_dir = pathlib.Path(os.environ.get("QEMU_TMP_DIR", self._root_dir.joinpath("tmp")))

        self.id = id
        self.iso = ""
        self.cores = "1"
        self.memory = "2G"
        self.address = "127.0.0.1"
        self.cpu_type = "qemu64-v1"
        self.cpu_opts = "avx ssse3 sse4.1 sse4.2"
        self.net_name = "virbr0"
        self.net_type = "e1000"
        self.disk_size = "20G"
        self.disk_type = "qcow2"
        self.uefi_bios = False
        self.test_mode = False
        self.write_force = False
        self.is_snapshot = False

    def __call__(self) -> str:
        if not self.test_mode:
            self.create_base_dirs()
            self.create_disk()
            self.create_snapshot()
            self.create_script()

        return self.__repr__()

    def __repr__(self) -> str:
        return '''\
   ID: "{vm_id}"
   Monitor: "telnet://{vm_address}:{mon_port}"
   Access: "spice://{vm_address}:{vm_port}"
   CPU: "{cpu_type}: {vm_cores}"
   BIOS: "{vm_bios}"
   Options: "{cpu_opts}"
   Memory: "{vm_memory}"
   Network: "{net_name}" ({net_type}: {net_mac})
   Boot: "{vm_iso}"
   Disk: "{disk_path}" ({disk_size})
'''.format(
        vm_id=self.id,
        vm_iso=self.get_boot_path(),
        vm_cores=self.cores,
        cpu_type=self.cpu_type,
        cpu_opts=self.cpu_opts,
        vm_bios=self.get_bios_path() if self.uefi_bios else "",
        vm_memory=self.memory,
        net_name=self.net_name,
        net_type=self.net_type,
        net_mac=self.get_mac_address(),
        disk_path=self.get_snapshot_path() if self.is_snapshot else self.get_disk_path(),
        disk_size=self.disk_size,
        vm_address=self.address,
        vm_port="10{}".format(self.id),
        mon_port="20{}".format(self.id)
    )

    def __str__(self) -> str:
        return self.__repr__()

    def get_mac_address(self) -> str:
        tmp = "{:06X}".format(int(self.id))
        return "{}:{}".format("02:13:BC", ":".join([tmp[0:2], tmp[2:4], tmp[4:6]]))

    def get_cpu_options(self) -> str:
        tmp = [self.cpu_type]
        tmp.extend(map(lambda item: "+{}".format(item), self.cpu_opts.split()))
        return ",".join(tmp)

    def get_bios_path(self) -> str:
        if not self._bios_dir.exists():
            raise FileExistsError("Not found: {}".format(self._bios_dir))

        return str(self._bios_dir)

    def get_disk_path(self) -> pathlib.Path:
        return self._vms_dir.joinpath("vm-{}-001.{}".format(self.id, self.disk_type))

    def get_snapshot_path(self) -> pathlib.Path:
        return self._vms_dir.joinpath("vm-{}-001-snapshot.{}".format(self.id, self.disk_type))

    def get_script_path(self) -> pathlib.Path:
        return self._vms_dir.joinpath("{}-vm-run.sh".format(self.id))

    def get_boot_path(self) -> str:
        file = self._iso_dir.joinpath(self.iso)
        return str(file) if file.is_file() else ""

    def get_sys_args(self) -> str:
        return " ".join(sys.argv[1:])

    def create_base_dirs(self) -> None:
        self._root_dir.mkdir(exist_ok=True)
        self._iso_dir.mkdir(exist_ok=True)
        self._vms_dir.mkdir(exist_ok=True)
        self._tmp_dir.mkdir(exist_ok=True)

    def create_disk(self) -> None:
        if not self.get_disk_path().exists():
            cmd = subprocess.Popen(
                ['/usr/bin/qemu-img', 'create', '-f', self.disk_type, str(self.get_disk_path()), self.disk_size],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
            )

            if cmd.wait():
                raise OSError("Disk create operation returned non-zero code!")

            print("Created:", self.get_disk_path())

    def create_snapshot(self) -> None:
        if not self.get_snapshot_path().exists() and self.is_snapshot:
            cmd = subprocess.Popen(
                ['/usr/bin/qemu-img', 'create', '-f', self.disk_type, '-b', str(self.get_disk_path()), '-F', self.disk_type, str(self.get_snapshot_path())],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
            )

            if cmd.wait():
                raise OSError("Snapshot create operation returned non-zero code!")

            print("Created:", self.get_snapshot_path())

    def create_script(self) -> None:
        template = '''\
#!/bin/bash
# {sys_args}
VMISO="{vm_iso}"

echo -e "{vm_id} ({net_mac})"
echo -e "remmina -c spice://{vm_address}:{vm_port}"
echo -e "ncat -t {vm_address} {mon_port}"

qemu-system-x86_64 -nodefaults \\
-boot "order=c,menu=on" -monitor "telnet:{vm_address}:{mon_port},server,nowait" \\
-smp "sockets=1,cores={vm_cores}" -m "{vm_memory}" -vga qxl \\
-cpu "{cpu_opts}" -machine "type=q35,accel=kvm" {vm_bios}\\
-name "{vm_id}" -pidfile "{vm_pid}" -daemonize \\
-drive "if=ide,index=0,media=cdrom,file=$VMISO" \\
-drive "if=ide,index=1,media=disk,cache=none,file={vm_disk}" \\
-device "{net_type},netdev=eth0,mac={net_mac}" \\
-netdev "bridge,id=eth0,br={net_name}" \\
-spice "addr={vm_address},port={vm_port},disable-ticketing=on"
'''

        data = template.format(
            sys_args=self.get_sys_args(),
            vm_id=self.id,
            vm_iso=self.get_boot_path(),
            vm_pid=self._vms_dir.joinpath("{}.pid".format(self.id)),
            vm_cores=self.cores,
            vm_memory=self.memory,
            cpu_opts=self.get_cpu_options(),
            net_type=self.net_type,
            net_name=self.net_name,
            net_mac=self.get_mac_address(),
            vm_bios="-bios \"{}\" ".format(self.get_bios_path()) if self.uefi_bios else "",
            vm_disk=self.get_snapshot_path() if self.is_snapshot else self.get_disk_path(),
            vm_address=self.address,
            vm_port="10{}".format(self.id),
            mon_port="20{}".format(self.id)
        )

        file = self.get_script_path()
        if not file.exists() or self.write_force:
            print("Created:", file)
            file.write_text(data)
            file.chmod(int("755", base=8))


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("vm_id", help="Set VM id.")
    parser.add_argument("--iso", dest="iso", default="", help="Set boot image.")
    parser.add_argument("--cpu", dest="cores", default="1", help="Set CPU cores.")
    parser.add_argument("--mem", dest="memory", default="2G", help="Set VM memory.")
    parser.add_argument("--cpu_type", dest="cpu_type", choices=["host", "qemu64-v1"], default="qemu64-v1", help="Set CPU type.")
    parser.add_argument("--cpu_opts", dest="cpu_opts", default="avx ssse3 sse4.1 sse4.2", help="Enable CPU features.")
    parser.add_argument("--net", dest="net_name", default="virbr0", help="Set network bridge.")
    parser.add_argument("--net_type", dest="net_type", choices=["e1000", "virtio-net"], default="e1000", help="Set network interface type.")
    parser.add_argument("--size", dest="disk_size", default="20G", help="Set disk size.")
    parser.add_argument("--type", dest="disk_type", choices=["qcow2", "raw"], default="qcow2", help="Set disk type.")
    parser.add_argument("--uefi", dest="uefi_bios", action="store_true", help="Enable UEFI bios.")
    parser.add_argument("--test", dest="test_mode", action="store_true", help="Run in test mode.")
    parser.add_argument("--force", dest="write_force", action="store_true", help="Rewrite existing script.")
    parser.add_argument("--snapshot", dest="is_snapshot", action="store_true", help="Create and boot from snapshot.")
    return parser.parse_args()


try:
    args = get_args()

    qemu = VM(args.vm_id)
    qemu.iso = args.iso
    qemu.cores = args.cores
    qemu.memory = args.memory
    qemu.cpu_type = args.cpu_type
    qemu.cpu_opts = args.cpu_opts
    qemu.net_name = args.net_name
    qemu.net_type = args.net_type
    qemu.disk_size = args.disk_size
    qemu.disk_type = args.disk_type
    qemu.uefi_bios = args.uefi_bios
    qemu.test_mode = args.test_mode
    qemu.write_force = args.write_force
    qemu.is_snapshot = args.is_snapshot

    print("VM info:\n", qemu(), sep="")

except Exception:
    traceback.print_exc()
    sys.exit(1)
