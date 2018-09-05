#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Taneli Leppä <taneli@crasman.fi>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
module: gluster_volume
short_description: Manage GlusterFS volumes
description:
  - Create, remove, start, stop and tune GlusterFS volumes
version_added: '1.9'
options:
  name:
    description:
      - The volume name.
    required: true
    aliases: ['volume']
  state:
    description:
      - Use present/absent ensure if a volume exists or not.
        Use started/stopped to control its availability.
    required: true
    choices: ['absent', 'present', 'started', 'stopped']
  cluster:
    description:
      - List of hosts to use for probing and brick setup.
  host:
    description:
      - Override local hostname (for peer probing purposes).
  replicas:
    description:
      - Replica count for volume.
  arbiters:
    description:
      - Arbiter count for volume.
    version_added: '2.3'
  stripes:
    description:
      - Stripe count for volume.
  disperses:
    description:
      - Disperse count for volume.
    version_added: '2.2'
  redundancies:
    description:
      - Redundancy count for volume.
    version_added: '2.2'
  transport:
    description:
      - Transport type for volume.
    default: tcp
    choices: [ tcp, rdma, 'tcp,rdma' ]
  bricks:
    description:
      - Brick paths on servers. Multiple brick paths can be separated by commas.
    aliases: [ brick ]
  start_on_create:
    description:
      - Controls whether the volume is started after creation or not.
    type: bool
    default: 'yes'
  rebalance:
    description:
      - Controls whether the cluster is rebalanced after changes.
    type: bool
    default: 'no'
  directory:
    description:
      - Directory for limit-usage.
  options:
    description:
      - A dictionary/hash with options/settings for the volume.
  quota:
    description:
      - Quota value for limit-usage (be sure to use 10.0MB instead of 10MB, see quota list).
  force:
    description:
      - If brick is being created in the root partition, module will fail.
        Set force to true to override this behaviour.
    type: bool
  master:
    description:
      - The node from which to run the volume commands. This is required for the
        API calls in GlusterFS 4.0 and above
    version_added: '2.7'
notes:
  - Requires cli tools for GlusterFS on servers.
  - Will add new bricks, but not remove them.
author:
- Taneli Leppä (@rosmo)
"""

EXAMPLES = """
- name: create gluster volume
  gluster_volume:
    state: present
    name: test1
    bricks: /bricks/brick1/g1
    rebalance: yes
    cluster:
      - 192.0.2.10
      - 192.0.2.11
  run_once: true

- name: tune
  gluster_volume:
    state: present
    name: test1
    options:
      performance.cache-size: 256MB

- name: Set multiple options on GlusterFS volume
  gluster_volume:
    state: present
    name: test1
    options:
      { performance.cache-size: 128MB,
        write-behind: 'off',
        quick-read: 'on'
      }

- name: start gluster volume
  gluster_volume:
    state: started
    name: test1

- name: limit usage
  gluster_volume:
    state: present
    name: test1
    directory: /foo
    quota: 20.0MB

- name: stop gluster volume
  gluster_volume:
    state: stopped
    name: test1

- name: remove gluster volume
  gluster_volume:
    state: absent
    name: test1

- name: create gluster volume with multiple bricks
  gluster_volume:
    state: present
    name: test2
    bricks: /bricks/brick1/g2,/bricks/brick2/g2
    cluster:
      - 192.0.2.10
      - 192.0.2.11
  run_once: true
"""

import re
import socket
import time
import traceback
from distutils.version import LooseVersion

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from glusterapilib import Client
from glusterapilib.exceptions import GlusterApiError

glusterbin = ''


def run_gluster(gargs, **kwargs):
    global glusterbin
    global module
    args = [glusterbin, '--mode=script']
    args.extend(gargs)
    try:
        rc, out, err = module.run_command(args, **kwargs)
        if rc != 0:
            module.fail_json(msg='error running gluster (%s) command (rc=%d): %s' %
                                 (' '.join(args), rc, out or err), exception=traceback.format_exc())
    except Exception as e:
        module.fail_json(msg='error running gluster (%s) command: %s' % (' '.join(args),
                                                                         to_native(e)), exception=traceback.format_exc())
    return out


def run_gluster_nofail(gargs, **kwargs):
    global glusterbin
    global module
    args = [glusterbin]
    args.extend(gargs)
    rc, out, err = module.run_command(args, **kwargs)
    if rc != 0:
        return None
    return out


def get_peers():
    out = run_gluster(['peer', 'status'])
    peers = {}
    hostname = None
    uuid = None
    state = None
    shortNames = False
    for row in out.split('\n'):
        if ': ' in row:
            key, value = row.split(': ')
            if key.lower() == 'hostname':
                hostname = value
                shortNames = False
            if key.lower() == 'uuid':
                uuid = value
            if key.lower() == 'state':
                state = value
                peers[hostname] = [uuid, state]
        elif row.lower() == 'other names:':
            shortNames = True
        elif row != '' and shortNames is True:
            peers[row] = [uuid, state]
        elif row == '':
            shortNames = False
    return peers


def get_volumes():
    out = run_gluster(['volume', 'info'])

    volumes = {}
    volume = {}
    for row in out.split('\n'):
        if ': ' in row:
            key, value = row.split(': ')
            if key.lower() == 'volume name':
                volume['name'] = value
                volume['options'] = {}
                volume['quota'] = False
            if key.lower() == 'volume id':
                volume['id'] = value
            if key.lower() == 'status':
                volume['status'] = value
            if key.lower() == 'transport-type':
                volume['transport'] = value
            if value.lower().endswith(' (arbiter)'):
                if 'arbiters' not in volume:
                    volume['arbiters'] = []
                value = value[:-10]
                volume['arbiters'].append(value)
            if key.lower() != 'bricks' and key.lower()[:5] == 'brick':
                if 'bricks' not in volume:
                    volume['bricks'] = []
                volume['bricks'].append(value)
            # Volume options
            if '.' in key:
                if 'options' not in volume:
                    volume['options'] = {}
                volume['options'][key] = value
                if key == 'features.quota' and value == 'on':
                    volume['quota'] = True
        else:
            if row.lower() != 'bricks:' and row.lower() != 'options reconfigured:':
                if len(volume) > 0:
                    volumes[volume['name']] = volume
                volume = {}
    return volumes


def get_quotas(name, nofail):
    quotas = {}
    if nofail:
        out = run_gluster_nofail(['volume', 'quota', name, 'list'])
        if not out:
            return quotas
    else:
        out = run_gluster(['volume', 'quota', name, 'list'])
    for row in out.split('\n'):
        if row[:1] == '/':
            q = re.split(r'\s+', row)
            quotas[q[0]] = q[1]
    return quotas


def wait_for_peer(host):
    for x in range(0, 4):
        peers = get_peers()
        if host in peers and peers[host][1].lower().find('peer in cluster') != -1:
            return True
        time.sleep(1)
    return False


def probe(host, myhostname):
    global module
    out = run_gluster(['peer', 'probe', host])
    if out.find('localhost') == -1 and not wait_for_peer(host):
        module.fail_json(msg='failed to probe peer %s on %s' % (host, myhostname))


def probe_all_peers(hosts, peers, myhostname):
    for host in hosts:
        host = host.strip()  # Clean up any extra space for exact comparison
        if host not in peers:
            probe(host, myhostname)


def create_volume(name, stripe, replica, arbiter, disperse, redundancy, transport, hosts, bricks, force):
    args = ['volume', 'create']
    args.append(name)
    if stripe:
        args.append('stripe')
        args.append(str(stripe))
    if replica:
        args.append('replica')
        args.append(str(replica))
    if arbiter:
        args.append('arbiter')
        args.append(str(arbiter))
    if disperse:
        args.append('disperse')
        args.append(str(disperse))
    if redundancy:
        args.append('redundancy')
        args.append(str(redundancy))
    args.append('transport')
    args.append(transport)
    for brick in bricks:
        for host in hosts:
            args.append(('%s:%s' % (host, brick)))
    if force:
        args.append('force')
    run_gluster(args)


def start_volume(name):
    run_gluster(['volume', 'start', name])


def stop_volume(name):
    run_gluster(['volume', 'stop', name])


def set_volume_option(name, option, parameter):
    run_gluster(['volume', 'set', name, option, parameter])


def add_bricks(name, new_bricks, stripe, replica, force):
    args = ['volume', 'add-brick', name]
    if stripe:
        args.append('stripe')
        args.append(str(stripe))
    if replica:
        args.append('replica')
        args.append(str(replica))
    args.extend(new_bricks)
    if force:
        args.append('force')
    run_gluster(args)


def do_rebalance(name):
    run_gluster(['volume', 'rebalance', name, 'start'])


def enable_quota(name):
    run_gluster(['volume', 'quota', name, 'enable'])


def set_quota(name, directory, value):
    run_gluster(['volume', 'quota', name, 'limit-usage', directory, value])


def check_gluster_version(module):
    cmd = module.get_bin_path('gluster', True) + ' --version'
    lang = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')
    rc, output, err = module.run_command(cmd, environ_update=lang)
    if rc > 0:
        module.fail_json(msg="GlusterFS is not installed, GlusterFS" +
                         "version > 3.2 is required.")
    ver_line = output.split('\n')[0]
    version = ver_line.split(' ')[1]
    return version


class GlusterVolume(object):
    def __init__(self, module):
        # Init the parameters
        self.state = module.params['state']
        self.volume_name = module.params['name']
        self.cluster = module.params['cluster']
        self.brick_paths = module.params['bricks']
        self.stripes = module.params['stripes']
        self.replicas = module.params['replicas']
        self.arbiters = module.params['arbiters']
        self.disperses = module.params['disperses']
        self.redundancies = module.params['redundancies']
        self.transport = module.params['transport']
        self.myhostname = module.params['host']
        self.start_on_create = module.boolean(module.params['start_on_create'])
        self.rebalance = module.boolean(module.params['rebalance'])
        self.force = module.boolean(module.params['force'])
        self.module = module
        # GlusterD2.0 specific options
        self.user = self.module.params['user']
        self.passwd = self.module.params['passwd']
        self.verify = self.module.params['verify']
        self.port = self.module.params['port']
        self.master = self.module.params['master']

    def _get_peers(self):
        peer_info = dict()

        try:
            status, peer_list = self.client.peer_status()
        except GlusterApiError as e:
            self.module.fail_json(msg="Unable to get peer list: %s" %
                                  e.message.reason)
        if status == 200:       # Success
            for peer in peer_list:
                hostname = peer['name']
                peer_ipaddr = peer['peer-addresses'][0].split(':')[0]
                peer_id = peer['id']
                peer_info[hostname] = peer_id
                peer_info[peer_ipaddr] = peer_id
        else:
            self.module.fail_json(msg="Failed to get peers")
        return peer_info

    def _get_volinfo(self):
        vol_info = dict()

        try:
            pass
        except GlusterApiError as e:
            pass
        return vol_info

    def _add_peers(self, peers, peer_info):
        for peer in peers:
            try:
                ret, result = self.client.peer_add(peer)
                if result:
                    peer_info[peer] = result['id']
                    peer_info[result['name']] = result['id']
            except GlusterApiError as e:
                reason = e.message.reason
                if reason.lower() == "internal server error":
                    self.module.fail_json(msg="Failed: %s" % reason)
        return peer_info

    def create_volume(self):
        changed = False
        # Create a GlusterD2 volume
        brickinfo = list()
        bricks = self.brick_paths.split(",")
        # Check if peers are probed, else probe and create volume
        peer_info = self._get_peers()
        peers_to_probe = [peer for peer in self.cluster if
                          peer not in peer_info.keys()]
        if peers_to_probe:
            peer_info = self._add_peers(peers_to_probe, peer_info)
        # Create brick path for volume creation. GlusterD2 needs volume-id for
        # brick creation
        for node in self.cluster:
            uuid = peer_info[node]
            for brick in bricks:
                brickinfo.append("%s:%s" % (uuid, brick))

        # Do not create a volume if it is already present, when the support in
        # python API is available get the list of volumes and compare
        try:
            code, out = self.client.volume_create(self.volume_name,
                                                  bricks=brickinfo,
                                                  replica=self.replicas,
                                                  disperse=self.disperses,
                                                  arbiter=self.arbiters,
                                                  disperse_redundancy=self.redundancies,
                                                  force=self.force)
            if code == 201:
                changed = True
        except GlusterApiError as e:
            reason = e.message.reason
            # Once the error codes are refined, fail only on fatal errors
            # For now, we ignore the errors

        # Start the volume if start_on_create is set
        if self.start_on_create:
            try:
                code, out = self.client.volume_start(self.volume_name,
                                                     self.force)
                if out['state'].lower() != "started":
                    self.module.fail_json(msg="Unable to start the volume")
            except GlusterApiError as e:
                pass
        return changed

    def stop_volume(self):
        changed = False
        # TODO: get the volume info and check the state
        try:
            retcode, out = self.client.volume_stop(self.volume_name)
            if out['state'].lower() == "stopped":
                changed = True
            else:
                # Fixme: Give a proper error code
                self.module.fail_json("Unable to stop the volume")
        except GlusterApiError as e:
            # When the error codes are implemented, print proper message
            pass        # Fix API! Do not raise an exception if unable to stop
            # self.module.fail_json(msg="Unable to stop the volume")
        return changed

    def delete_volume(self):
        changed = False
        # Try to stop the volume if it is already started
        changed = self.stop_volume()

        # Delete the volume
        try:
            retcode, out = self.client.volume_delete(self.volume_name)
            if retcode == 204:         # volume deleted successfully
                changed = True
        except GlusterApiError as e:
            self.module.fail_json(msg="Unable to delete the volume")
        return changed

    def start_volume(self):
        # TODO: Handle cases when state=changed and other variables are set.
        try:
            code, out = self.client.volume_start(self.volume_name,
                                                 self.force)
            if out['state'].lower() != "started":
                self.module.fail_json(msg="Unable to start the volume")
                changed = True
        except GlusterApiError as e:
            self.module.fail_json(msg="Unable to start the volume")

    def manage_vol(self):
        changed = False
        if self.master is None:
            self.module.fail_json(msg="master variable has to be set to use" +
                                  "gluster_volume with GlusterFS-4.0 or above")
        master = "http://" + self.master + ":%s" % self.port
        self.client = Client(master, self.user, self.passwd, self.verify)
        if self.state == "present":
            changed = self.create_volume()
        elif self.state == "absent":
            changed = self.delete_volume()
        elif self.state == "started":
            changed = self.start_volume()
        elif self.state == "stopped":
            changed = self.stop_volume()
        self.module.exit_json(changed=changed)


def main():
    # MAIN

    global module
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, aliases=['volume']),
            state=dict(type='str', required=True, choices=['absent', 'started', 'stopped', 'present']),
            cluster=dict(type='list'),
            host=dict(type='str'),
            stripes=dict(type='int'),
            replicas=dict(type='int'),
            arbiters=dict(type='int'),
            disperses=dict(type='int'),
            redundancies=dict(type='int'),
            transport=dict(type='str', default='tcp', choices=['tcp', 'rdma', 'tcp,rdma']),
            bricks=dict(type='str', aliases=['brick']),
            start_on_create=dict(type='bool', default=True),
            rebalance=dict(type='bool', default=False),
            options=dict(type='dict', default={}),
            quota=dict(type='str'),
            directory=dict(type='str'),
            force=dict(type='bool', default=False),
            master=dict(type='str', required=False),
            user=dict(type='str', required=False),
            passwd=dict(type='str', required=False, no_log=True),
            verify=dict(type='str', required=False, default=False),
            port=dict(type='str', required=False, default='24007'),
        ),
    )

    # If gluster version is greater than 4.0, call gluster API
    version = check_gluster_version(module)
    if LooseVersion(version) > LooseVersion("4"):
        gluster_vol = GlusterVolume(module)
        gluster_vol.manage_vol()

    global glusterbin
    glusterbin = module.get_bin_path('gluster', True)

    changed = False

    action = module.params['state']
    volume_name = module.params['name']
    cluster = module.params['cluster']
    brick_paths = module.params['bricks']
    stripes = module.params['stripes']
    replicas = module.params['replicas']
    arbiters = module.params['arbiters']
    disperses = module.params['disperses']
    redundancies = module.params['redundancies']
    transport = module.params['transport']
    myhostname = module.params['host']
    start_on_create = module.boolean(module.params['start_on_create'])
    rebalance = module.boolean(module.params['rebalance'])
    force = module.boolean(module.params['force'])

    if not myhostname:
        myhostname = socket.gethostname()

    # Clean up if last element is empty. Consider that yml can look like this:
    #   cluster="{% for host in groups['glusterfs'] %}{{ hostvars[host]['private_ip'] }},{% endfor %}"
    if cluster is not None and len(cluster) > 1 and cluster[-1] == '':
        cluster = cluster[0:-1]

    if cluster is None:
        cluster = []

    if brick_paths is not None and "," in brick_paths:
        brick_paths = brick_paths.split(",")
    else:
        brick_paths = [brick_paths]

    options = module.params['options']
    quota = module.params['quota']
    directory = module.params['directory']

    # get current state info
    peers = get_peers()
    volumes = get_volumes()
    quotas = {}
    if volume_name in volumes and volumes[volume_name]['quota'] and volumes[volume_name]['status'].lower() == 'started':
        quotas = get_quotas(volume_name, True)

    # do the work!
    if action == 'absent':
        if volume_name in volumes:
            if volumes[volume_name]['status'].lower() != 'stopped':
                stop_volume(volume_name)
            run_gluster(['volume', 'delete', volume_name])
            changed = True

    if action == 'present':
        probe_all_peers(cluster, peers, myhostname)

        # create if it doesn't exist
        if volume_name not in volumes:
            create_volume(volume_name, stripes, replicas, arbiters, disperses, redundancies, transport, cluster, brick_paths, force)
            volumes = get_volumes()
            changed = True

        if volume_name in volumes:
            if volumes[volume_name]['status'].lower() != 'started' and start_on_create:
                start_volume(volume_name)
                changed = True

            # switch bricks
            new_bricks = []
            removed_bricks = []
            all_bricks = []
            for node in cluster:
                for brick_path in brick_paths:
                    brick = '%s:%s' % (node, brick_path)
                    all_bricks.append(brick)
                    if brick not in volumes[volume_name]['bricks']:
                        new_bricks.append(brick)

            # this module does not yet remove bricks, but we check those anyways
            for brick in volumes[volume_name]['bricks']:
                if brick not in all_bricks:
                    removed_bricks.append(brick)

            if new_bricks:
                add_bricks(volume_name, new_bricks, stripes, replicas, force)
                changed = True

            # handle quotas
            if quota:
                if not volumes[volume_name]['quota']:
                    enable_quota(volume_name)
                quotas = get_quotas(volume_name, False)
                if directory not in quotas or quotas[directory] != quota:
                    set_quota(volume_name, directory, quota)
                    changed = True

            # set options
            for option in options.keys():
                if option not in volumes[volume_name]['options'] or volumes[volume_name]['options'][option] != options[option]:
                    set_volume_option(volume_name, option, options[option])
                    changed = True

        else:
            module.fail_json(msg='failed to create volume %s' % volume_name)

    if action != 'delete' and volume_name not in volumes:
        module.fail_json(msg='volume not found %s' % volume_name)

    if action == 'started':
        if volumes[volume_name]['status'].lower() != 'started':
            start_volume(volume_name)
            changed = True

    if action == 'stopped':
        if volumes[volume_name]['status'].lower() != 'stopped':
            stop_volume(volume_name)
            changed = True

    if changed:
        volumes = get_volumes()
        if rebalance:
            do_rebalance(volume_name)

    facts = {}
    facts['glusterfs'] = {'peers': peers, 'volumes': volumes, 'quotas': quotas}

    module.exit_json(changed=changed, ansible_facts=facts)


if __name__ == '__main__':
    main()
