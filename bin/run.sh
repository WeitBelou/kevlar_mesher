#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

docker build -t kevlar_solver .

OUTDIR=${OUTDIR:-out}

docker run --rm -v "$(pwd)/out:/app/out" -e HOST_UID=${UID} -e OUTDIR=${OUTDIR} kevlar_solver