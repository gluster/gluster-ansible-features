nfs_ganesha
=========

The role nfs_ganesha enables user to perform the following actions:

* Create nfs_ganesha cluster
* Destroy nfs_ganesha cluster
* Add a node to nfs_ganesha cluster
* Delete a node from nfs_ganesha cluster
* Export a nfs_ganesha cluster
* Unexport a nfs_ganesha cluster
* Refresh the configuration

Requirements
------------

GlusterFS 3.2 or above.
NFS Ganesha packages for gluster

Role Variables
--------------

### Creating nfs_ganesha cluster

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_ganesha_haname |  | UNDEF   | Name of the NFS Ganesha cluster.  |
| gluster_features_ganesha_volume |    | UNDEF    | An existing GlusterFS volume which will be exported through NFS Ganesha |
| gluster_features_ganesha_viplist    | UNDEF | public   | A comma separated list of virtual IPs for each of the nodes specified above. |
| gluster_features_ganesha_hostnames  |  | UNDEF | A comma separated list of hostnames, these are subset of nodes of the Gluster Trusted Pool that form the ganesha HA cluster|
| gluster_features_ganesha_masternode |    | UNDEF | One of the nodes from the Trusted Storage Pool, gluster commands will be run on this node. gluster_features_ganesha_masternode: "{{ groups['ganesha_nodes'][0] }}" - the first node of the inventory section ganesha_nodes will be used.|
| gluster_features_ganesha_clusternodes |    | UNDEF | List of the nodes in the Trusted Storage Pool. gluster_features_ganesha_clusternodes: "{{ groups['ganesha_nodes'] }}" - The nodes listed in section ganesha_nodes in the inventory. |
| gluster_features_ganesha_newnodes_vip | | | Dictionary containing the ip/hostname of new node and corresponding VIP. See example below. |
| gluster_features_ganesha_ha_pass | | | Password for ha cluster, this variable has to be encrypted using ansible-vault. |


Dependencies
------------

gluster.infra
gluster.cluster

Example Playbook
----------------

An example playbook to deploy NFS Ganesha.

```yaml
---
- name: Setting NFS Ganesha
  remote_user: root
  hosts: nfs_ganesha
  gather_facts: false
  no_log: True

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

An example playbook to add a new node to NFS Ganesha cluster.

```yaml
---
- name: Setup NFS Ganesha
  hosts: newnodes
  remote_user: root
  gather_facts: false
  no_log: True

  vars:
    gluster_features_ganesha_masternode: '10.70.42.31'
    gluster_features_ganesha_clusternodes: "{{ groups['newnodes'] }}"

    # This has to be hostnames
    gluster_features_ganesha_haname: ganesha-ha
    gluster_features_ganesha_volume: 'ganeshavol'
    gluster_features_ganesha_newnodes_vip:
      - { host: '10.70.43.206', vip: '192.168.1.4' }

  roles:
     - gluster.features

```

License
-------

GPLv3

Author Information
------------------

Author: Sachidananda Urs <surs@redhat.com>
