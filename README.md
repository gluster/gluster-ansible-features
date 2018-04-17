gluster.features
=========

The gluster.features role implements GlusterFS usecases. This role implements following sub-roles:

* nfs_ganesha
* gluster_hc
* ctdb
* geo_replication

Requirements
------------

* GlusterFS

Role Variables
--------------

### NFS Ganesha related variables

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_ganesha_haname |  | UNDEF   | Name of the NFS Ganesha cluster.  |
| gluster_features_ganesha_volume |    | UNDEF    | An existing GlusterFS volume which will be exported through NFS Ganesha |
| gluster_features_ganesha_hostnames  |  | UNDEF | A comma separated list of hostnames, these are subset of nodes of the Gluster Trusted Pool that form the ganesha HA cluster|
| gluster_features_ganesha_viplist    | UNDEF | public   | A comma separated list of virtual IPs for each of the nodes specified above. |
| gluster_features_ganesha_masternode |    | UNDEF | One of the nodes from the Trusted Storage Pool, gluster commands will be run on this node. gluster_features_ganesha_masternode: "{{ groups['ganesha_nodes'][0] }}" - the first node of the inventory section ganesha_nodes will be used.|
| gluster_features_ganesha_clusternodes |    | UNDEF | List of the nodes in the Trusted Storage Pool. gluster_features_ganesha_clusternodes: "{{ groups['ganesha_nodes'] }}" - The nodes listed in section ganesha_nodes in the inventory. |

### Gluster Hyperconverged Interface setup related roles

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_hci_cluster |  | UNDEF   | The cluster ip/hostnames. Can be set by gluster_hci_cluster: "{{ groups['hc-nodes'] }}",  where hc-nodes is from the inventory file.  |
| gluster_features_hci_volumes  |  | UNDEF | This is a dictionary setting the volume information. See below for futher explanation and variables. |
| gluster_features_hci_packages   | UNDEF | | List of packages to be installed. User need not set this, picked up from defaults. |
| gluster_features_hci_volume_options |  | UNDEF | This is not needed to be set by user, defauts are picked up. Set to override defaults. For default values see Gluster HCI documentation. |


Dependencies
------------

gluster.infra
gluster.cluster


Example Playbook
----------------

Creating a NFS Ganesha Cluster:

An example playbook to deploy NFS Ganesha.
Note to gather_facts should be set to true.


```yaml
---
- name: Setting NFS Ganesha
  remote_user: root
  hosts: nfs_ganesha
  gather_facts: false

  vars:
     # Setting up NFS Ganesha
     gluster_features_ganesha_haname: ganesha-ha
     gluster_features_ganesha_volume: nfs_ganesha
     gluster_features_ganesha_hostnames: "server1,server2,server3,server4"
     gluster_features_ganesha_viplist: 10.70.44.121,10.70.44.122,10.70.44.123,10.70.44.124

     gluster_features_ganesha_masternode: "{{ groups['ganesha_nodes'][0] }}"
     gluster_features_ganesha_clusternodes: "{{ groups['ganesha_nodes'] }}"

  roles:
     - gluster.features

```

The above playbook assumes that a volume named nfs_ganesha is created and running.


License
-------

GPLv3

Author Information
------------------

Sachidananda Urs <surs@redhat.com>
