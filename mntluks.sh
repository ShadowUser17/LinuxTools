#!/bin/bash
LOOP="/dev/loop1"
LUKS=""
CRYPT="secdat1"
MOUNT=""
MAPPER="/dev/mapper/$CRYPT"


function open {
	[[ -e "$LOOP" ]] || modprobe loop

	[[ -e "$LUKS" ]] && {
		losetup "$LOOP" "$LUKS" && cryptsetup open "$LOOP" "$CRYPT" && {

			[[ -e "$MAPPER" && -e "$MOUNT" ]] && mount "$MAPPER" "$MOUNT" && echo "Open..."
		}
	}
}

function close {
	$(mount | grep -q "$MOUNT") && {
		umount -f "$MOUNT" && cryptsetup close "$CRYPT" && losetup -d "$LOOP" && echo "Closed!"
	}
}

#set -x
if [[ "$UID" -eq "0" ]]; then
	case "$1" in
	"open") open ;;
	"close") close ;;
	*) echo -e "$0 <open | close>" ;;
	esac
fi
#set +x
