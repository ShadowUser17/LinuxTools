TBOX_TOR="socks5://127.0.0.1:9050"
TBOX_DIR="${HOME}/Pentest/tmpfiles"

TBOX_PYENV=".venv"
TBOX_PYREQ="requirements.txt"

TBOX_VPN="$(ip -j address show dev tun0 | jq -r '.[0].addr_info[0].local')"
TBOX_PORT1="4444"
TBOX_PORT2="4445"

function tbox_torip {
    echo "$(curl --proxy ${TBOX_TOR} ident.me)"
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

function tbox_pyenv {
    [[ -n "${TBOX_PYENV}" ]] && {
        TBOX_PYPIP="./${TBOX_PYENV}/bin/pip3"
        python3 -m venv "${TBOX_PYENV}"

        [[ $? -eq 0 && -e "${TBOX_PYPIP}" ]] && "${TBOX_PYPIP}" install --upgrade pip
        [[ $? -eq 0 && -e "${TBOX_PYREQ}" ]] && "${TBOX_PYPIP}" install -r "${TBOX_PYREQ}"
        [[ $? -eq 0 ]] && "${TBOX_PYPIP}" list
    }
}
