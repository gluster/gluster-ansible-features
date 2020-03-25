ctdb
=========

The role ctdb enables user setup CTDB for GlusterFS

Requirements
------------

GlusterFS 3.2 or above.
CTDB packages for GlusterFS

Role Variables
--------------

### Setting up CTDB for GlusterFS

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_ctdb_volume |    | UNDEF | GlusterFS volumename to configure with CTDB|
| gluster_features_ctdb_nodes  |  | UNDEF | Comma separated list of IP addresses  |
| gluster_features_ctdb_publicaddr | | UNDEF | Comma separated list of public addresses with interface. For eg: 10.70.37.6/24 eth0,10.70.37.8/24 eth0|
| gluster_features_smb_username | | UNDEF | Samba username |
| gluster_features_smb_password | | UNDEF | Samba password. Note that password variable has to be encrypted using ansible-vault |

Dependencies
------------

gluster.infra
gluster.cluster

Example Playbook
----------------

An example playbook to setup CTDB.

```yaml
---
- name: Setup CTDB for GlusterFS
  remote_user: root
  hosts: ctdb_hosts
  gather_facts: false
  no_log: True

  vars:
     # Setting up CTDB for GlusterFS cluster
     gluster_features_ctdb_volume: gluster-ctdb
     gluster_features_ctdb_nodes: 192.168.1.1,192.168.2.5
     gluster_features_ctdb_publicaddr: '10.70.37.6/24 eth0,10.70.37.8/24 eth0'

  roles:
     - gluster.features

```

The above playbook assumes that a volume named gluster-ctdb is created and running.

Note: Password has to be encrypted using ansible-vault

License
-------

GPLv3

