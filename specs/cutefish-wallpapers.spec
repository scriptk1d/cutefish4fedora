%global repo wallpapers
%global commit 2c6191179b82c49584e738baf92d34a84c6a62d6
%global shortcommit 2c61911
%global commitdate 20261020

%global debug_package %{nil}

Name:           cutefish-wallpapers
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Default wallpapers for the Cutefish desktop

License:        LicenseRef-Unsplash
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros

%description
The default wallpaper set, installed in /usr/share/backgrounds/cutefishos.

%prep
%setup -q -n %{repo}-%{commit}

%build
%cmake -DCMAKE_BUILD_TYPE=Release

%install
%cmake_install

%files
%license LICENSE
%{_datadir}/backgrounds/cutefishos

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261020git2c61911
- Initial package, pinned to upstream main 2c61911.
