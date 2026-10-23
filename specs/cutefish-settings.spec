%global repo settings
%global commit c0f85ad191468a9dd13fb9afb37a7feebfefddae
%global shortcommit c0f85ad
%global commitdate 20261020

%global debug_package %{nil}

Name:           cutefish-settings
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        System settings for the Cutefish desktop

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext
BuildRequires:  cutefish-toolkit-devel
BuildRequires:  cutefish-framework-devel
BuildRequires:  libxcrypt-devel

BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(icu-i18n)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libspa-0.2)

Requires:       accountsservice
Requires:       polkit

%description
The Cutefish system settings application: appearance, wallpaper, network,
Bluetooth, sound, power, display, accounts, date and time, language, keyboard
and shortcuts.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_bindir}/cutefish-settings
%{_datadir}/cutefish-settings/images
%{_datadir}/applications/cutefish-settings.desktop
%{_datadir}/polkit-1/rules.d/60-cutefish-datetime.rules

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261020gitc0f85ad
- Initial package, pinned to upstream main c0f85ad.
