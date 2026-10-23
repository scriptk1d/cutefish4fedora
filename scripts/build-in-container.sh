#!/usr/bin/env bash
# Runs scripts/build-one.sh in a throwaway Fedora container. CI entry point.
#
#   scripts/build-in-container.sh cutefish-dm
#   IMAGE=fedora:44 JOBS=8 scripts/build-in-container.sh cutefish-toolkit
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
name=${1:?usage: build-in-container.sh <spec-name>}
image=${IMAGE:-fedora:44}
jobs=${JOBS:-$(nproc)}

engine=${ENGINE:-}
if [ -z "$engine" ]; then
    if command -v podman >/dev/null 2>&1; then
        engine=podman
    elif command -v docker >/dev/null 2>&1; then
        engine=docker
    else
        echo "podman or docker is required" >&2
        exit 1
    fi
fi

security=()
if [ "$engine" = podman ]; then
    security=(--security-opt label=disable)
fi

run=(
    "$engine" run --rm
    -v "$root":/work
    -w /work
    "${security[@]}"
    -e "JOBS=$jobs"
    -e "BUILD_SRPMS=${BUILD_SRPMS:-0}"
)

if [ "$engine" = docker ] && [ "$(id -u)" -ne 0 ]; then
    run+=(-e "HOST_UID=$(id -u)" -e "HOST_GID=$(id -g)")
fi

echo "== $engine $image: $name"
exec "${run[@]}" "$image" bash scripts/build-one.sh "$name"
