#!/usr/bin/env bash
# Builds one spec inside a Fedora container. Runs as root.
#
#   scripts/build-one.sh cutefish-dm
#
# The CI jobs call this through build-in-container.sh. RPMs built by earlier
# stages are expected in deps/ and are installed before the spec's
# BuildRequires are resolved.
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

name=${1:?usage: build-one.sh <spec-name>}
spec=$root/specs/$name.spec
if [ ! -f "$spec" ]; then
    echo "no such spec: $spec" >&2
    exit 1
fi

jobs=${JOBS:-$(nproc)}
export CMAKE_BUILD_PARALLEL_LEVEL=$jobs
export RPM_BUILD_NCPUS=$jobs

echo "== build tools"
dnf -y --setopt=install_weak_deps=False install \
    rpm-build rpmdevtools redhat-rpm-config dnf5-plugins \
    curl tar gzip git python3 gettext \
    cmake cmake-rpm-macros ninja-build gcc gcc-c++ clang \
    pkgconf-pkg-config gtk-update-icon-cache

echo "== source for $name"
bash scripts/fetch-sources.sh "$name"

topdir=${TOPDIR:-$root/.build/rpmbuild-$name}
rm -rf "$topdir"
mkdir -p "$topdir"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

repo=$(sed -n 's/^%global repo \([^[:space:]]*\)$/\1/p' "$spec" | head -n1)
for file in "$root/SOURCES/$repo-"*.tar.gz "$root/SOURCES/skia-"*.tar.gz; do
    if [ -f "$file" ]; then
        cp "$file" "$topdir/SOURCES/"
    fi
done
cp "$root"/patches/*.patch "$topdir/SOURCES/" 2>/dev/null || true
cp "$spec" "$topdir/SPECS/"

if compgen -G "$root/deps/*.rpm" >/dev/null; then
    echo "== dependencies from earlier stages"
    dnf -y --setopt=install_weak_deps=False install "$root"/deps/*.rpm || \
        rpm -Uvh --replacepkgs --nodeps "$root"/deps/*.rpm
fi

echo "== $name: build dependencies"
dnf -y --setopt=install_weak_deps=False builddep --spec "$spec"

echo "== $name: rpmbuild"
rpmbuild -bb --define "_topdir $topdir" "$topdir/SPECS/$name.spec"

mkdir -p "$root/dist"
find "$topdir/RPMS" -name '*.rpm' -exec cp {} "$root/dist/" \;

if [ "${BUILD_SRPMS:-0}" = "1" ]; then
    rpmbuild -bs --define "_topdir $topdir" "$topdir/SPECS/$name.spec"
    cp "$topdir"/SRPMS/*.src.rpm "$root/dist/"
fi

# Docker runs as real root; hand the outputs back to the invoking user.
if [ -n "${HOST_UID:-}" ]; then
    chown -R "$HOST_UID:${HOST_GID:-$HOST_UID}" \
        "$root/dist" "$root/SOURCES" "$root/.build" 2>/dev/null || true
fi

echo "== done: $name"
ls -1 "$root/dist"
