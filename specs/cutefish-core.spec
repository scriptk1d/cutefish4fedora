%global repo cutefish-core
%global commit 4e8e6061d86d349fba093b17e27bea6146d805d2
%global shortcommit 4e8e606
%global commitdate 20261022

%global debug_package %{nil}

Name:           cutefish-core
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Session and system services for the Cutefish desktop

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

BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libpipewire-0.3)

Requires:       polkit
Recommends:     cutefish-icons
Recommends:     cutefish-wallpapers

%description
The Cutefish session: compositor and shell startup, application runtime,
locale generation, camera and microphone switches, the polkit agent and the
screen recorder.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_bindir}/cutefish-appruntime
%{_bindir}/cutefish-polkit-agent
%{_bindir}/cutefish-session
%{_bindir}/cutefish-services
%{_bindir}/cutefish-wayland-session
%{_libexecdir}/cutefish-locales
%{_libexecdir}/cutefish-privacy
%{_libexecdir}/cutefish-screenrecorder
%{_datadir}/dbus-1/system.d/org.cutefish.Locales.conf
%{_datadir}/dbus-1/system.d/org.cutefish.Privacy.conf
%{_datadir}/dbus-1/system-services/org.cutefish.Locales.service
%{_datadir}/dbus-1/system-services/org.cutefish.Privacy.service
%{_unitdir}/cutefish-locales.service
%{_unitdir}/cutefish-privacy.service
%{_datadir}/polkit-1/actions/org.cutefish.locales.policy
%{_datadir}/polkit-1/actions/org.cutefish.privacy.policy
%{_udevrulesdir}/60-cutefish-ddc.rules
%{_udevrulesdir}/60-cutefish-privacy.rules
%{_modulesloaddir}/cutefish-ddc.conf
%{_datadir}/wayland-sessions/cutefish-wayland.desktop
%{_datadir}/cutefish-services/gtk/gtk-3.0.css
%{_datadir}/cutefish-services/gtk/gtk-4.0.css
%{_userunitdir}/xdg-document-portal.service.d/cutefish-session.conf

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022git4e8e606
- Initial package, pinned to upstream main 4e8e606.
