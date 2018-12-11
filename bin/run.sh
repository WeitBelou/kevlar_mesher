#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

IMAGE=kevlar_solver
VOLUME=kevlar_solver
CONTAINER=kevlar_solver

docker build -t "${IMAGE}" .

docker rm ${CONTAINER} || true
docker volume rm ${VOLUME} || true

docker volume create ${VOLUME}

docker run --name "${CONTAINER}" -v "${VOLUME}:/app/out" ${CONTAINER}

docker cp "${CONTAINER}:/app/out" out
