%global rolesdir %{_sysconfdir}/ansible/roles/gluster.features
%global docdir %{_datadir}/doc/gluster.features
%global buildnum 5

Name:      gluster-ansible-features
Version:   1.0.4
Release:   5%{?dist}
Summary:   Ansible roles for GlusterFS infrastructure management

URL:       https://github.com/gluster/gluster-ansible-features
Source0:   %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}-%{buildnum}.tar.gz
License:   GPLv3
BuildArch: noarch

Requires:  ansible >= 2.6

%description
Collection of Ansible roles for the deploying and managing GlusterFS clusters.
The features role enables user to configure CTDB, NFS-Ganesha, Geo-Replication,
Gluster HCI on GlusterFS clusters

%prep
%autosetup -p1

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
* Mon Mar 4 2019 Sachidananda Urs <sac@redhat.com> 1.0.4-5
- Add slice setup support rhbz#1683528

* Fri Mar 1 2019 Sachidananda Urs <sac@redhat.com> 1.0.4-4
- Validate if the disks have logical sector size of 512B rhbz#1674608

* Wed Feb 20 2019 Sachidananda Urs <sac@redhat.com> 1.0.0-1
- Bumping version number to 1

* Fri Oct 12 2018 Sachidananda Urs <sac@redhat.com> 0.4
- Remove granular-entry-self-heal from the setting vol opts

* Thu Sep 27 2018 Sachidananda Urs <sac@redhat.com> 0.3
- Embed gluster_volume module within role

* Fri Aug 31 2018 Sachidananda Urs <sac@redhat.com> 0.2
- Disabled geo-replication for the initial release

* Tue Apr 24 2018 Sachidananda Urs <sac@redhat.com> 0.1
- Initial release.

