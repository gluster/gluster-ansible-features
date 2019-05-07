gluster_hci
===========

The role gluster_hci deploys and manages the hyperconverged interface by
integrating Red Hat Virtualization and GlusterFS.

Requirements
------------

GlusterFS 3.2 or higher

Role Variables
--------------

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_hci_cluster |  | UNDEF   | The cluster ip/hostnames. Can be set by gluster_hci_cluster: "{{ groups['hc-nodes'] }}",  where hc-nodes is from the inventory file.  |
| gluster_features_hci_volumes  |  | UNDEF | This is a dictionary setting the volume information. See below for further explanation and variables. |
| gluster_features_hci_packages   | | UNDEF | List of packages to be installed. User need not set this, picked up from defaults. |
| gluster_features_hci_volume_options |  | UNDEF | This is not needed to be set by user, defaults are picked up. Set to override defaults. See below for details on default values.|
| gluster_features_hci_master | | UNDEF | The REST host to be connected to (do not include `http'. This value will be ignored if glusterd1 is running on remote node. |
| gluster_features_hci_port || 24007 | The port to be set for the remote  |
| gluster_features_fqdn_check |true/false|true|Check if the hosts have valid FQDN. Set the variable to false to skip the FQDN check.|
| gluster_features_min_disk ||15360|The minimum disk size that /var/log directory must have for the role to proceed. By default the role checks for 15G. Should be in megabytes|
| gluster_features_force_varlogsizecheck |true/false|true|Force the role to enforce the minimum disk size requirement for /var/log. If set to false, disk size check is ignored.|
|gluster_features_512B_check|true/false|true|If set to false, logical block size is not checked. By default checks if logical block size for a disk is set to 512 bytes.|
|gluster_features_slice_setup|true/false|true|If set to false, slice setup will not be done. This features creates a CPU slice limiting the glusterd process's CPU consumption|
|gluster_features_enable_ipv6|true/false|false|If set to true, role will configure glusterd to use ipv6 address|
|gluster_features_enable_ssl|true/false|false|If set to true, role will configure ssl on the provided volumes|
|gluster_features_ssl_clients||None|A comma separated list of ssl clients to be configured. This variable is optional.|
|gluster_features_priv_key||/etc/ssl/glusterfs.key|If set, the value is used to store the generated key.|
|gluster_features_ssl_self_signed|true/false|true|If set to false, a private key has to be provided. And the role will not generate a key.|
|gluster_features_cert_file||/etc/ssl/glusterfs.pem|If the user wishes to use third party certificate, this variable has to be set to point to the certificate. If the variable is not set, then the self-signed certificate /etc/ssl/glusterfs.pem will be used.|
|gluster_features_cert_validity||365|Validity of the certificate in days. Default is 1 year|
|gluster_features_ssl_volumes||gluster_features_hci_volumes|Volumes on which to setup ssl. By default ssl will be created on all the HCI volumes.|


### gluster_features_hci_volume_options
---------------------------------------

This variable defines the options that has to be set upon volume creation. If replica volume is created, the options are set by default by the role. The options set for replica volume are:

```
gluster_features_hci_volume_options:
   { group: 'virt',
     storage.owner-uid: '36',
     storage.owner-gid: '36',
     network.ping-timeout: '30',
     performance.strict-o-direct: 'on',
     network.remote-dio: 'off'
   }
```

If the volume created is a _**single node distribute**_, then the variable _gluster_features_hci_volume_options_ has to be set in the playbook, which overrides the above values. Distribute volume should have the following options:

```
    gluster_features_hci_volume_options:
      { storage.owner-uid: '36',
        storage.owner-gid: '36',
        features.shard: 'on',
        performance.low-prio-threads: '32',
        performance.strict-o-direct: 'on',
        network.remote-dio: 'off',
        network.ping-timeout: '30',
        user.cifs: 'off',
        nfs.disable: 'on',
        performance.quick-read: 'off',
        performance.read-ahead: 'off',
        performance.io-cache: 'off',
        cluster.eager-lock: enable
      }
```

Dependencies
------------

gluster.infra

Example Playbook
----------------

Assuming that backend is already created. Else please see examples for more
detailed playbooks.

```
- name: Setting up GlusterFS HCI
  remote_user: root
  hosts: hc-nodes
  gather_facts: false

  vars:
    gluster_features_hci_cluster: "{{ groups['hc-nodes'] }}"
    gluster_features_hci_volumes:
       - { volname: 'engine', brick: '/gluster_bricks/engine/engine' }
       - { volname: 'data', brick: '/gluster_bricks/data/data' }
       - { volname: 'vmstore', brick: '/gluster_bricks/vmstore/vmstore' }

  roles:
     - gluster.features
```

License
-------

GPLv3
