# Cutefish RPM packaging

Fedora RPM builds for the required and recommended components of the
[Cutefish desktop](https://github.com/cutefishos). The specs pin upstream
`main` by commit; the build runs inside a Fedora container, so the host only
needs podman or docker.

Built packages:

| Package | Upstream repository | Contents |
|---|---|---|
| cutefish-toolkit | cutefish-toolkit | UI toolkit (Skia linked in), `-devel` |
| cutefish-framework | cutefish-framework | service clients, file operations, `-devel` |
| cutefish-icons | icons | default icon theme |
| cutefish-core | cutefish-core | session, services, polkit agent, screen recorder |
| cutefish-filemanager | filemanager | file manager and desktop |
| cutefish-terminal | terminal | terminal emulator |
| xdg-desktop-portal-cutefish | xdg-desktop-portal-cutefish | desktop portals |
| cutefish-settings | settings | system settings |
| cutefish-compositor | cutefish-compositor | Wayland compositor, shell, Xwayland |
| cutefish-wallpapers | wallpapers | default wallpapers |

`cutefish-dm`, `qt-plugins`, `text-editor`, `video-player`, `calendar`,
`system-monitor` and `cutefish-computer-use` are optional upstream and are
not packaged here.

## Build locally

```sh
scripts/build.sh              # podman or docker, Fedora 44
IMAGE=fedora:43 scripts/build.sh
JOBS=8 scripts/build.sh
RESUME=1 scripts/build.sh     # keep RPMs already in dist/ and skip their packages
BUILD_SRPMS=1 scripts/build.sh
```

The script:

1. runs `scripts/fetch-sources.sh`, which downloads the GitHub tarballs the
   specs pin into `SOURCES/` and packs the pinned Skia revision
   (`chrome/m156`, for `cutefish-toolkit`) into `SOURCES/skia-<rev>.tar.gz`;
2. starts `fedora:44` and runs `scripts/build-inside.sh` in it, which
   installs the build tools, then for each component resolves its
   `BuildRequires` with `dnf builddep`, builds the RPM with `rpmbuild -bb`
   and installs it into the container so the next component can find it;
3. copies the binary RPMs (and source RPMs with `BUILD_SRPMS=1`) to `dist/`.

`SOURCES/` and `.build/` are caches: the source tarballs are kept, the
rpmbuild tree is left for debugging. `rm -rf .build SOURCES` starts over.

The first component builds Skia with clang and dominates the build time.

## Update the pinned commits

Each spec carries its pin in the header:

```spec
%global repo cutefish-framework
%global commit c138da60f59f906b91def406168460ce3cedd1c2
%global shortcommit c138da6
%global commitdate 20261020
```

Set all four to the new commit, then delete the old tarball from `SOURCES/`
(or the whole directory) before building. `cutefish-toolkit.spec` also pins
Skia:

```spec
%global skiabranch chrome/m156
%global skiarev 95ee33d7ec7791ab9c071675710a14fe6408ae4f
```

They must match `cutefish-toolkit/scripts/fetch-skia.sh` upstream, because
the toolkit's CMake expects `third_party/skia` at that revision.

Release numbers are `0.<commit date>git<short commit>%{?dist}`, so every
commit bump produces a newer package without changing `Version`.

## GitHub Actions

`.github/workflows/build.yml` builds all RPMs on every push and pull
request, and uploads them as the `cutefish-rpms` artifact. Pushing a tag that
starts with `v` additionally creates a GitHub release with the RPMs attached:

```sh
git tag v1.0-20261023
git push origin v1.0-20261023
```

`workflow_dispatch` has an `srpms` switch to include source RPMs.

## Install on Fedora

```sh
sudo dnf install ./dist/*.rpm
```

Everything installs into `/usr`, as the Cutefish session expects
(`/usr/bin/cutefish-wayland-session`, `/usr/share/wayland-sessions/...`).
After installing, log out and pick **Cutefish (Wayland)** in the display
manager's session menu.

Runtime services Cutefish expects but does not package: NetworkManager,
BlueZ, UPower, power-profiles-daemon, UDisks2, PipeWire with WirePlumber,
AccountsService, polkit, xdg-desktop-portal and Xwayland. `dnf` pulls the
library dependencies the packages declare; the services above have to be
installed separately, as on any distribution.

`cutefish-dm` is not part of this repository, so the current display manager
(SDDM, GDM, LightDM) stays in place and starts the session.

## Layout

```
specs/                 one spec per component
patches/               fixes needed by the Fedora toolchain or libraries
scripts/fetch-sources.sh   pinned tarballs into SOURCES/
scripts/update-pins.sh     moves the specs to the tip of upstream main
scripts/build-inside.sh    the build itself, runs in the Fedora container
scripts/build.sh           container wrapper for local use
.github/workflows/build.yml  CI: artifacts, release on v* tags
```

## Notes

- `cutefish-framework` carries one patch: `clients/audio/audio_object.cpp`
  needs `<spa/pod/iter.h>`, which PipeWire up to 1.4 included indirectly but
  1.6 (Fedora 44) does not, and `cutefish-compositor` needs `<cstdint>` in
  `src/clipboard/selection.h` with GCC 16. The patches are in `patches/`.
- Debug packages are disabled: Skia would add hundreds of megabytes of debug
  info to the toolkit package.
- `cutefish-toolkit-devel` and `cutefish-framework-devel` carry headers and
  CMake packages; the other packages are applications or data.
- The toolkit's Skia build uses the system FreeType, HarfBuzz, ICU and image
  codecs, exactly like the upstream build guide.
