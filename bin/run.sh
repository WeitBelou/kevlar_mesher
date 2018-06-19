#!/usr/bin/env bash

set -euo pipefail

docker build -t kevlar_solver .

docker run --rm -v "$(pwd)/out:/app/out" -e HOST_UID=${UID} kevlar_solver