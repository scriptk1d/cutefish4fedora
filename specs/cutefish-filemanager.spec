%global repo filemanager
%global commit a475b515692e2acbf6cdaf2b4c4c16a593095d06
%global shortcommit a475b51
%global commitdate 20261022

%global debug_package %{nil}

Name:           cutefish-filemanager
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        File manager and desktop for Cutefish

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
BuildRequires:  libzip-devel

BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(fuse3)
BuildRequires:  pkgconfig(libmtp)
BuildRequires:  pkgconfig(smbclient)
BuildRequires:  pkgconfig(libssh)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(icu-i18n)

%description
The Cutefish file manager. It also draws the desktop and its icons, and
mounts phones and network shares through FUSE so their files are local paths
to everything else.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_bindir}/cutefish-filemanager
%{_libexecdir}/cutefish-filemanager-daemon
%{_libexecdir}/cutefish-mountd
%{_datadir}/dbus-1/services/org.cutefish.FileManager1.service
%{_datadir}/dbus-1/services/org.cutefish.FileOperations.service
%{_datadir}/dbus-1/services/org.cutefish.FilePreview.service
%{_datadir}/dbus-1/services/org.cutefish.Mounts1.service
%{_datadir}/polkit-1/rules.d/60-cutefish-filemanager.rules
%{_datadir}/applications/cutefish-filemanager.desktop

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022gita475b51
- Initial package, pinned to upstream main a475b51.
