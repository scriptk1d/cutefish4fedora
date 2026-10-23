%global repo terminal
%global commit bd1d32202d66899d5ba0af55f00d871cc8d9b32c
%global shortcommit bd1d322
%global commitdate 20261022

%global debug_package %{nil}

Name:           cutefish-terminal
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Terminal emulator for the Cutefish desktop

License:        GPL-3.0-only
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext
BuildRequires:  cutefish-toolkit-devel

BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libpcre2-16)
BuildRequires:  pkgconfig(xkbcommon)

%description
The Cutefish terminal emulator, built on the Konsole emulator core by way of
qmltermwidget.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_bindir}/cutefish-terminal
%{_datadir}/applications/cutefish-terminal.desktop
%{_datadir}/cutefish-terminal/color-schemes
%{_datadir}/cutefish-terminal/kb-layouts

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022gitbd1d322
- Initial package, pinned to upstream main bd1d322.
