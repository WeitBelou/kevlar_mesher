#!/usr/bin/env bash

set -euo pipefail

: ${HOST_UID:?"HOST_UID has to be set"}

OUTDIR=out

fix_permissions() {
    rv=$?
    chown -R ${HOST_UID} ${OUTDIR}
    exit ${rv}
}
trap fix_permissions INT TERM EXIT

python -m kevlar_mesher -c config.yaml