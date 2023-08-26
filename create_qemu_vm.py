#!/usr/bin/env python3
import os
import sys
import pathlib
import argparse
import traceback
import subprocess


class VM:
    def __init__(self, id: str) -> None:
        self._root_dir = pathlib.Path(os.environ.get("QEMU_BASE_DIR", os.path.expanduser("~/qemu")))
        self._iso_dir = pathlib.Path(os.environ.get("QEMU_ISO_DIR", self._root_dir.joinpath("iso")))
        self._vms_dir = pathlib.Path(os.environ.get("QEMU_VM_DIR", self._root_dir.joinpath("vms")))

        self.id = id
        self.boot = ""
        self.cores = "1"
        self.memory = "2G"
        self.network = "virbr0"
        self.disk_size = "20G"
        self.disk_type = "qcow2"

    def __repr__(self) -> str:
        return '''\
   ID: "{vm_id}"
   Monitor: "telnet://{vm_address}:{mon_port}"
   Access: "spice://{vm_address}:{vm_port}"
   Cores: "{vm_cores}"
   Memory: "{vm_memory}"
   Network: "{vm_network}" ({vm_mac})
   Boot: "{vm_iso}"
   Disk: "{disk_path}" ({disk_size})
'''.format(
        vm_id=self.id,
        vm_iso=self.get_boot_path(),
        vm_cores=self.cores,
        vm_memory=self.memory,
        vm_network=self.network,
        disk_path=self.get_disk_path(),
        disk_size=self.disk_size,
        vm_mac=self.get_mac_address(),
        vm_address="127.0.0.1",
        vm_port="10{}".format(self.id),
        mon_port="20{}".format(self.id)
    )

    def __str__(self) -> str:
        return self.__repr__()

    def get_mac_address(self) -> str:
        tmp = "{:06X}".format(int(self.id))
        return "{}:{}".format("02:13:BC", ":".join([tmp[0:2], tmp[2:4], tmp[4:6]]))

    def get_disk_path(self) -> pathlib.Path:
        return self._vms_dir.joinpath("vm-{}-001.{}".format(self.id, self.disk_type))

    def get_script_path(self) -> pathlib.Path:
        return self._vms_dir.joinpath("{}-vm-run.sh".format(self.id))

    def get_boot_path(self) -> str:
        file = self._iso_dir.joinpath(self.boot)
        return str(file) if file.is_file() else ""

    def create_base_dirs(self) -> None:
        self._root_dir.mkdir(exist_ok=True)
        self._iso_dir.mkdir(exist_ok=True)
        self._vms_dir.mkdir(exist_ok=True)

    def create_disk(self) -> None:
        if not self.get_disk_path().exists():
            cmd = subprocess.Popen(
                ['/usr/bin/qemu-img', 'create', '-f', self.disk_type, str(self.get_disk_path()), self.disk_size],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
            )

            cmd.wait()
            print("Created:", self.get_disk_path())

    def create_script(self) -> None:
        template = '''\
#!/bin/bash
VMISO="{vm_iso}"

echo -e "{vm_id} ({vm_mac})"
echo -e "remmina -c spice://{vm_address}:{vm_port}"
echo -e "ncat -t {vm_address} {mon_port}"

qemu-system-x86_64 -nodefaults \\
-boot "order=c,menu=on" -monitor "telnet:{vm_address}:{mon_port},server,nowait" \\
-smp "sockets=1,cores={vm_cores}" -m "{vm_memory}" -vga qxl \\
-cpu qemu64-v1 -machine "type=q35,accel=kvm" \\
-name "{vm_id}" -pidfile "{vm_pid}" -daemonize \\
-drive "if=ide,media=cdrom,file=$VMISO" \\
-drive "if=virtio,index=0,media=disk,file={vm_disk}" \\
-device "virtio-net,netdev=eth0,mac={vm_mac}" \\
-netdev "bridge,id=eth0,br={vm_network}" \\
-spice "addr={vm_address},port={vm_port},disable-ticketing=on"
'''

        data = template.format(
            vm_id=self.id,
            vm_iso=self.get_boot_path(),
            vm_pid=self._vms_dir.joinpath("{}.pid".format(self.id)),
            vm_cores=self.cores,
            vm_memory=self.memory,
            vm_network=self.network,
            vm_disk=self.get_disk_path(),
            vm_mac=self.get_mac_address(),
            vm_address="127.0.0.1",
            vm_port="10{}".format(self.id),
            mon_port="20{}".format(self.id)
        )

        file = self.get_script_path()
        if not file.exists():
            print("Created:", file)
            file.write_text(data)
            file.chmod(int("755", base=8))


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("vm_id", help="Set VM id.")
    parser.add_argument("--iso", dest="vm_boot", default="", help="Set VM boot image.")
    parser.add_argument("--cpu", dest="vm_cores", default="1", help="Set VM cpu cores. (Default: 1)")
    parser.add_argument("--mem", dest="vm_memory", default="2G", help="Set VM memory. (Default: 2G)")
    parser.add_argument("--net", dest="vm_network", default="virbr0", help="Set VM bridge. (Default: virbr0)")
    parser.add_argument("--size", dest="disk_size", default="20G", help="Set disk size. (Default: 20G)")
    parser.add_argument("--type", dest="disk_type", choices=["qcow2", "raw"], default="qcow2", help="Set disk type. (Default: qcow2)")
    return parser.parse_args()


try:
    args = get_args()

    qemu = VM(args.vm_id)
    qemu.boot = args.vm_boot
    qemu.cores = args.vm_cores
    qemu.memory = args.vm_memory
    qemu.network = args.vm_network
    qemu.disk_size = args.disk_size
    qemu.disk_type = args.disk_type

    qemu.create_base_dirs()
    qemu.create_disk()
    qemu.create_script()
    print("VM info:\n", qemu, sep="")

except Exception:
    traceback.print_exc()
    sys.exit(1)
