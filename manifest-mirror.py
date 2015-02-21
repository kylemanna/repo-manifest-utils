#!/usr/bin/env python3
#
# Author: Kyle Manna <kyle [at] kylemana [dot] com >
#

import os
import sys
import glob
import json
import logging
import subprocess
import xml.etree.ElementTree as ET
import http.client

manifest=sys.argv[1]

if len(sys.argv) > 3:
    base=sys.argv[2]
else:
    base=os.path.dirname(manifest)

gh_token=os.environ.get('GITHUB_TOKEN')

logging.basicConfig(level=logging.INFO)


def github_create_repo_cmd(name):
    logging.info('Creating Github Repo {}'.format(name))

    h = http.client.HTTPSConnection('api.github.com', 443)
    header = {'Authorization': 'token {}'.format(gh_token),
              'User-agent': 'repo-mirromatic v0.0.1'}
    body = json.dumps({ 'name':name } )
    h.request("POST", "/orgs/omapzoom/repos", body, header)
    resp = h.getresponse()
    logging.info("Status={}, Reason={}".format(resp.status, resp.reason))
    logging.debug(resp.read())


manifest = ET.parse(manifest)
root = manifest.getroot()

default_mirror = "http://git.omapzoom.org"
new_mirror = "git@github.com:omapzoom"
src_remote = 'omap-mirror'

for element in root.findall('project'):
    remote = (element.get('remote'))
    if remote:
        continue


    name = element.get('name')
    path = element.get('path', name)
    safe_name = name.replace("/", "-")
    dst = '{}/{}'.format(new_mirror, safe_name)
    
    logging.info("Repo {} -> {}".format(name, dst))

    github_create_repo_cmd(safe_name)

    cmd = ['git',
            '--git-dir={}/.git'.format(os.path.join(base, path)),
            'push', '--prune',
            dst,
            '+refs/remotes/{}/*:refs/heads/*'.format(src_remote),
            '+refs/tags/*:refs/tags/*']

    logging.info('Executing {}'.format(cmd))
    ret = subprocess.call(cmd)
    logging.info('Command returned {}'.format(ret))
    if ret != 0:
        sys.exit(1)
