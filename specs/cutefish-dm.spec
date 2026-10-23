%global repo cutefish-dm
%global commit 73ed274f3ec27af8e4e118f428073769fc4e873a
%global shortcommit 73ed274
%global commitdate 20261022

%global debug_package %{nil}
%global greeteruser cutefish-greeter
%global greeterhome /var/lib/cutefish-greeter

Name:           cutefish-dm
Version:        1.0
Release:        0.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Cutefish display manager

License:        BSD-3-Clause
URL:            https://github.com/cutefishos/%{repo}
Source0:        %{repo}-%{commit}.tar.gz
Patch0:         cutefish-dm-0001-fedora-pam.patch

BuildRequires:  cmake
BuildRequires:  cmake-rpm-macros
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  gettext
BuildRequires:  cutefish-toolkit-devel
BuildRequires:  pam-devel
BuildRequires:  systemd-rpm-macros

Requires:       cutefish-compositor
Requires(pre):  shadow-utils
Recommends:     cutefish-core
# The files below are owned by the greeter user, which %pre creates.
Provides:       user(%{greeteruser})
Provides:       group(%{greeteruser})

%description
The Cutefish display manager. It owns the login screen on VT1, runs the
greeter as the unprivileged cutefish-greeter user, and starts the Wayland
session the user picks on VT2 through PAM.

The PAM stacks are adapted for Fedora: upstream includes the Debian
common-auth/common-session files, which do not exist here.

%prep
%setup -q -n %{repo}-%{commit}
%patch -P 0 -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install
install -d -m 0700 %{buildroot}%{greeterhome}
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/cutefish-dm
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/cutefish-dm/backgrounds

%pre
getent group %{greeteruser} >/dev/null || groupadd -r %{greeteruser}
getent passwd %{greeteruser} >/dev/null || \
    useradd -r -g %{greeteruser} -d %{greeterhome} -s /sbin/nologin \
        -c "Cutefish greeter" %{greeteruser}
exit 0

%post
%systemd_post cutefish-dm.service

%preun
%systemd_preun cutefish-dm.service

%files
%license LICENSE
%doc README.md
%{_bindir}/cutefish-dm
%{_libexecdir}/cutefish-dm-helper
%{_libexecdir}/cutefish-dm-session
%{_unitdir}/cutefish-dm.service
%config(noreplace) %{_sysconfdir}/pam.d/cutefish-dm
%config(noreplace) %{_sysconfdir}/pam.d/cutefish-dm-greeter
%{_datadir}/dbus-1/system.d/org.cutefish.DisplayManager.conf
%{_userunitdir}/filter-chain.service.d/cutefish-dm.conf
%{_userunitdir}/pipewire-pulse.service.d/cutefish-dm.conf
%{_userunitdir}/pipewire-pulse.socket.d/cutefish-dm.conf
%{_userunitdir}/pipewire.service.d/cutefish-dm.conf
%{_userunitdir}/pipewire.socket.d/cutefish-dm.conf
%{_userunitdir}/wireplumber.service.d/cutefish-dm.conf
%dir %attr(0700,%{greeteruser},%{greeteruser}) %{greeterhome}
%dir %{_localstatedir}/lib/cutefish-dm
%dir %{_localstatedir}/lib/cutefish-dm/backgrounds

%changelog
* Fri Oct 23 2026 r00t <r00t@localhost> - 1.0-0.20261022git73ed274
- Initial package, pinned to upstream main 73ed274.
