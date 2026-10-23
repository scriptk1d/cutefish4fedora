#!/usr/bin/env bash
# Builds every RPM in specs/ inside a Fedora container. Runs as root.
#
# The components are built in the order the upstream build guide uses: each
# one is installed into the container before the next is configured, so the
# later projects find the earlier ones as installed CMake packages.
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

jobs=${JOBS:-$(nproc)}
export CMAKE_BUILD_PARALLEL_LEVEL=$jobs
export RPM_BUILD_NCPUS=$jobs

echo "== build tools"
dnf -y --setopt=install_weak_deps=False install \
    rpm-build rpmdevtools redhat-rpm-config dnf5-plugins \
    curl tar gzip git python3 gettext \
    cmake cmake-rpm-macros ninja-build gcc gcc-c++ clang \
    pkgconf-pkg-config gtk-update-icon-cache

echo "== sources"
bash scripts/fetch-sources.sh

topdir=${TOPDIR:-$root/.build/rpmbuild}
rm -rf "$topdir"
mkdir -p "$topdir"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
cp "$root"/SOURCES/*.tar.gz "$topdir/SOURCES/"
cp "$root"/patches/*.patch "$topdir/SOURCES/" 2>/dev/null || true
cp "$root"/specs/*.spec "$topdir/SPECS/"

# Dependencies flow this way: every component needs the toolkit, the
# applications need the framework, the compositor and settings need both.
order=(
    cutefish-toolkit
    cutefish-framework
    cutefish-icons
    cutefish-core
    cutefish-filemanager
    cutefish-terminal
    xdg-desktop-portal-cutefish
    cutefish-settings
    cutefish-compositor
    cutefish-wallpapers
)

resume=${RESUME:-0}
if [ "$resume" = "1" ]; then
    mkdir -p "$root/dist"
    if compgen -G "$root/dist/*.rpm" >/dev/null; then
        echo "== RESUME=1: installing RPMs already in dist"
        dnf -y --setopt=install_weak_deps=False install "$root"/dist/*.rpm || \
            rpm -Uvh --replacepkgs --nodeps "$root"/dist/*.rpm
    fi
else
    rm -rf "$root/dist"
    mkdir -p "$root/dist"
fi

for name in "${order[@]}"; do
    if [ "$resume" = "1" ] && compgen -G "$root/dist/$name-*.rpm" >/dev/null; then
        echo "== $name: already built (RESUME=1)"
        continue
    fi

    spec=$topdir/SPECS/$name.spec
    echo "== $name: build dependencies"
    dnf -y --setopt=install_weak_deps=False builddep --spec "$spec"
    echo "== $name: rpmbuild"
    rpmbuild -bb --define "_topdir $topdir" "$spec"

    mapfile -t built < <(find "$topdir/RPMS" -name "$name-*.rpm" | sort)
    if [ ${#built[@]} -eq 0 ]; then
        echo "no RPMs produced for $name" >&2
        exit 1
    fi
    cp "${built[@]}" "$root/dist/"
    echo "== $name: install into the build environment"
    dnf -y --setopt=install_weak_deps=False install "${built[@]}" || \
        rpm -Uvh --replacepkgs --nodeps "${built[@]}"
done

if [ "${BUILD_SRPMS:-0}" = "1" ]; then
    echo "== source RPMs"
    for name in "${order[@]}"; do
        rpmbuild -bs --define "_topdir $topdir" "$topdir/SPECS/$name.spec"
    done
    cp "$topdir"/SRPMS/*.src.rpm "$root/dist/"
fi

# Docker runs as real root; hand the outputs back to the invoking user.
if [ -n "${HOST_UID:-}" ]; then
    chown -R "$HOST_UID:${HOST_GID:-$HOST_UID}" \
        "$root/dist" "$root/SOURCES" "$root/.cache" "$root/.build" 2>/dev/null || true
fi

echo "== done"
ls -1 "$root/dist"
