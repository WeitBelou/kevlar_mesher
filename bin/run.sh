#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

IMAGE=kevlar_solver
VOLUME=kevlar_solver
CONTAINER=kevlar_solver

docker build -t "${IMAGE}" .

docker stop ${CONTAINER} || true

docker run --rm \
    --name "${CONTAINER}" \
    -v "$(pwd)/out:/app/out" \
    ${IMAGE}
