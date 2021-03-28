#!/bin/bash

ITEMS=(
    "total.num.queries"
    "total.num.cachehits"
    "total.num.cachemiss"
    "total.num.prefetch"
    "total.num.recursivereplies"
    "total.requestlist.max"
    "total.requestlist.avg"
    "total.requestlist.overwritten"
    "total.requestlist.exceeded"
    "total.requestlist.current.all"
    "total.requestlist.current.user"
    "total.tcpusage"
    "num.query.a"
    "num.query.ns"
    "num.query.mx"
    "num.query.txt"
    "num.query.ptr"
    "num.query.aaaa"
    "num.query.srv"
    "num.query.soa"
    "num.answer.rcode.NOERROR"
    "num.answer.rcode.NXDOMAIN"
    "num.answer.rcode.SERVFAIL"
    "num.answer.rcode.REFUSED"
    "num.answer.rcode.nodata"
    "num.answer.secure"
)


function read_item {
    DATA=$(echo "$1" | sed 's/\./\\\./g')
    DATA=$(awk -F= "\$1~/${DATA}\$/{print \$2}" "${STAT_FILE}")
}

function send_item {
    [[ -n "$1" && -n "$2" ]] && \
    zabbix_sender -z "${ZABBIX_SERVER}" -s "${HOSTNAME}" -k "$1" -o "$2"
}

function main {
    [[ -z "$1" || -z "$2" || -z "$3" ]] && {
        echo -n "Example: "
        echo "/opt/unboundSend.sh 192.168.10.1 UnboundServer /tmp/dump_unbound_control_stats.txt"
        return 1
    }

    ZABBIX_SERVER="$1"
    HOSTNAME="$2"
    STAT_FILE="$3"

    unbound-control stats > "${STAT_FILE}"

    for I in ${ITEMS[*]}; do
        read_item "$I"
        send_item "$I" "$DATA"
    done
}

#set -x
main "$1" "$2" "$3"
#set +x
