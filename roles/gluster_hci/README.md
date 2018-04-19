gluster_hci
===========

The role gluster_hci deploys and manages the hyperconverged interface by
integrating Red Hat Virtualizition and GlusterFS.

Requirements
------------

GlusterFS 3.2 or higher

Role Variables
--------------

| Name                     |Choices| Default value         | Comments                          |
|--------------------------|-------|-----------------------|-----------------------------------|
| gluster_features_hci_cluster |  | UNDEF   | The cluster ip/hostnames. Can be set by gluster_hci_cluster: "{{ groups['hc-nodes'] }}",  where hc-nodes is from the inventory file.  |
| gluster_features_hci_volumes  |  | UNDEF | This is a dictionary setting the volume information. See below for futher explanation and variables. |
| gluster_features_hci_packages   | | UNDEF | List of packages to be installed. User need not set this, picked up from defaults. |
| gluster_features_hci_volume_options |  | UNDEF | This is not needed to be set by user, defauts are picked up. Set to override defaults. For default values see Gluster HCI documentation. |

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
  hosts: gluster_hci
  gather_facts: true

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
