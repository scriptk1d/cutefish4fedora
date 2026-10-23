%global repo xdg-desktop-portal-cutefish
%global commit 03d019c0bf5cb875881f852b6a74e2b1670a5949
%global shortcommit 03d019c
%global commitdate 20261020

%global debug_package %{nil}

Name:           xdg-desktop-portal-cutefish
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        XDG desktop portals for the Cutefish desktop

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  cutefish-toolkit-devel

BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdrm)

Requires:       xdg-desktop-portal

%description
The Cutefish backend for xdg-desktop-portal: the file chooser, screen
sharing, settings and inhibit portals for sandboxed and browser
applications.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libexecdir}/xdg-desktop-portal-cutefish
%{_datadir}/xdg-desktop-portal/portals/cutefish.portal
%{_datadir}/xdg-desktop-portal/cutefish-portals.conf
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.cutefish.service
%{_userunitdir}/xdg-desktop-portal-cutefish.service

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261020git03d019c
- Initial package, pinned to upstream main 03d019c.
