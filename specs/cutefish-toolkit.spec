%global repo cutefish-toolkit
%global commit d8a60ed3a7546094a2c40f7e24db8c3f304d53bc
%global shortcommit d8a60ed
%global commitdate 20261023

# Pinned by scripts/fetch-skia.sh in the toolkit repository.
%global skiabranch chrome/m156
%global skiarev 95ee33d7ec7791ab9c071675710a14fe6408ae4f

# Skia is linked statically into libcutefish-toolkit; its debug info would be
# hundreds of megabytes in the release artifacts.
%global debug_package %{nil}

Name:           cutefish-toolkit
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        UI toolkit for the Cutefish desktop

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz
Source1:        skia-%{skiarev}.tar.gz
Patch0:         cutefish-toolkit-0001-xdg-data-dirs.patch

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  clang
BuildRequires:  python3
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext

BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(icu-i18n)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libheif)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)

%description
The Cutefish UI toolkit: base utilities, widgets and window chrome that every
Cutefish component is built on. Skia provides the rendering.

%package devel
Summary:        Development files for the Cutefish UI toolkit
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and CMake packages needed to build applications against the Cutefish
UI toolkit.

%prep
%setup -q -n %{repo}-%{commit}
%patch -P 0 -p1
mkdir -p third_party
tar -xzf %{SOURCE1} -C third_party
mv third_party/skia-%{skiarev} third_party/skia

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/libcutefish-toolkit.so.*
%{_libdir}/libcutefish-toolkit-base.so.*
%{_datadir}/locale/*/LC_MESSAGES/cutefish-toolkit.mo

%files devel
%{_libdir}/libcutefish-toolkit.so
%{_libdir}/libcutefish-toolkit-base.so
%{_includedir}/cutefish-toolkit
%{_libdir}/cmake/CutefishToolkit

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022git9e161d0
- Initial package, pinned to upstream main 9e161d0.
