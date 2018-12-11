#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

docker build -t kevlar_solver .

OUTDIR=${OUTDIR:-out}

docker rm kevlar_solver || true

docker run --name kevlar_solve \
    --rm -v "$(pwd)/out:/app/out" \
    -e HOST_UID=${UID} \
    -e OUTDIR=${OUTDIR} kevlar_solver
