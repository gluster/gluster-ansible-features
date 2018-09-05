%global rolesdir %{_sysconfdir}/ansible/roles/gluster.features
%global docdir %{_datadir}/doc/gluster.features

Name:      gluster-ansible-features
Version:   0.2
Release:   1%{?dist}
Summary:   Ansible roles for GlusterFS infrastructure management

URL:       https://github.com/gluster/gluster-ansible-features
Source0:   %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
License:   GPLv3
BuildArch: noarch

Requires:  ansible >= 2.6

%description
Collection of Ansible roles for the deploying and managing GlusterFS clusters.
The features role enables user to configure CTDB, NFS-Ganesha, Geo-Replication,
Gluster HCI on GlusterFS clusters

%prep
%setup -q -n %{name}-%{version}

%build

%install
mkdir -p %{buildroot}/%{rolesdir}
cp -dpr defaults handlers meta roles tasks tests README.md LICENSE vars \
   %{buildroot}/%{rolesdir}

mkdir -p %{buildroot}/%{docdir}
cp -dpr README.md examples %{buildroot}/%{docdir}

%files
%{rolesdir}
%doc %{docdir}

%license LICENSE

%changelog
* Fri Aug 31 2018 Sachidananda Urs <sac@redhat.com> 0.2
- Disabled geo-replication for the initial release

* Tue Apr 24 2018 Sachidananda Urs <sac@redhat.com> 0.1
- Initial release.

