TBOX_TOR="socks5://127.0.0.1:9050"
TBOX_DIR="${HOME}/Pentest/tmpfiles"

TBOX_PYENV="./.venv"
TBOX_PYREQ="./requirements.txt"

TBOX_VPN="$(ip -j address show dev tun0 | jq -r '.[0].addr_info[0].local')"
TBOX_PORT1="4444"
TBOX_PORT2="4445"

TBOX_NMAP_TARGET="./target.txt"
TBOX_NMAP_REPORT_SYN="./nmap-ss.txt"
TBOX_NMAP_REPORT_VRB="./nmap-sv.txt"

function tbox_torip {
    echo "$(curl --proxy ${TBOX_TOR} ident.me)"
}

function tbox_chown {
    [[ -n "$1" ]] && \
    sudo chown "$(id -u):$(id -g)" "$1"
}

function tbox_ncat1 {
    [[ -n "${TBOX_VPN}" && -n "${TBOX_PORT1}" ]] && \
    sudo ncat -v -n -l "${TBOX_VPN}" "${TBOX_PORT1}"
}

function tbox_ncat2 {
    [[ -n "${TBOX_VPN}" && -n "${TBOX_PORT2}" ]] && \
    sudo ncat -v -n -l "${TBOX_VPN}" "${TBOX_PORT2}"
}

function tbox_pyhttp {
    [[ -n "${TBOX_VPN}" && -n "${TBOX_PORT2}" ]] && \
    sudo python3 -m http.server -b "${TBOX_VPN}" "${TBOX_PORT2}"
}

function tbox_nmap_syn {
    [[ -e "${TBOX_NMAP_TARGET}" && ! -e "${TBOX_NMAP_REPORT_SYN}" ]] && \
    sudo nmap -Pn -iL "${TBOX_NMAP_TARGET}" -oN "${TBOX_NMAP_REPORT_SYN}" -sS -p-
}

function tbox_nmap_vrb {
    [[ -e "${TBOX_NMAP_TARGET}" && ! -e "${TBOX_NMAP_REPORT_VRB}" && -n "$1" ]] && \
    sudo nmap -Pn -iL "${TBOX_NMAP_TARGET}" -oN "${TBOX_NMAP_REPORT_VRB}" -sV -sC -p "$1"
}

function tbox_pyenv {
    [[ -n "${TBOX_PYENV}" ]] && {
        TBOX_PYPIP="./${TBOX_PYENV}/bin/pip3"
        python3 -m venv "${TBOX_PYENV}"

        [[ $? -eq 0 && -e "${TBOX_PYPIP}" ]] && "${TBOX_PYPIP}" install --upgrade pip
        [[ $? -eq 0 && -e "${TBOX_PYREQ}" ]] && "${TBOX_PYPIP}" install -r "${TBOX_PYREQ}"
        [[ $? -eq 0 ]] && "${TBOX_PYPIP}" list
    }
}
