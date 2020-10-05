geo_replication
===============

The role geo_replication enables user setup/start/stop/configure Geo-Replication sessions.

Requirements
------------

GlusterFS 3.2 or above.
Geo-Replication packages for GlusterFS

Role Variables
--------------

### Setting up CTDB for GlusterFS

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_georep_mastervol |    | UNDEF | Geo-Replication master volume. |
| gluster_features_georep_slavevol |  | UNDEF | Geo-Replication slave volume.  |
| georepuser |  | UNDEF | Geo-Replication user for secure sessions.  |
| georep_masternode | | UNDEF | Master node on which Geo-Replication commands will be run |

Dependencies
------------

gluster.infra
gluster.cluster

Example Playbook
----------------

An example playbook to setup Geo-Replication

```yaml
---
- name: Setup Geo-Replication
  remote_user: root
  hosts: georep_hosts
  gather_facts: false

  vars:
     # Setting up Geo-Replication for GlusterFS cluster
     gluster_features_georep_mastervol: mastervol
     gluster_features_georep_slavevol: slavevol
     georepuser: staff
     georep_masternode: "{{groups['masternodes'][0]}}"

  roles:
     - gluster.features

```

The above playbook assumes that master and slave nodes are up and running.


License
-------

GPLv3

