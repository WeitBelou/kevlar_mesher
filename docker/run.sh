#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

: ${HOST_UID:?"HOST_UID has to be set"}
: ${OUTDIR:?"OUTDIR has to be set"}

fix_permissions() {
    rv=$?
    chown -R ${HOST_UID} ${OUTDIR}
    exit ${rv}
}
trap fix_permissions INT TERM EXIT

python3 -m kevlar_mesher -c config.yaml