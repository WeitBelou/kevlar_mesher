#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

IMAGE='kevlar_solver.img'

sudo singularity build "${IMAGE}" Singularity
chmod +x "${IMAGE}"
"./${IMAGE}" --bind "$(pwd)/out:/app/out"