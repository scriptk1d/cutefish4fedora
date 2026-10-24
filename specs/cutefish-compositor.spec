%global repo cutefish-compositor
%global commit f7f1f14a38e9a9deb6f8ce34108598d21c06736a
%global shortcommit f7f1f14
%global commitdate 20261022

%global debug_package %{nil}

Name:           cutefish-compositor
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Wayland compositor, window manager and shell for Cutefish

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz
Patch0:         cutefish-compositor-0001-clipboard-include-cstdint.patch

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext
BuildRequires:  cutefish-toolkit-devel
BuildRequires:  cutefish-framework-devel
BuildRequires:  pam-devel

BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-shape)
BuildRequires:  pkgconfig(xcb-sync)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(icu-i18n)

Requires:       xkeyboard-config

%description
The Cutefish Wayland compositor: window management, the status bar, dock,
launcher and lock screen. It also runs X11 applications through Xwayland.

%prep
%setup -q -n %{repo}-%{commit}
%patch -P 0 -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE LICENSE.chromium LICENSE.sommelier
%{_bindir}/cutefish-compositor
%{_bindir}/cutefish-displayctl
%{_bindir}/cutefish-screenshot
%{_libexecdir}/cutefish-auth-helper
%config(noreplace) %{_sysconfdir}/pam.d/cutefish-auth
%{_datadir}/cutefish-compositor/shell
%{_datadir}/licenses/cutefish-compositor/input-method-unstable-v2.xml
%{_datadir}/licenses/cutefish-compositor/virtual-keyboard-unstable-v1.xml
%{_datadir}/licenses/cutefish-compositor/xwayland-shell-v1.xml
%{_datadir}/applications/cutefish-screenshot.desktop

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022git0c27874
- Initial package, pinned to upstream main 0c27874.
