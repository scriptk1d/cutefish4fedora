%global repo cutefish-framework
%global commit c138da60f59f906b91def406168460ce3cedd1c2
%global shortcommit c138da6
%global commitdate 20261020

%global debug_package %{nil}

Name:           cutefish-framework
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        System service clients and file operations for Cutefish

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz
Patch0:         cutefish-framework-0001-audio-include-spa-pod-iter.patch

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext
BuildRequires:  cutefish-toolkit-devel

BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libpng)

%description
Clients for the system services Cutefish talks to (AccountsService, UPower,
NetworkManager, BlueZ, PipeWire, ...) and the file-operation library the file
manager is built on.

%package devel
Summary:        Development files for the Cutefish framework
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cutefish-toolkit-devel
# CutefishClientaudioTargets.cmake records the PipeWire and SPA include paths
# as absolute paths, so consumers need those headers installed.
Requires:       pkgconfig(libpipewire-0.3)
Requires:       pkgconfig(libspa-0.2)

%description devel
Headers and CMake packages for the CutefishClients and CutefishFiles
libraries.

%prep
%setup -q -n %{repo}-%{commit}
%patch -P 0 -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/libcutefish-*.so.*

%files devel
%{_libdir}/libcutefish-*.so
%{_includedir}/cutefish
%{_libdir}/cmake/CutefishClients
%{_libdir}/cmake/CutefishFiles

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261020gitc138da6
- Initial package, pinned to upstream main c138da6.
