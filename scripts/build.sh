#!/usr/bin/env bash
# Runs scripts/build-inside.sh in a Fedora container.
#
#   scripts/build.sh              # fedora:44, all components
#   IMAGE=fedora:43 scripts/build.sh
#   JOBS=8 scripts/build.sh
#   BUILD_SRPMS=1 scripts/build.sh
#
# podman is preferred: rootless podman maps the container's root to the
# invoking user, so SOURCES/, dist/ and .build/ stay owned by you. With docker
# the script chowns those directories back after the build.
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
image=${IMAGE:-fedora:44}
jobs=${JOBS:-$(nproc)}

if command -v podman >/dev/null 2>&1; then
    engine=podman
elif command -v docker >/dev/null 2>&1; then
    engine=docker
else
    echo "podman or docker is required" >&2
    exit 1
fi

run=(
    "$engine" run --rm
    -v "$root":/work
    -w /work
    --security-opt label=disable
    -e "JOBS=$jobs"
    -e "RESUME=${RESUME:-0}"
    -e "BUILD_SRPMS=${BUILD_SRPMS:-0}"
)

if [ "$engine" = docker ] && [ "$(id -u)" -ne 0 ]; then
    run+=(-e "HOST_UID=$(id -u)" -e "HOST_GID=$(id -g)")
fi

echo "== $engine $image"
exec "${run[@]}" "$image" bash scripts/build-inside.sh
