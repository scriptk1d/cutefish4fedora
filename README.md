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
| cutefish-dm | cutefish-dm | display manager: login screen, session start |

`qt-plugins`, `text-editor`, `video-player`, `calendar`, `system-monitor` and
`cutefish-computer-use` are optional upstream and are not packaged here.

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

To build one package on its own, put the RPMs of its dependencies in `deps/`
and call the entry point the CI jobs use:

```sh
scripts/build-in-container.sh cutefish-dm
```

`scripts/build-one.sh` resolves that spec's `BuildRequires`, installs the RPMs
from `deps/` first, and copies the result to `dist/`.

## Update the pinned commits

Each spec carries its pin in the header:

```spec
%global repo cutefish-framework
%global commit c138da60f59f906b91def406168460ce3cedd1c2
%global shortcommit c138da6
%global commitdate 20261020
```

Run `scripts/update-pins.sh` to do this for all components (or pass repository
names to limit it), or let the sync workflow do it. If you edit the specs by
hand, delete the old tarball from `SOURCES/` (or the whole directory) before
building. `cutefish-toolkit.spec` also pins Skia:

```spec
%global skiabranch chrome/m156
%global skiarev 95ee33d7ec7791ab9c071675710a14fe6408ae4f
```

They must match `cutefish-toolkit/scripts/fetch-skia.sh` upstream, because
the toolkit's CMake expects `third_party/skia` at that revision.

Release numbers are `0.<commit date>git<short commit>%{?dist}`, so every
commit bump produces a newer package without changing `Version`.

## GitHub Actions

`.github/workflows/build.yml` builds every package in its own job on every
push and pull request. The jobs follow the dependency order: the toolkit
first, then the framework and the two data packages in parallel, then the
applications and `cutefish-dm` in parallel. Each job installs the RPMs built
by the previous stage from artifacts, so a failed package can be re-run on
its own from the Actions tab without rebuilding the others.

The `release` job collects the per-package artifacts into `cutefish-rpms`.
Pushing a tag that starts with `v` additionally creates a GitHub release with
the RPMs attached:

```sh
git tag v1.0-20261023
git push origin v1.0-20261023
```

`workflow_dispatch` has an `srpms` switch to include source RPMs and a
`tag_name` field that turns the run into a release once it succeeds. The Skia
source is cached by revision, so only a Skia bump pays for the checkout.

## Automatic upstream sync

`.github/workflows/sync-upstream.yml` runs every day at 03:17 UTC, and on
demand from the Actions tab. It:

1. moves every spec to the tip of the matching upstream `main` with
   `scripts/update-pins.sh`, including the Skia revision read from the
   toolkit's own `scripts/fetch-skia.sh`;
2. commits the new pins and pushes to `main` if anything moved;
3. dispatches `build.yml` for that commit. The build creates the dated tag and
   the release (`v1.0-<date>-<short commit>`) only after the RPMs are built,
   so a failing build leaves no release behind.

Pushes made with the workflow's `GITHUB_TOKEN` do not trigger other workflows,
which is why the sync step dispatches the build explicitly. Set the repository
variable `AUTO_RELEASE` to `false` to keep building on upstream changes
without publishing releases.

GitHub disables scheduled workflows after 60 days without repository
activity; run the workflow once from the Actions tab to re-enable it.

If a build fails, the new pins are already committed, so the next sync has
nothing to do. Re-run the `RPM` workflow from the Actions tab (or
`gh workflow run build.yml -f tag_name=v1.0-<date>-<short commit>`) once the
upstream problem is fixed.

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

### Using cutefish-dm

The display manager is installed but not enabled, so the current one (on
Fedora 44 KDE that is `plasmalogin`, on other spins `sddm` or `gdm`) keeps
starting the session. Installing the package creates the `cutefish-greeter`
system user and its home, and ships PAM stacks using Fedora's
`password-auth`/`system-auth` (the upstream files include the Debian
`common-*` files, which do not exist here).

To switch to it, disable the current display manager first: both claim the
`display-manager.service` alias.

```sh
readlink -f /etc/systemd/system/display-manager.service   # see the current one
sudo systemctl disable plasmalogin                        # or sddm, gdm
sudo systemctl enable cutefish-dm
sudo systemctl start cutefish-dm
```

The greeter runs on VT1 and the user session on VT2. Autologin, if wanted, is
configured in `/etc/cutefish-dm.conf`:

```ini
[Autologin]
User=cutefish
Session=cutefish-wayland
```

Removing the package leaves the greeter user and `/var/lib/cutefish-dm` in
place, as those may still hold state.

## Layout

```
specs/                 one spec per component
patches/               fixes needed by the Fedora toolchain or libraries
scripts/fetch-sources.sh   pinned tarballs into SOURCES/
scripts/update-pins.sh     moves the specs to the tip of upstream main
scripts/build-inside.sh    the full sequential build, runs in the container
scripts/build.sh           container wrapper for local use
scripts/build-one.sh       builds one spec, runs in the container
scripts/build-in-container.sh  one-package wrapper used by CI
.github/workflows/build.yml  CI: one job per package, release on v* tags
.github/workflows/sync-upstream.yml  daily pin update and release dispatch
```

## Notes

- `cutefish-framework` carries one patch: `clients/audio/audio_object.cpp`
  needs `<spa/pod/iter.h>`, which PipeWire up to 1.4 included indirectly but
  1.6 (Fedora 44) does not, and `cutefish-compositor` needs `<cstdint>` in
  `src/clipboard/selection.h` with GCC 16. The patches are in `patches/`.
- `cutefish-dm` carries one patch that rewrites its PAM stacks for Fedora
  (`password-auth`/`system-auth` instead of the Debian `common-*` includes).
  Its `%pre` creates the `cutefish-greeter` system user, and the package owns
  the greeter's home and `/var/lib/cutefish-dm`.
- Debug packages are disabled: Skia would add hundreds of megabytes of debug
  info to the toolkit package.
- `cutefish-toolkit-devel` and `cutefish-framework-devel` carry headers and
  CMake packages; the other packages are applications or data.
- The toolkit's Skia build uses the system FreeType, HarfBuzz, ICU and image
  codecs, exactly like the upstream build guide.
