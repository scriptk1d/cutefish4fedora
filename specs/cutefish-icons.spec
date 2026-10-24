%global repo icons
%global commit 863d156cbef6be7bc2eb7c4453800df416bd73ea
%global shortcommit 863d156
%global commitdate 20261023

%global debug_package %{nil}

Name:           cutefish-icons
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Default icon theme for the Cutefish desktop

License:        GPL-3.0-only
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  gtk-update-icon-cache

Requires:       hicolor-icon-theme

%description
The Cutefish icon theme, installed as /usr/share/icons/Cutefish.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release

%install
%cmake_install

%files
%license LICENSE
%{_datadir}/icons/Cutefish

%post
[ -x /usr/bin/gtk-update-icon-cache ] && [ -d %{_datadir}/icons/Cutefish ] && \
  gtk-update-icon-cache -q -t -f %{_datadir}/icons/Cutefish || :

%postun
[ -x /usr/bin/gtk-update-icon-cache ] && [ -d %{_datadir}/icons/Cutefish ] && \
  gtk-update-icon-cache -q -t -f %{_datadir}/icons/Cutefish || :

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261020git83a6149
- Initial package, pinned to upstream main 83a6149.
